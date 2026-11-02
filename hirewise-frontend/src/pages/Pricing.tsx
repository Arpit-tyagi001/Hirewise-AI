import React from 'react';
import { Check, ChevronRight, Zap } from 'lucide-react';
import { Button } from '../components/Button';
import { Footer } from '../components/Footer';
import { Page } from '../components/Navbar';

export function Pricing({ go }: { go: (p: Page) => void }) {
  const plans = [
    {
      name: 'Free Demo Plan',
      price: '$0',
      period: 'forever',
      desc: 'Instant ATS resume parsing and JD skill matching',
      features: [
        'PDF & DOCX Resume Uploads',
        '10-Dimension ATS Scoring',
        'TF-IDF Cosine Similarity JD Match',
        'Anonymous Demo Access'
      ],
      action: 'Start Free Analysis',
      page: 'upload' as Page,
      highlight: false
    },
    {
      name: 'Professional Developer',
      price: '$29',
      period: 'per month',
      desc: 'Full user history, bullet rewriter & DOCX export',
      features: [
        'Everything in Free',
        'JWT Auth & Unlimited History',
        'Rule-Based Weak Verb Upgrades',
        'Groq LLM Guardrailed Bullet Rewriter',
        'Tailored Resume DOCX Export'
      ],
      action: 'Try Pro Features',
      page: 'upload' as Page,
      highlight: true
    },
    {
      name: 'Enterprise Recruiter',
      price: '$99',
      period: 'per month',
      desc: 'Multi-tenant team management & custom API access',
      features: [
        'Everything in Pro',
        'Multi-User Team Isolation',
        'Custom Skill Taxonomy Definition',
        'Dedicated API Key Access',
        'Priority SLA Support'
      ],
      action: 'Contact Sales',
      page: 'contact' as Page,
      highlight: false
    }
  ];

  return (
    <>
      <section style={{ maxWidth: 1100, margin: '40px auto', padding: '0 20px' }}>
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <span className="eyebrow"><Zap size={14} /> Transparent Plans</span>
          <h1 style={{ fontSize: 36, margin: '10px 0 8px' }}>Flexible Pricing for Developers & Recruiters</h1>
          <p style={{ color: '#94a3b8' }}>Objective ATS score calculation & AI bullet rewriting powered by FastAPI.</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 24 }}>
          {plans.map(p => (
            <div
              key={p.name}
              className="panel"
              style={{
                padding: 32,
                border: p.highlight ? '2px solid #3b82f6' : '1px solid #ffffff15',
                background: p.highlight ? '#1e293b' : '#0c1525',
                position: 'relative'
              }}
            >
              {p.highlight && (
                <span style={{ position: 'absolute', top: -12, right: 24, background: '#2563eb', color: '#fff', fontSize: 11, fontWeight: 700, padding: '3px 10px', borderRadius: 10 }}>
                  POPULAR
                </span>
              )}
              <h3 style={{ fontSize: 20, margin: 0 }}>{p.name}</h3>
              <p style={{ fontSize: 13, color: '#94a3b8', margin: '6px 0 20px' }}>{p.desc}</p>
              <div style={{ marginBottom: 24 }}>
                <strong style={{ fontSize: 36, color: '#f8fafc' }}>{p.price}</strong>
                <span style={{ fontSize: 13, color: '#64748b' }}> / {p.period}</span>
              </div>
              <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 28px', display: 'grid', gap: 12 }}>
                {p.features.map(f => (
                  <li key={f} style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, color: '#cbd5e1' }}>
                    <Check size={16} style={{ color: '#60a5fa' }} /> {f}
                  </li>
                ))}
              </ul>
              <Button onClick={() => go(p.page)} kind={p.highlight ? 'primary' : 'ghost'} style={{ width: '100%' }}>
                {p.action} <ChevronRight size={15} />
              </Button>
            </div>
          ))}
        </div>
      </section>
      <Footer go={go} />
    </>
  );
}
