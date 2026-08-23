'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/store';
import { Zap, ArrowRight, Shield, Brain, FileText, BarChart3, Sparkles, CheckCircle2 } from 'lucide-react';

export default function LandingPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) router.push('/dashboard');
  }, [user, loading, router]);

  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="skeleton w-8 h-8 rounded-full" /></div>;

  return (
    <div className="min-h-screen">
      {/* Nav */}
      <nav className="fixed top-0 w-full z-50 glass border-b" style={{ borderColor: 'var(--border)' }}>
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold">ApplyIQ</span>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => router.push('/login')} className="btn btn-ghost text-sm">Log in</button>
            <button onClick={() => router.push('/signup')} className="btn btn-primary text-sm">
              Get Started <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center animate-fadeIn">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium mb-8"
               style={{ background: 'var(--muted)', color: 'var(--muted-foreground)' }}>
            <Sparkles className="w-4 h-4" /> AI-Powered Job Applications
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold leading-tight mb-6">
            Apply smarter.<br />
            <span style={{ color: 'var(--primary)' }}>Not harder.</span>
          </h1>
          <p className="text-xl mb-10 max-w-2xl mx-auto" style={{ color: 'var(--muted-foreground)' }}>
            ApplyIQ automates your job search — from discovering roles to sending personalized
            applications with AI-tailored resumes. Track everything in one dashboard.
          </p>
          <div className="flex items-center justify-center gap-4">
            <button onClick={() => router.push('/signup')} className="btn btn-primary text-lg px-8 py-3">
              Start Free <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6" style={{ background: 'var(--muted)' }}>
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Everything you need to land your next role</h2>
          <p className="text-center mb-16" style={{ color: 'var(--muted-foreground)' }}>
            Discover → Match → Tailor → Apply → Track
          </p>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Brain, title: 'AI Job Matching', desc: 'Groq AI evaluates every job for genuine relevance. No more spam applications.' },
              { icon: FileText, title: 'Resume Customization', desc: 'AI tailors your resume for each role using your real experience — never fabricated.' },
              { icon: Zap, title: 'One-Click Apply', desc: 'Automated search, filtering, and personalized email delivery to recruiters.' },
              { icon: BarChart3, title: 'Analytics Dashboard', desc: 'Track applications, response rates, and interview pipeline in real time.' },
              { icon: Shield, title: 'Smart Filters', desc: 'Block bench sales, junk posts, and non-matching roles automatically.' },
              { icon: CheckCircle2, title: 'Application Tracking', desc: 'Full lifecycle tracking from discovery to offer. Never lose an application.' },
            ].map((f, i) => (
              <div key={i} className="card animate-fadeIn" style={{ animationDelay: `${i * 100}ms` }}>
                <f.icon className="w-10 h-10 mb-4" style={{ color: 'var(--primary)' }} />
                <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
                <p style={{ color: 'var(--muted-foreground)' }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to automate your job search?</h2>
          <p className="mb-8" style={{ color: 'var(--muted-foreground)' }}>
            Set up in 2 minutes. No credit card required.
          </p>
          <button onClick={() => router.push('/signup')} className="btn btn-primary text-lg px-8 py-3">
            Get Started Free
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t text-center text-sm" style={{ borderColor: 'var(--border)', color: 'var(--muted-foreground)' }}>
        © 2024 ApplyIQ. Apply smarter, not harder.
      </footer>
    </div>
  );
}
