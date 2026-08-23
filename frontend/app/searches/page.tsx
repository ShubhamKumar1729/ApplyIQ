'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { Plus, Play, Pause, Trash2, Copy, Search, Loader2, Settings as SettingsIcon } from 'lucide-react';

export default function SearchesPage() {
  const router = useRouter();
  const [searches, setSearches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, []);
  const load = async () => {
    try { const res = await api.listSearches(); setSearches(res.data); }
    catch {} finally { setLoading(false); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this search?')) return;
    await api.deleteSearch(id);
    await load();
  };

  const handleDuplicate = async (id: string) => {
    await api.duplicateSearch(id);
    await load();
  };

  const handleStartAutomation = async (id: string) => {
    try {
      const res = await api.startAutomation(id);
      router.push('/automation');
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (loading) return <div className="space-y-4">{[1,2].map(i => <div key={i} className="card"><div className="skeleton h-6 w-48 mb-3" /><div className="skeleton h-4 w-full" /></div>)}</div>;

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Job Searches</h1>
          <p style={{ color: 'var(--muted-foreground)' }}>Configure and manage your job searches</p>
        </div>
        <button onClick={() => router.push('/searches/new')} className="btn btn-primary">
          <Plus className="w-4 h-4" /> New Search
        </button>
      </div>

      {searches.length === 0 ? (
        <div className="card text-center py-12">
          <Search className="w-12 h-12 mx-auto mb-3" style={{ color: 'var(--muted-foreground)' }} />
          <p className="font-medium">No job searches yet</p>
          <p className="text-sm mt-1" style={{ color: 'var(--muted-foreground)' }}>Create your first job search to start applying</p>
          <button onClick={() => router.push('/searches/new')} className="btn btn-primary mt-4">
            Create Search <Plus className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {searches.map((s: any) => (
            <div key={s.id} className="card">
              <div className="flex items-start gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold">{s.name}</h3>
                    {s.paused && <span className="badge" style={{ background: 'rgba(245,158,11,0.1)', color: 'var(--warning)' }}>Paused</span>}
                    {s.archived && <span className="badge" style={{ background: 'var(--muted)', color: 'var(--muted-foreground)' }}>Archived</span>}
                  </div>
                  {s.description && <p className="text-sm mb-3" style={{ color: 'var(--muted-foreground)' }}>{s.description}</p>}
                  <div className="flex flex-wrap gap-2 mb-3">
                    {s.roles?.slice(0, 5).map((r: any, i: number) => (
                      <span key={i} className="badge" style={{ background: 'var(--muted)', color: 'var(--foreground)' }}>
                        {r.title}
                      </span>
                    ))}
                    {s.roles?.length > 5 && <span className="text-xs" style={{ color: 'var(--muted-foreground)' }}>+{s.roles.length - 5} more</span>}
                  </div>
                  <div className="flex items-center gap-4 text-xs" style={{ color: 'var(--muted-foreground)' }}>
                    <span>Mode: <strong>{s.applicationMode}</strong></span>
                    <span>AI Threshold: <strong>{s.aiThreshold}%</strong></span>
                    <span>Max Apps: <strong>{s.globalMaxApplications}</strong></span>
                    {s.customizeResume && <span className="badge" style={{ background: 'rgba(139,92,246,0.1)', color: '#8b5cf6' }}>Resume Customization</span>}
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button onClick={() => handleStartAutomation(s.id)} className="p-2 rounded-lg hover:bg-[var(--muted)]" title="Start automation">
                    <Play className="w-4 h-4" style={{ color: 'var(--success)' }} />
                  </button>
                  <button onClick={() => router.push(`/searches/${s.id}`)} className="p-2 rounded-lg hover:bg-[var(--muted)]" title="Edit">
                    <SettingsIcon className="w-4 h-4" style={{ color: 'var(--primary)' }} />
                  </button>
                  <button onClick={() => handleDuplicate(s.id)} className="p-2 rounded-lg hover:bg-[var(--muted)]" title="Duplicate">
                    <Copy className="w-4 h-4" />
                  </button>
                  <button onClick={() => handleDelete(s.id)} className="p-2 rounded-lg hover:bg-[var(--muted)]" title="Delete">
                    <Trash2 className="w-4 h-4" style={{ color: 'var(--danger)' }} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
