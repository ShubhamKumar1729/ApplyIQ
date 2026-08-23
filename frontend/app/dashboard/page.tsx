'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import {
  Briefcase, Send, TrendingUp, Target, Play, ArrowRight,
  CheckCircle2, Clock, XCircle, AlertCircle,
} from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { load(); }, []);
  const load = async () => {
    try { setStats((await api.getDashboard()).data); }
    catch {} finally { setLoading(false); }
  };

  if (loading) return <DashboardSkeleton />;

  const statCards = [
    { label: 'Applications Sent', value: stats?.applicationsSent || 0, icon: Send, color: 'var(--primary)' },
    { label: 'Total Applications', value: stats?.totalApplications || 0, icon: Briefcase, color: 'var(--success)' },
    { label: 'Relevant Jobs', value: stats?.relevantJobs || 0, icon: Target, color: 'var(--warning)' },
    { label: 'Response Rate', value: `${stats?.responseRate || 0}%`, icon: TrendingUp, color: '#8b5cf6' },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p style={{ color: 'var(--muted-foreground)' }}>Your job search at a glance</p>
        </div>
        <button onClick={() => router.push('/searches')} className="btn btn-primary">
          <Play className="w-4 h-4" /> New Search
        </button>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((s, i) => (
          <div key={i} className="card">
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                   style={{ background: `${s.color}15` }}>
                <s.icon className="w-5 h-5" style={{ color: s.color }} />
              </div>
            </div>
            <div className="text-2xl font-bold">{s.value}</div>
            <div className="text-sm" style={{ color: 'var(--muted-foreground)' }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Profile Completeness */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold">Profile Completeness</h3>
          <span className="text-sm font-medium" style={{ color: 'var(--primary)' }}>{stats?.profileCompleteness || 0}%</span>
        </div>
        <div className="w-full h-2 rounded-full" style={{ background: 'var(--muted)' }}>
          <div className="h-full rounded-full transition-all" style={{ width: `${stats?.profileCompleteness || 0}%`, background: 'var(--primary)' }} />
        </div>
        <button onClick={() => router.push('/profile')} className="text-sm mt-3 font-medium" style={{ color: 'var(--primary)' }}>
          Complete your profile →
        </button>
      </div>

      {/* Live Automation */}
      {stats?.liveAutomation && (
        <div className="card" style={{ borderColor: 'var(--success)', borderWidth: 2 }}>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-3 h-3 rounded-full animate-pulse-soft" style={{ background: 'var(--success)' }} />
            <h3 className="font-semibold">Automation Running</h3>
            <button onClick={() => router.push('/automation')} className="ml-auto text-sm font-medium" style={{ color: 'var(--primary)' }}>
              View Details →
            </button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
            <div><span style={{ color: 'var(--muted-foreground)' }}>Role:</span> <span className="font-medium">{stats.liveAutomation.currentRoleKey || 'N/A'}</span></div>
            <div><span style={{ color: 'var(--muted-foreground)' }}>Sent:</span> <span className="font-medium">{stats.liveAutomation.applicationsSent}</span></div>
            <div><span style={{ color: 'var(--muted-foreground)' }}>Found:</span> <span className="font-medium">{stats.liveAutomation.jobsFound}</span></div>
            <div><span style={{ color: 'var(--muted-foreground)' }}>Status:</span> <span className="font-medium">{stats.liveAutomation.status}</span></div>
          </div>
        </div>
      )}

      {/* Recent Applications */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Recent Applications</h2>
          <button onClick={() => router.push('/applications')} className="text-sm font-medium" style={{ color: 'var(--primary)' }}>
            View all →
          </button>
        </div>
        {stats?.recentApplications?.length > 0 ? (
          <div className="space-y-2">
            {stats.recentApplications.slice(0, 5).map((app: any) => (
              <div key={app.id} className="card flex items-center gap-4 py-3 px-4 cursor-pointer hover:shadow-md transition"
                   onClick={() => router.push(`/applications`)}>
                <StatusIcon status={app.status} />
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm truncate">{app.recruiterEmail || 'Unknown'}</div>
                  <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>{app.roleKey || ''} • {app.mode}</div>
                </div>
                <StatusBadge status={app.status} />
              </div>
            ))}
          </div>
        ) : (
          <div className="card text-center py-12">
            <Briefcase className="w-12 h-12 mx-auto mb-3" style={{ color: 'var(--muted-foreground)' }} />
            <p className="font-medium">No applications yet</p>
            <p className="text-sm mt-1" style={{ color: 'var(--muted-foreground)' }}>Create a job search to get started</p>
            <button onClick={() => router.push('/searches')} className="btn btn-primary mt-4 text-sm">
              Create Search <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, { bg: string; text: string }> = {
    EMAIL_SENT: { bg: 'rgba(16,185,129,0.1)', text: 'var(--success)' },
    PREPARED: { bg: 'rgba(59,130,246,0.1)', text: 'var(--primary)' },
    SKIPPED: { bg: 'rgba(100,116,139,0.1)', text: 'var(--muted-foreground)' },
    FAILED: { bg: 'rgba(239,68,68,0.1)', text: 'var(--danger)' },
    AI_MATCHED: { bg: 'rgba(139,92,246,0.1)', text: '#8b5cf6' },
  };
  const c = colors[status] || colors.PREPARED;
  return <span className="badge" style={{ background: c.bg, color: c.text }}>{status}</span>;
}

function StatusIcon({ status }: { status: string }) {
  if (status === 'EMAIL_SENT') return <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--success)' }} />;
  if (status === 'FAILED') return <XCircle className="w-5 h-5" style={{ color: 'var(--danger)' }} />;
  if (status === 'SKIPPED') return <AlertCircle className="w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />;
  return <Clock className="w-5 h-5" style={{ color: 'var(--primary)' }} />;
}

function DashboardSkeleton() {
  return (
    <div className="space-y-8">
      <div><div className="skeleton h-8 w-48 mb-2" /><div className="skeleton h-4 w-64" /></div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1,2,3,4].map(i => <div key={i} className="card"><div className="skeleton h-10 w-10 rounded-xl mb-3" /><div className="skeleton h-8 w-20 mb-2" /><div className="skeleton h-4 w-32" /></div>)}
      </div>
    </div>
  );
}
