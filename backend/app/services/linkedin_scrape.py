"""Synchronous LinkedIn post scrape.

Playwright's sync API must run on a process main thread. On Windows it
deadlocks if started from asyncio.to_thread / a worker thread. We therefore
run the scrape in a spawned child process.
"""
from __future__ import annotations

import sys
import traceback
from multiprocessing import get_context
from pathlib import Path
from typing import Any
from urllib.parse import quote

# Project root (ApplyIQ/) so core/ and utils/ import
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def _scrape_worker(query: str, profile_dir: str, scroll_rounds: int, conn) -> None:
    result: dict[str, Any] = {"ok": False, "error": "unknown", "posts": []}
    try:
        result = _scrape_role_posts_sync(query, profile_dir, scroll_rounds)
    except Exception:
        result = {"ok": False, "error": traceback.format_exc()[-500:], "posts": []}
    try:
        conn.send(result)
    finally:
        conn.close()


def _scrape_role_posts_sync(
    query: str,
    profile_dir: str,
    scroll_rounds: int = 8,
) -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    from utils.helpers import clean, extract_emails
    from core.filters import filter_recruiter_emails, should_send_to_post

    profile_path = Path(profile_dir)
    profile_path.mkdir(parents=True, exist_ok=True)

    posts: list[dict[str, Any]] = []
    seen: set[str] = set()

    print(f"[scrape] launching Chromium  query={query!r}  profile={profile_path}", flush=True)

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch_persistent_context(
                user_data_dir=str(profile_path),
                headless=False,
                viewport={"width": 1400, "height": 900},
            )
        except Exception as exc:
            msg = str(exc)
            if "Executable doesn't exist" in msg or "playwright install" in msg.lower():
                return {
                    "ok": False,
                    "error": "Playwright Chromium is not installed. Run: python -m playwright install chromium",
                    "posts": [],
                }
            raise

        page = browser.pages[0] if browser.pages else browser.new_page()
        search_url = (
            "https://www.linkedin.com/search/results/content/"
            f"?keywords={quote(query)}&sortBy=date_posted"
        )
        print(f"[scrape] goto {search_url}", flush=True)
        try:
            page.goto(search_url, timeout=45000)
        except Exception as exc:
            print(f"[scrape] goto warning: {exc}", flush=True)
        page.wait_for_timeout(4000)

        for _ in range(max(1, int(scroll_rounds or 8))):
            page.mouse.wheel(0, 1800)
            page.wait_for_timeout(900)

        try:
            more_buttons = page.get_by_text("more", exact=False)
            for i in range(min(more_buttons.count(), 20)):
                try:
                    more_buttons.nth(i).click(timeout=800)
                    page.wait_for_timeout(200)
                except Exception:
                    pass
        except Exception:
            pass

        cards = page.locator("div.feed-shared-update-v2").all()
        if not cards:
            cards = page.locator("div[data-urn]").all()
        print(f"[scrape] cards={len(cards)}", flush=True)

        for card in cards:
            try:
                text = clean(card.inner_text(timeout=2000))
                if len(text) < 40:
                    continue
                emails = filter_recruiter_emails(extract_emails(text))
                if not emails:
                    continue
                allowed, reason = should_send_to_post(text)
                key = text[:700]
                if key in seen:
                    continue
                seen.add(key)
                posts.append({
                    "text": text[:5000],
                    "emails": emails[:5],
                    "allowed": allowed,
                    "skipReason": reason,
                })
            except Exception:
                continue

        browser.close()

    print(f"[scrape] done posts={len(posts)}", flush=True)
    return {"ok": True, "error": "", "posts": posts}


def scrape_role_posts(
    query: str,
    profile_dir: str,
    scroll_rounds: int = 8,
    timeout_s: int = 180,
) -> dict[str, Any]:
    """Run the scrape in a spawned process (Windows-safe)."""
    ctx = get_context("spawn")
    parent, child = ctx.Pipe(duplex=False)
    proc = ctx.Process(
        target=_scrape_worker,
        args=(query, profile_dir, scroll_rounds, child),
        daemon=True,
    )
    proc.start()
    child.close()
    proc.join(timeout_s)
    if proc.is_alive():
        proc.terminate()
        proc.join(5)
        return {
            "ok": False,
            "error": f"LinkedIn scrape timed out after {timeout_s}s (browser hung or login required).",
            "posts": [],
        }
    if parent.poll():
        return parent.recv()
    code = proc.exitcode
    return {
        "ok": False,
        "error": f"Scrape process exited with code {code} and no result. Install Chromium: python -m playwright install chromium",
        "posts": [],
    }
