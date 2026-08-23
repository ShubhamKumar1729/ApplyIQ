'use client';
import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Briefcase, ExternalLink, Star } from 'lucide-react';

export default function JobsPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listJobs('limit=100').then(res => setJobs(res.data.jobs)).finally(() => setLoading(false));
  }, []);

  const handleSave = async (id: string) => {
    await api.saveJob(id);
  };

  if (loading) return <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="card"><div className="skeleton h-6 w-full" /></div>)}</div>;

  return (
    <div className="space-y-6 animate-fadeIn">
      <div>
        <h1 className="text-2xl font-bold">Jobs</h1>
        <p style={{ color: 'var(--muted-foreground)' }}>Discovered jobs from your searches</p>
      </div>

      {jobs.length === 0 ? (
        <div className="card text-center py-12">
          <Briefcase className="w-12 h-12 mx-auto mb-3" style={{ color: 'var(--muted-foreground)' }} />
          <p className="font-medium">No jobs discovered yet</p>
          <p className="text-sm mt-1" style={{ color: 'var(--muted-foreground)' }}>Start an automation to discover jobs</p>
        </div>
      ) : (
        <div className="grid gap-3">
          {jobs.map(job => (
            <div key={job.id} className="card">
              <div className="flex items-start gap-4">
                <div className="flex-1">
                  <h3 className="font-semibold">{job.title || 'Unknown Title'}</h3>
                  <div className="text-sm flex flex-wrap items-center gap-2 mt-1" style={{ color: 'var(--muted-foreground)' }}>
                    {job.company && <span>{job.company}</span>}
                    {job.location && <span>• {job.location}</span>}
                    {job.workplaceType && <span>• {job.workplaceType}</span>}
                  </div>
                  {job.recruiterEmail && (
                    <div className="text-xs mt-2" style={{ color: 'var(--primary)' }}>
                      📧 {job.recruiterEmail}
                    </div>
                  )}
                  {job.description && (
                    <p className="text-sm mt-2 line-clamp-3" style={{ color: 'var(--muted-foreground)' }}>
                      {job.description.slice(0, 200)}...
                    </p>
                  )}
                  <div className="flex items-center gap-2 mt-3">
                    {job.url && (
                      <a href={job.url} target="_blank" rel="noopener noreferrer"
                         className="text-xs font-medium flex items-center gap-1" style={{ color: 'var(--primary)' }}>
                        <ExternalLink className="w-3 h-3" /> View Post
                      </a>
                    )}
                  </div>
                </div>
                <button onClick={() => handleSave(job.id)} className="p-2 rounded-lg hover:bg-[var(--muted)]">
                  <Star className="w-4 h-4" style={{ color: 'var(--warning)' }} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
