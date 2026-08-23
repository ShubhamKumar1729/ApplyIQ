"""Synchronous LinkedIn post scrape.

Playwright must run off the uvicorn event loop on Windows: the default
SelectorEventLoop cannot spawn subprocesses (NotImplementedError).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import quote


def scrape_role_posts(
    query: str,
    profile_dir: str,
    scroll_rounds: int = 8,
) -> dict[str, Any]:
    """
    Open LinkedIn search, scroll, return posts that contain emails.

    Returns:
        {"ok": bool, "error": str, "posts": [{"text": str, "emails": [str]}]}
    """
    from playwright.sync_api import sync_playwright

    from utils.helpers import clean, extract_emails
    from core.filters import filter_recruiter_emails, should_send_to_post

    profile_path = Path(profile_dir)
    profile_path.mkdir(parents=True, exist_ok=True)

    posts: list[dict[str, Any]] = []
    seen: set[str] = set()

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch_persistent_context(
                user_data_dir=str(profile_path),
                headless=False,
                viewport={"width": 1400, "height": 900},
            )
            page = browser.pages[0] if browser.pages else browser.new_page()

            search_url = (
                "https://www.linkedin.com/search/results/content/"
                f"?keywords={quote(query)}&sortBy=date_posted"
            )
            page.goto(search_url, timeout=30000)
            page.wait_for_timeout(4000)

            for _ in range(max(1, scroll_rounds)):
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
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:500], "posts": posts}

    return {"ok": True, "error": "", "posts": posts}
