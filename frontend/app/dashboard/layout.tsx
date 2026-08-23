'use client';
import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/lib/store';
import {
  LayoutDashboard, User, FileText, Search, Briefcase, BarChart3,
  Settings, Bell, Zap, LogOut, Moon, Sun, Menu, X, ChevronRight,
} from 'lucide-react';
import { useTheme } from 'next-themes';

const NAV = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/searches', icon: Search, label: 'Job Searches' },
  { href: '/applications', icon: Briefcase, label: 'Applications' },
  { href: '/jobs', icon: FileText, label: 'Jobs' },
  { href: '/resumes', icon: FileText, label: 'Resumes' },
  { href: '/profile', icon: User, label: 'Profile' },
  { href: '/analytics', icon: BarChart3, label: 'Analytics' },
  { href: '/automation', icon: Zap, label: 'Automation' },
  { href: '/settings', icon: Settings, label: 'Settings' },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notifCount, setNotifCount] = useState(0);

  useEffect(() => {
    if (!loading && !user) router.push('/login');
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="skeleton w-10 h-10 rounded-full animate-pulse-soft" />
      </div>
    );
  }
  if (!user) return null;

  const handleLogout = () => { logout(); router.push('/'); };

  return (
    <div className="min-h-screen flex">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`fixed lg:static inset-y-0 left-0 z-50 w-64 flex flex-col border-r transition-transform duration-300 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}
             style={{ background: 'var(--card)', borderColor: 'var(--border)' }}>
        {/* Logo */}
        <div className="h-16 flex items-center gap-2 px-6 border-b" style={{ borderColor: 'var(--border)' }}>
          <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <span className="text-lg font-bold">ApplyIQ</span>
          <button className="ml-auto lg:hidden" onClick={() => setSidebarOpen(false)}>
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {NAV.map(item => {
            const active = pathname === item.href || pathname.startsWith(item.href + '/');
            return (
              <button key={item.href} onClick={() => { router.push(item.href); setSidebarOpen(false); }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${active ? 'text-white' : ''}`}
                style={active ? { background: 'var(--primary)' } : { color: 'var(--muted-foreground)' }}>
                <item.icon className="w-4 h-4" />
                {item.label}
                {active && <ChevronRight className="w-4 h-4 ml-auto" />}
              </button>
            );
          })}
        </nav>

        {/* Bottom */}
        <div className="p-4 border-t space-y-2" style={{ borderColor: 'var(--border)' }}>
          <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm"
                  style={{ color: 'var(--muted-foreground)' }}>
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
          </button>
          <button onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm"
                  style={{ color: 'var(--danger)' }}>
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="h-16 flex items-center justify-between px-6 border-b sticky top-0 z-30 glass">
          <button className="lg:hidden" onClick={() => setSidebarOpen(true)}>
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium hidden sm:block">{user.name}</span>
            <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'var(--muted)', color: 'var(--muted-foreground)' }}>
              {user.email}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button className="relative p-2 rounded-lg" style={{ color: 'var(--muted-foreground)' }}>
              <Bell className="w-5 h-5" />
              {notifCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 text-[10px] font-bold rounded-full flex items-center justify-center text-white"
                      style={{ background: 'var(--danger)' }}>{notifCount}</span>
              )}
            </button>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 p-6 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
