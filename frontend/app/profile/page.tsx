'use client';
import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Save, Loader2, CheckCircle2 } from 'lucide-react';

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>(null);
  const [form, setForm] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.getProfile().then(res => {
      setProfile(res.data);
      setForm(res.data);
    }).finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await api.updateProfile(form);
      setProfile(res.data);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {} finally { setSaving(false); }
  };

  const set = (key: string, val: any) => setForm((p: any) => ({ ...p, [key]: val }));

  if (loading) return <div className="space-y-4">{[1,2,3].map(i => <div key={i} className="card"><div className="skeleton h-6 w-48 mb-3" /><div className="skeleton h-10 w-full" /></div>)}</div>;

  return (
    <div className="max-w-3xl space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Profile</h1>
          <p style={{ color: 'var(--muted-foreground)' }}>Manage your professional information</p>
        </div>
        <button onClick={handleSave} disabled={saving} className="btn btn-primary">
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : saved ? <CheckCircle2 className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          {saving ? 'Saving…' : saved ? 'Saved!' : 'Save'}
        </button>
      </div>

      {/* Essential */}
      <div className="card space-y-4">
        <h3 className="font-semibold text-lg">Essential Info</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Full Name</label>
            <input className="input" value={form.fullName || ''} onChange={e => set('fullName', e.target.value)} placeholder="John Doe" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Email</label>
            <input className="input" value={form.email || ''} disabled style={{ opacity: 0.6 }} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Phone</label>
            <input className="input" value={form.phone || ''} onChange={e => set('phone', e.target.value)} placeholder="+1 555-000-0000" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Headline</label>
            <input className="input" value={form.headline || ''} onChange={e => set('headline', e.target.value)} placeholder="Software Engineer" />
          </div>
        </div>
      </div>

      {/* Professional */}
      <div className="card space-y-4">
        <h3 className="font-semibold text-lg">Professional Details</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Location <span className="text-xs" style={{ color: 'var(--muted-foreground)' }}>(optional)</span></label>
            <input className="input" value={form.location || ''} onChange={e => set('location', e.target.value)} placeholder="San Francisco, CA" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Work Authorization</label>
            <input className="input" value={form.workAuthorization || ''} onChange={e => set('workAuthorization', e.target.value)} placeholder="US Citizen / OPT / H1B" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Experience</label>
            <input className="input" value={form.experience || ''} onChange={e => set('experience', e.target.value)} placeholder="3+ Years" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Availability</label>
            <input className="input" value={form.availability || ''} onChange={e => set('availability', e.target.value)} placeholder="Immediate" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Relocation</label>
            <input className="input" value={form.relocation || ''} onChange={e => set('relocation', e.target.value)} placeholder="Yes / No" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Rate</label>
            <input className="input" value={form.rate || ''} onChange={e => set('rate', e.target.value)} placeholder="Open (C2C)" />
          </div>
        </div>
      </div>

      {/* Links */}
      <div className="card space-y-4">
        <h3 className="font-semibold text-lg">Links</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">LinkedIn</label>
            <input className="input" value={form.linkedin || ''} onChange={e => set('linkedin', e.target.value)} placeholder="https://linkedin.com/in/..." />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">GitHub</label>
            <input className="input" value={form.github || ''} onChange={e => set('github', e.target.value)} placeholder="https://github.com/..." />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Portfolio</label>
            <input className="input" value={form.portfolio || ''} onChange={e => set('portfolio', e.target.value)} placeholder="https://..." />
          </div>
        </div>
      </div>

      {/* Skills */}
      <div className="card space-y-4">
        <h3 className="font-semibold text-lg">Skills</h3>
        <input className="input" value={(form.skills || []).join(', ')}
               onChange={e => set('skills', e.target.value.split(',').map((s: string) => s.trim()).filter(Boolean))}
               placeholder="React, Node.js, Python, SQL..." />
        <p className="text-xs" style={{ color: 'var(--muted-foreground)' }}>Comma-separated list of your skills</p>
      </div>
    </div>
  );
}
