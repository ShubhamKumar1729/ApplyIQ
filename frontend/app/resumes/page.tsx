'use client';
import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Upload, FileText, Trash2, Star, Loader2, CheckCircle2 } from 'lucide-react';

export default function ResumesPage() {
  const [resumes, setResumes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  useEffect(() => { load(); }, []);
  const load = async () => {
    try { const res = await api.listResumes(); setResumes(res.data); }
    catch {} finally { setLoading(false); }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try { await api.uploadResume(file); await load(); }
    catch (err: any) { alert(err.message); }
    finally { setUploading(false); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this resume?')) return;
    await api.deleteResume(id);
    await load();
  };

  const handleSetDefault = async (id: string) => {
    await api.setDefaultResume(id);
    await load();
  };

  if (loading) return <div className="space-y-4">{[1,2].map(i => <div key={i} className="card"><div className="skeleton h-6 w-48 mb-3" /><div className="skeleton h-4 w-full" /></div>)}</div>;

  return (
    <div className="max-w-3xl space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Resumes</h1>
          <p style={{ color: 'var(--muted-foreground)' }}>Upload and manage your resumes</p>
        </div>
        <label className="btn btn-primary cursor-pointer">
          {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
          {uploading ? 'Uploading…' : 'Upload Resume'}
          <input type="file" accept=".pdf,.docx" onChange={handleUpload} className="hidden" />
        </label>
      </div>

      {resumes.length === 0 ? (
        <div className="card text-center py-12">
          <FileText className="w-12 h-12 mx-auto mb-3" style={{ color: 'var(--muted-foreground)' }} />
          <p className="font-medium">No resumes yet</p>
          <p className="text-sm mt-1" style={{ color: 'var(--muted-foreground)' }}>Upload a PDF or DOCX resume to get started</p>
        </div>
      ) : (
        <div className="space-y-3">
          {resumes.map((r: any) => (
            <div key={r.id} className="card flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ background: 'rgba(59,130,246,0.1)' }}>
                <FileText className="w-6 h-6" style={{ color: 'var(--primary)' }} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium truncate">{r.originalName}</div>
                <div className="text-xs flex items-center gap-2" style={{ color: 'var(--muted-foreground)' }}>
                  <span>{(r.sizeBytes / 1024).toFixed(0)} KB</span>
                  <span>•</span>
                  <span>{r.status}</span>
                  {r.isDefault && <span className="badge" style={{ background: 'rgba(16,185,129,0.1)', color: 'var(--success)' }}>Default</span>}
                </div>
              </div>
              <div className="flex items-center gap-2">
                {!r.isDefault && (
                  <button onClick={() => handleSetDefault(r.id)} className="p-2 rounded-lg hover:bg-[var(--muted)]" title="Set as default">
                    <Star className="w-4 h-4" style={{ color: 'var(--warning)' }} />
                  </button>
                )}
                <button onClick={() => handleDelete(r.id)} className="p-2 rounded-lg hover:bg-[var(--muted)]" title="Delete">
                  <Trash2 className="w-4 h-4" style={{ color: 'var(--danger)' }} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
