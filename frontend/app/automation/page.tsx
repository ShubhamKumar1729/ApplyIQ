'use client';
import { useEffect, useState, useRef } from 'react';
import api from '@/lib/api';
import { Zap, Play, Pause, Square, RefreshCw, Terminal, Activity, Loader2 } from 'lucide-react';

export default function AutomationPage() {
  const [run, setRun] = useState<any>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState('');
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { loadStatus(); }, []);

  const loadStatus = async () => {
    try {
      const res = await api.getAutomationStatus();
      setRun(res.data);
      if (res.data?.id) {
        const logsRes = await api.getLogs(res.data.id);
        setLogs(logsRes.data);
      }
    } catch {} finally { setLoading(false); }
  };

  // Poll for updates
  useEffect(() => {
    if (!run || (run.status !== 'RUNNING' && run.status !== 'PAUSED')) return;
    const interval = setInterval(loadStatus, 3000);
    return () => clearInterval(interval);
  }, [run?.status, run?.id]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleAction = async (action: string) => {
    if (!run) return;
    setActionLoading(action);
    try {
      if (action === 'stop') await api.stopAutomation(run.id);
      else if (action === 'pause') await api.pauseAutomation(run.id);
      else if (action === 'resume') await api.resumeAutomation(run.id);
      await loadStatus();
    } catch (err: any) { alert(err.message); }
    finally { setActionLoading(''); }
  };

  const logColor = (level: string) => {
    switch (level) {
      case 'success': return 'var(--success)';
      case 'error': return 'var(--danger)';
      case 'warn': return 'var(--warning)';
      default: return 'var(--muted-foreground)';
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Automation</h1>
          <p style={{ color: 'var(--muted-foreground)' }}>Live automation status and controls</p>
        </div>
        {run && (run.status === 'RUNNING' || run.status === 'PAUSED') && (
          <div className="flex items-center gap-2">
            {run.status === 'RUNNING' ? (
              <button onClick={() => handleAction('pause')} disabled={!!actionLoading}
                      className="btn btn-secondary text-sm">
                {actionLoading === 'pause' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Pause className="w-4 h-4" />}
                Pause
              </button>
            ) : (
              <button onClick={() => handleAction('resume')} disabled={!!actionLoading}
                      className="btn btn-primary text-sm">
                {actionLoading === 'resume' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                Resume
              </button>
            )}
            <button onClick={() => handleAction('stop')} disabled={!!actionLoading}
                    className="btn btn-danger text-sm">
              {actionLoading === 'stop' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Square className="w-4 h-4" />}
              Stop
            </button>
          </div>
        )}
      </div>

      {!run && !loading ? (
        <div className="card text-center py-16">
          <Zap className="w-16 h-16 mx-auto mb-4" style={{ color: 'var(--muted-foreground)' }} />
          <h3 className="text-lg font-semibold mb-2">No Active Automation</h3>
          <p className="text-sm" style={{ color: 'var(--muted-foreground)' }}>
            Start an automation from your job searches to see live status here.
          </p>
        </div>
      ) : (
        <>
          {/* Stats */}
          {run && (
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
              {[
                { label: 'Status', value: run.status, color: run.status === 'RUNNING' ? 'var(--success)' : run.status === 'PAUSED' ? 'var(--warning)' : 'var(--muted-foreground)' },
                { label: 'Jobs Found', value: run.jobsFound },
                { label: 'Evaluated', value: run.jobsEvaluated },
                { label: 'Relevant', value: run.relevantCount, color: 'var(--success)' },
                { label: 'Sent', value: run.applicationsSent, color: 'var(--primary)' },
                { label: 'Skipped', value: run.skippedCount },
              ].map((s, i) => (
                <div key={i} className="card text-center py-3">
                  <div className="text-xs mb-1" style={{ color: 'var(--muted-foreground)' }}>{s.label}</div>
                  <div className="text-lg font-bold" style={s.color ? { color: s.color } : {}}>{s.value}</div>
                </div>
              ))}
            </div>
          )}

          {/* Current progress */}
          {run && (run.currentRoleKey || run.currentJobTitle) && (
            <div className="card" style={{ borderColor: 'var(--success)', borderWidth: 2 }}>
              <div className="flex items-center gap-3">
                <Activity className="w-5 h-5 animate-pulse-soft" style={{ color: 'var(--success)' }} />
                <div>
                  <div className="text-sm font-medium">Currently Processing</div>
                  <div className="text-xs" style={{ color: 'var(--muted-foreground)' }}>
                    Role: {run.currentRoleKey || 'N/A'} {run.currentJobTitle && `• Job: ${run.currentJobTitle}`}
                  </div>
                </div>
                {run.status === 'RUNNING' && <RefreshCw className="w-4 h-4 animate-spin ml-auto" style={{ color: 'var(--success)' }} />}
              </div>
            </div>
          )}

          {/* Activity Log */}
          <div className="card">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <Terminal className="w-4 h-4" /> Activity Log
            </h3>
            <div className="bg-black/5 dark:bg-white/5 rounded-xl p-4 max-h-96 overflow-y-auto font-mono text-xs space-y-1">
              {logs.length === 0 ? (
                <p style={{ color: 'var(--muted-foreground)' }}>No logs yet...</p>
              ) : (
                logs.map((log: any, i: number) => (
                  <div key={i} className="flex items-start gap-2 py-0.5">
                    <span style={{ color: 'var(--muted-foreground)' }}>
                      {log.createdAt ? new Date(log.createdAt).toLocaleTimeString() : ''}
                    </span>
                    <span style={{ color: logColor(log.level) }}>{log.message}</span>
                  </div>
                ))
              )}
              <div ref={logEndRef} />
            </div>
          </div>
        </>
      )}
    </div>
  );
}
