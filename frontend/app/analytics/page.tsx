'use client';
import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { BarChart3, TrendingUp, Send, Target, Award, XCircle } from 'lucide-react';

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getAnalytics().then(res => setData(res.data)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="space-y-6">{[1,2,3].map(i => <div key={i} className="card"><div className="skeleton h-48 w-full" /></div>)}</div>;

  const maxApps = Math.max(...(data?.applicationsOverTime?.map((d: any) => d.count) || [1]), 1);

  return (
    <div className="space-y-6 animate-fadeIn">
      <div>
        <h1 className="text-2xl font-bold">Analytics</h1>
        <p style={{ color: 'var(--muted-foreground)' }}>Your job search performance</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        {[
          { label: 'Total', value: data?.totalApplications || 0, icon: BarChart3 },
          { label: 'Sent', value: data?.totalSent || 0, icon: Send, color: 'var(--success)' },
          { label: 'Responses', value: data?.totalResponses || 0, icon: TrendingUp, color: 'var(--primary)' },
          { label: 'Interviews', value: data?.totalInterviews || 0, icon: Award, color: 'var(--warning)' },
          { label: 'Offers', value: data?.totalOffers || 0, icon: Award, color: 'var(--success)' },
          { label: 'Rejected', value: data?.totalRejected || 0, icon: XCircle, color: 'var(--danger)' },
        ].map((s, i) => (
          <div key={i} className="card text-center">
            <s.icon className="w-6 h-6 mx-auto mb-2" style={{ color: s.color || 'var(--muted-foreground)' }} />
            <div className="text-2xl font-bold">{s.value}</div>
            <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Applications Over Time */}
      <div className="card">
        <h3 className="font-semibold mb-4">Applications Over Time (30 days)</h3>
        {data?.applicationsOverTime?.length > 0 ? (
          <div className="flex items-end gap-1 h-40">
            {data.applicationsOverTime.map((d: any, i: number) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <div className="w-full rounded-t transition-all hover:opacity-80"
                     style={{
                       height: `${(d.count / maxApps) * 100}%`,
                       minHeight: d.count > 0 ? '4px' : '0px',
                       background: 'var(--primary)',
                     }}
                     title={`${d.date}: ${d.count}`}
                />
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-center py-8" style={{ color: 'var(--muted-foreground)' }}>No data yet</p>
        )}
      </div>

      {/* Status Funnel */}
      <div className="card">
        <h3 className="font-semibold mb-4">Status Funnel</h3>
        {data?.statusFunnel && Object.values(data.statusFunnel).some((v: any) => v > 0) ? (
          <div className="space-y-2">
            {Object.entries(data.statusFunnel).map(([status, count]: [string, any]) => {
              const max = Math.max(...Object.values(data.statusFunnel) as number[], 1);
              return (
                <div key={status} className="flex items-center gap-3">
                  <div className="w-28 text-xs text-right" style={{ color: 'var(--muted-foreground)' }}>{status.replace('_', ' ')}</div>
                  <div className="flex-1 h-6 rounded-full overflow-hidden" style={{ background: 'var(--muted)' }}>
                    <div className="h-full rounded-full transition-all flex items-center justify-end pr-2"
                         style={{ width: `${(count / max) * 100}%`, background: 'var(--primary)', minWidth: count > 0 ? '24px' : 0 }}>
                      {count > 0 && <span className="text-xs text-white font-medium">{count}</span>}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-sm text-center py-8" style={{ color: 'var(--muted-foreground)' }}>No data yet</p>
        )}
      </div>

      {/* Per Role */}
      {data?.perRolePerformance?.length > 0 && (
        <div className="card">
          <h3 className="font-semibold mb-4">Performance by Role</h3>
          <div className="space-y-3">
            {data.perRolePerformance.map((r: any, i: number) => (
              <div key={i} className="flex items-center gap-4">
                <Target className="w-4 h-4" style={{ color: 'var(--primary)' }} />
                <div className="flex-1">
                  <div className="text-sm font-medium">{r.roleKey}</div>
                  <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>
                    {r.applications} applications, {r.sent} sent
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <p className="text-xs text-center" style={{ color: 'var(--muted-foreground)' }}>
        * Statistics update as automation processes jobs. Small sample sizes may not be representative.
      </p>
    </div>
  );
}
