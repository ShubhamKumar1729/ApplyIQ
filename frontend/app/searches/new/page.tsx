'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { Plus, Trash2, ArrowLeft, ArrowRight, Loader2, Eye, Sparkles } from 'lucide-react';

interface Role {
  key: string;
  title: string;
  query: string;
  location: string;
  maxApplications: number;
  workplaceType: string;
  datePosted: string;
  enabled: boolean;
  keywords: string[];
  excludedKeywords: string[];
}

export default function NewSearchPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);

  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [roles, setRoles] = useState<Role[]>([{
    key: 'role_1', title: '', query: '', location: '',
    maxApplications: 15, workplaceType: '', datePosted: 'LAST_24H',
    enabled: true, keywords: [], excludedKeywords: [],
  }]);
  const [applicationMode, setApplicationMode] = useState('AUTO_APPLY');
  const [customizeResume, setCustomizeResume] = useState(false);
  const [aiThreshold, setAiThreshold] = useState(70);
  const [globalMax, setGlobalMax] = useState(50);
  const [ccEmails, setCcEmails] = useState('');
  const [bccEmails, setBccEmails] = useState('');

  const addRole = () => {
    setRoles([...roles, {
      key: `role_${roles.length + 1}`, title: '', query: '', location: '',
      maxApplications: 15, workplaceType: '', datePosted: 'LAST_24H',
      enabled: true, keywords: [], excludedKeywords: [],
    }]);
  };

  const removeRole = (i: number) => {
    if (roles.length <= 1) return;
    setRoles(roles.filter((_, idx) => idx !== i));
  };

  const updateRole = (i: number, field: string, value: any) => {
    const updated = [...roles];
    (updated[i] as any)[field] = value;
    setRoles(updated);
  };

  const handleCreate = async () => {
    if (!name.trim()) { alert('Please enter a search name'); return; }
    if (roles.some(r => !r.title.trim())) { alert('All roles need a title'); return; }

    setSaving(true);
    try {
      const payload = {
        name: name.trim(),
        description: description.trim(),
        roles: roles.map(r => ({
          ...r,
          keywords: r.keywords,
          excludedKeywords: r.excludedKeywords,
        })),
        applicationMode,
        customizeResume,
        aiThreshold,
        globalMaxApplications: globalMax,
        ccEmails: ccEmails.split(',').map(e => e.trim()).filter(Boolean),
        bccEmails: bccEmails.split(',').map(e => e.trim()).filter(Boolean),
      };
      await api.createSearch(payload);
      router.push('/searches');
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSaving(false);
    }
  };

  const steps = ['Basic Info', 'Roles', 'Settings', 'Review'];

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fadeIn">
      <div className="flex items-center gap-4">
        <button onClick={() => router.back()} className="btn btn-ghost"><ArrowLeft className="w-4 h-4" /></button>
        <div>
          <h1 className="text-2xl font-bold">Create Job Search</h1>
          <p style={{ color: 'var(--muted-foreground)' }}>Configure your automated job search</p>
        </div>
      </div>

      {/* Step indicator */}
      <div className="flex items-center gap-2">
        {steps.map((s, i) => (
          <div key={i} className="flex items-center gap-2">
            <button onClick={() => setStep(i)}
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${i === step ? 'text-white' : ''}`}
                    style={i === step ? { background: 'var(--primary)' } : i < step ? { background: 'var(--success)', color: 'white' } : { background: 'var(--muted)', color: 'var(--muted-foreground)' }}>
              {i + 1}
            </button>
            <span className={`text-sm hidden sm:block ${i === step ? 'font-medium' : ''}`} style={{ color: i === step ? 'var(--foreground)' : 'var(--muted-foreground)' }}>{s}</span>
            {i < steps.length - 1 && <div className="w-8 h-px" style={{ background: 'var(--border)' }} />}
          </div>
        ))}
      </div>

      {/* Step 0: Basic Info */}
      {step === 0 && (
        <div className="card space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Search Name *</label>
            <input className="input" value={name} onChange={e => setName(e.target.value)}
                   placeholder="e.g., Data Analyst Jobs" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Description <span className="text-xs" style={{ color: 'var(--muted-foreground)' }}>(optional)</span></label>
            <textarea className="input" rows={3} value={description} onChange={e => setDescription(e.target.value)}
                      placeholder="Brief description of this search..." />
          </div>
        </div>
      )}

      {/* Step 1: Roles */}
      {step === 1 && (
        <div className="space-y-4">
          {roles.map((role, i) => (
            <div key={i} className="card space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">Role {i + 1}</h3>
                {roles.length > 1 && (
                  <button onClick={() => removeRole(i)} className="p-1 rounded" style={{ color: 'var(--danger)' }}>
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5">Role Title *</label>
                  <input className="input" value={role.title} onChange={e => updateRole(i, 'title', e.target.value)}
                         placeholder="Data Analyst" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5">Search Query *</label>
                  <input className="input" value={role.query} onChange={e => updateRole(i, 'query', e.target.value)}
                         placeholder="Data Analyst us -hotlist -benchsales" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5">Location <span className="text-xs" style={{ color: 'var(--muted-foreground)' }}>(optional)</span></label>
                  <input className="input" value={role.location} onChange={e => updateRole(i, 'location', e.target.value)}
                         placeholder="Remote / San Francisco / leave empty" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5">Max Applications</label>
                  <input type="number" className="input" value={role.maxApplications}
                         onChange={e => updateRole(i, 'maxApplications', parseInt(e.target.value) || 15)} />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5">Workplace Type</label>
                  <select className="input" value={role.workplaceType} onChange={e => updateRole(i, 'workplaceType', e.target.value)}>
                    <option value="">Any</option>
                    <option value="remote">Remote</option>
                    <option value="onsite">Onsite</option>
                    <option value="hybrid">Hybrid</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5">Date Posted</label>
                  <select className="input" value={role.datePosted} onChange={e => updateRole(i, 'datePosted', e.target.value)}>
                    <option value="LAST_24H">Past 24 Hours</option>
                    <option value="LAST_3D">Past 3 Days</option>
                    <option value="LAST_WEEK">Past Week</option>
                    <option value="LAST_MONTH">Past Month</option>
                    <option value="ANY">Any Time</option>
                  </select>
                </div>
              </div>
            </div>
          ))}
          <button onClick={addRole} className="btn btn-secondary w-full">
            <Plus className="w-4 h-4" /> Add Another Role
          </button>
        </div>
      )}

      {/* Step 2: Settings */}
      {step === 2 && (
        <div className="card space-y-6">
          <div>
            <label className="block text-sm font-medium mb-3">Application Mode</label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                { value: 'AUTO_APPLY', label: 'Auto Apply', desc: 'Search, match, and send automatically' },
                { value: 'REVIEW', label: 'Review First', desc: 'Preview before sending each application' },
                { value: 'TEST', label: 'Test Mode', desc: 'Run everything but never send' },
              ].map(m => (
                <button key={m.value} onClick={() => setApplicationMode(m.value)}
                        className="p-4 rounded-xl text-left border-2 transition"
                        style={{ borderColor: applicationMode === m.value ? 'var(--primary)' : 'var(--border)' }}>
                  <div className="font-medium text-sm">{m.label}</div>
                  <div className="text-xs mt-1" style={{ color: 'var(--muted-foreground)' }}>{m.desc}</div>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">AI Relevance Threshold: {aiThreshold}%</label>
            <input type="range" min="0" max="100" value={aiThreshold}
                   onChange={e => setAiThreshold(parseInt(e.target.value))}
                   className="w-full" style={{ accentColor: 'var(--primary)' }} />
            <p className="text-xs mt-1" style={{ color: 'var(--muted-foreground)' }}>Jobs scoring below this will be skipped</p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">Global Max Applications</label>
            <input type="number" className="input" value={globalMax}
                   onChange={e => setGlobalMax(parseInt(e.target.value) || 50)} />
          </div>

          <div className="flex items-center justify-between p-4 rounded-xl" style={{ background: 'var(--muted)' }}>
            <div>
              <div className="font-medium text-sm">Customize Resume</div>
              <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>AI tailors your resume for each job</div>
            </div>
            <button onClick={() => setCustomizeResume(!customizeResume)}
                    className="w-12 h-6 rounded-full transition relative"
                    style={{ background: customizeResume ? 'var(--primary)' : 'var(--border)' }}>
              <div className="w-5 h-5 rounded-full bg-white absolute top-0.5 transition-all shadow"
                   style={{ left: customizeResume ? '26px' : '2px' }} />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">CC Emails <span className="text-xs" style={{ color: 'var(--muted-foreground)' }}>(optional)</span></label>
              <input className="input" value={ccEmails} onChange={e => setCcEmails(e.target.value)}
                     placeholder="email1@test.com, email2@test.com" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">BCC Emails <span className="text-xs" style={{ color: 'var(--muted-foreground)' }}>(optional)</span></label>
              <input className="input" value={bccEmails} onChange={e => setBccEmails(e.target.value)}
                     placeholder="email@test.com" />
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Review */}
      {step === 3 && (
        <div className="card space-y-6">
          <h3 className="text-lg font-semibold flex items-center gap-2"><Eye className="w-5 h-5" /> Review Your Search</h3>

          <div className="space-y-4">
            <div className="p-4 rounded-xl" style={{ background: 'var(--muted)' }}>
              <div className="text-sm font-medium mb-1">Search</div>
              <div className="text-lg font-semibold">{name}</div>
              {description && <div className="text-sm" style={{ color: 'var(--muted-foreground)' }}>{description}</div>}
            </div>

            <div className="p-4 rounded-xl" style={{ background: 'var(--muted)' }}>
              <div className="text-sm font-medium mb-2">Roles ({roles.length})</div>
              {roles.map((r, i) => (
                <div key={i} className="flex items-center gap-3 py-2 border-b last:border-0" style={{ borderColor: 'var(--border)' }}>
                  <Sparkles className="w-4 h-4" style={{ color: 'var(--primary)' }} />
                  <div>
                    <div className="font-medium text-sm">{r.title}</div>
                    <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>
                      Query: {r.query} {r.location && `• Location: ${r.location}`} • Max: {r.maxApplications}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-3 rounded-xl text-center" style={{ background: 'var(--muted)' }}>
                <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>Mode</div>
                <div className="font-medium text-sm">{applicationMode}</div>
              </div>
              <div className="p-3 rounded-xl text-center" style={{ background: 'var(--muted)' }}>
                <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>AI Threshold</div>
                <div className="font-medium text-sm">{aiThreshold}%</div>
              </div>
              <div className="p-3 rounded-xl text-center" style={{ background: 'var(--muted)' }}>
                <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>Max Apps</div>
                <div className="font-medium text-sm">{globalMax}</div>
              </div>
              <div className="p-3 rounded-xl text-center" style={{ background: 'var(--muted)' }}>
                <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>Resume</div>
                <div className="font-medium text-sm">{customizeResume ? 'Customized' : 'Original'}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button onClick={() => setStep(Math.max(0, step - 1))} disabled={step === 0}
                className="btn btn-secondary" style={{ opacity: step === 0 ? 0.5 : 1 }}>
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        {step < 3 ? (
          <button onClick={() => setStep(step + 1)} className="btn btn-primary">
            Next <ArrowRight className="w-4 h-4" />
          </button>
        ) : (
          <button onClick={handleCreate} disabled={saving} className="btn btn-primary">
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {saving ? 'Creating…' : 'Create Search'}
          </button>
        )}
      </div>
    </div>
  );
}
