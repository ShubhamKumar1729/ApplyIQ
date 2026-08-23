'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { Briefcase, Filter, CheckCircle2, Clock, XCircle, AlertCircle, Mail } from 'lucide-react';

const STATUS_FILTERS = ['ALL', 'EMAIL_SENT', 'PREPARED', 'AI_MATCHED', 'SKIPPED', 'FAILED', 'RESPONSE', 'INTERVIEW', 'OFFER', 'REJECTED'];

export default function ApplicationsPage() {
  const router = useRouter();
  const [apps, setApps] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');

  useEffect(() => { load(); }, [filter]);
  const load = async () => {
    setLoading(true);
    try {
      const params = filter !== 'ALL' ? `status=${filter}&limit=100` : 'limit=100';
      const res = await api.listApplications(params);
      setApps(res.data.applications);
      setTotal(res.data.total);
    } catch {} finally { setLoading(false); }
  };

  const handleStatusChange = async (id: string, status: string) => {
    await api.updateAppStatus(id, status);
    await load();
  };

  const statusColor = (s: string) => {
    const m: Record<string, string> = {
      EMAIL_SENT: 'var(--success)', PREPARED: 'var(--primary)', AI_MATCHED: '#8b5cf6',
      SKIPPED: 'var(--muted-foreground)', FAILED: 'var(--danger)', RESPONSE: 'var(--warning)',
      INTERVIEW: 'var(--success)', OFFER: 'var(--success)', REJECTED: 'var(--danger)',
    };
    return m[s] || 'var(--muted-foreground)';
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Applications</h1>
          <p style={{ color: 'var(--muted-foreground)' }}>{total} total applications</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {STATUS_FILTERS.map(s => (
          <button key={s} onClick={() => setFilter(s)}
                  className="badge cursor-pointer whitespace-nowrap px-3 py-1.5 rounded-lg text-sm transition"
                  style={filter === s ? { background: 'var(--primary)', color: 'white' } : { background: 'var(--muted)', color: 'var(--muted-foreground)' }}>
            {s === 'ALL' ? 'All' : s.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* List */}
      {loading ? (
        <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="card"><div className="skeleton h-6 w-full" /></div>)}</div>
      ) : apps.length === 0 ? (
        <div className="card text-center py-12">
          <Briefcase className="w-12 h-12 mx-auto mb-3" style={{ color: 'var(--muted-foreground)' }} />
          <p className="font-medium">No applications found</p>
        </div>
      ) : (
        <div className="space-y-2">
          {apps.map(app => (
            <div key={app.id} className="card flex items-center gap-4 py-3 px-4 cursor-pointer hover:shadow-md transition"
                 onClick={() => router.push(`/applications`)}>
              <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                   style={{ background: `${statusColor(app.status)}15` }}>
                {app.status === 'EMAIL_SENT' ? <Mail className="w-5 h-5" style={{ color: statusColor(app.status) }} /> :
                 app.status === 'FAILED' ? <XCircle className="w-5 h-5" style={{ color: statusColor(app.status) }} /> :
                 app.status === 'SKIPPED' ? <AlertCircle className="w-5 h-5" style={{ color: statusColor(app.status) }} /> :
                 <Clock className="w-5 h-5" style={{ color: statusColor(app.status) }} />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm truncate">{app.recruiterEmail}</div>
                <div className="text-xs flex items-center gap-2" style={{ color: 'var(--muted-foreground)' }}>
                  <span>{app.roleKey}</span>
                  {app.matchScore > 0 && <span>• Score: {app.matchScore}</span>}
                  <span>• {app.mode}</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="badge text-xs" style={{ background: `${statusColor(app.status)}15`, color: statusColor(app.status) }}>
                  {app.status.replace('_', ' ')}
                </span>
                {app.status === 'PREPARED' && (
                  <select className="text-xs rounded border p-1" style={{ borderColor: 'var(--border)', background: 'var(--background)' }}
                          onClick={e => e.stopPropagation()}
                          onChange={e => { if (e.target.value) handleStatusChange(app.id, e.target.value); e.target.value = ''; }}>
                    <option value="">Update</option>
                    <option value="RESPONSE">Response</option>
                    <option value="INTERVIEW">Interview</option>
                    <option value="OFFER">Offer</option>
                    <option value="REJECTED">Rejected</option>
                  </select>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
