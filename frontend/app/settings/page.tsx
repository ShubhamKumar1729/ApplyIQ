'use client';
import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { useTheme } from 'next-themes';
import { Save, Loader2, Moon, Sun, Monitor, Shield, Bell, Zap, Palette, User } from 'lucide-react';

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [tab, setTab] = useState('appearance');

  useEffect(() => {
    api.getSettings().then(res => setSettings(res.data)).finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.updateSettings(settings);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {} finally { setSaving(false); }
  };

  const update = (key: string, val: any) => setSettings((p: any) => ({ ...p, [key]: val }));

  if (loading) return <div className="space-y-4"><div className="skeleton h-64 w-full rounded-xl" /></div>;

  const tabs = [
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'automation', label: 'Automation', icon: Zap },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'privacy', label: 'Privacy', icon: Shield },
  ];

  return (
    <div className="max-w-3xl space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Settings</h1>
          <p style={{ color: 'var(--muted-foreground)' }}>Manage your preferences</p>
        </div>
        <button onClick={handleSave} disabled={saving} className="btn btn-primary">
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : saved ? '✓ Saved' : <><Save className="w-4 h-4" /> Save</>}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 overflow-x-auto">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition ${tab === t.id ? 'text-white' : ''}`}
                  style={tab === t.id ? { background: 'var(--primary)' } : { background: 'var(--muted)', color: 'var(--muted-foreground)' }}>
            <t.icon className="w-4 h-4" /> {t.label}
          </button>
        ))}
      </div>

      {/* Appearance */}
      {tab === 'appearance' && (
        <div className="card space-y-6">
          <h3 className="font-semibold">Theme</h3>
          <div className="grid grid-cols-3 gap-3">
            {[
              { value: 'light', label: 'Light', icon: Sun },
              { value: 'dark', label: 'Dark', icon: Moon },
              { value: 'system', label: 'System', icon: Monitor },
            ].map(t => (
              <button key={t.value} onClick={() => { setTheme(t.value); update('theme', t.value); }}
                      className="p-4 rounded-xl text-center border-2 transition"
                      style={{ borderColor: theme === t.value ? 'var(--primary)' : 'var(--border)' }}>
                <t.icon className="w-6 h-6 mx-auto mb-2" />
                <div className="text-sm font-medium">{t.label}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Automation */}
      {tab === 'automation' && (
        <div className="card space-y-6">
          <h3 className="font-semibold">Automation Defaults</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Default Application Mode</label>
              <select className="input" value={settings?.defaultApplicationMode || 'AUTO_APPLY'}
                      onChange={e => update('defaultApplicationMode', e.target.value)}>
                <option value="AUTO_APPLY">Auto Apply</option>
                <option value="REVIEW">Review Before Sending</option>
                <option value="TEST">Test Mode</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Default AI Threshold: {settings?.defaultAiThreshold || 70}%</label>
              <input type="range" min="0" max="100" value={settings?.defaultAiThreshold || 70}
                     onChange={e => update('defaultAiThreshold', parseInt(e.target.value))}
                     className="w-full" style={{ accentColor: 'var(--primary)' }} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Default Max Applications</label>
              <input type="number" className="input" value={settings?.defaultMaxApplications || 50}
                     onChange={e => update('defaultMaxApplications', parseInt(e.target.value) || 50)} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Sending Pacing (ms)</label>
              <input type="number" className="input" value={settings?.sendingPacingMs || 4000}
                     onChange={e => update('sendingPacingMs', parseInt(e.target.value) || 4000)} />
              <p className="text-xs mt-1" style={{ color: 'var(--muted-foreground)' }}>Delay between sending emails. Minimum 500ms.</p>
            </div>
            <div className="flex items-center justify-between p-4 rounded-xl" style={{ background: 'var(--muted)' }}>
              <div>
                <div className="font-medium text-sm">Customize Resume by Default</div>
                <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>AI tailors resume for each job</div>
              </div>
              <button onClick={() => update('defaultCustomizeResume', !settings?.defaultCustomizeResume)}
                      className="w-12 h-6 rounded-full transition relative"
                      style={{ background: settings?.defaultCustomizeResume ? 'var(--primary)' : 'var(--border)' }}>
                <div className="w-5 h-5 rounded-full bg-white absolute top-0.5 transition-all shadow"
                     style={{ left: settings?.defaultCustomizeResume ? '26px' : '2px' }} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Notifications */}
      {tab === 'notifications' && (
        <div className="card space-y-4">
          <h3 className="font-semibold">Notification Preferences</h3>
          <p className="text-sm" style={{ color: 'var(--muted-foreground)' }}>
            You will receive in-app notifications for:
          </p>
          <ul className="space-y-2 text-sm">
            {['Automation started/completed/stopped', 'Application sent', 'Application failed',
              'Limit reached', 'Resume processed', 'Review needed'].map(n => (
              <li key={n} className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full" style={{ background: 'var(--success)' }} />
                {n}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Privacy */}
      {tab === 'privacy' && (
        <div className="card space-y-4">
          <h3 className="font-semibold">Privacy & Data</h3>
          <div>
            <label className="block text-sm font-medium mb-1.5">Data Retention (days)</label>
            <input type="number" className="input" value={settings?.dataRetentionDays || 90}
                   onChange={e => update('dataRetentionDays', parseInt(e.target.value) || 90)} />
            <p className="text-xs mt-1" style={{ color: 'var(--muted-foreground)' }}>Old logs and generated data will be cleaned up after this period.</p>
          </div>
          <div className="p-4 rounded-xl border" style={{ borderColor: 'var(--border)' }}>
            <h4 className="font-medium text-sm mb-2">Your Data</h4>
            <p className="text-xs mb-3" style={{ color: 'var(--muted-foreground)' }}>
              All your data is stored securely. You can export or delete your account at any time.
            </p>
            <div className="flex gap-2">
              <button className="btn btn-secondary text-sm">Export Data</button>
              <button className="btn btn-danger text-sm">Delete Account</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
