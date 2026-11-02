import React from 'react';
import { ChevronRight, Cpu, Database, ShieldCheck, Sparkles } from 'lucide-react';
import { Button } from '../components/Button';
import { Footer } from '../components/Footer';
import { Page } from '../components/Navbar';

export function About({ go }: { go: (p: Page) => void }) {
  return (
    <>
      <section style={{ maxWidth: 900, margin: '40px auto', padding: '0 20px' }}>
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <span className="eyebrow"><Sparkles size={14} /> Architecture Overview</span>
          <h1 style={{ fontSize: 36, margin: '10px 0 8px' }}>About HireWise AI</h1>
          <p style={{ color: '#94a3b8' }}>A production SaaS solution for objective ATS evaluation and JD-aware tailoring.</p>
        </div>

        <div className="panel" style={{ padding: 32, display: 'grid', gap: 24 }}>
          <div style={{ display: 'flex', gap: 16 }}>
            <Cpu size={28} style={{ color: '#60a5fa', flexShrink: 0 }} />
            <div>
              <h3 style={{ margin: '0 0 6px', fontSize: 18 }}>Rule-Based & LLM Hybrid Engine</h3>
              <p style={{ margin: 0, color: '#94a3b8', fontSize: 14 }}>
                HireWise AI combines deterministic Python NLP rules (weak verb upgrades, keyword matching) with Groq LLM fallback (<code style={{ color: '#60a5fa' }}>openai/gpt-oss-120b</code>). Hard fabrication guardrails ensure zero hallucinated metrics or skills.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 16 }}>
            <Database size={28} style={{ color: '#34d399', flexShrink: 0 }} />
            <div>
              <h3 style={{ margin: '0 0 6px', fontSize: 18 }}>PostgreSQL & Alembic Migrations</h3>
              <p style={{ margin: 0, color: '#94a3b8', fontSize: 14 }}>
                Built on FastAPI and SQLAlchemy ORM with full schema versioning via Alembic migrations. User authentication is secured via bcrypt password hashing and JWT access tokens.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 16 }}>
            <ShieldCheck size={28} style={{ color: '#a78bfa', flexShrink: 0 }} />
            <div>
              <h3 style={{ margin: '0 0 6px', fontSize: 18 }}>Data Privacy & Security</h3>
              <p style={{ margin: 0, color: '#94a3b8', fontSize: 14 }}>
                Includes 10 MB upload limits, MIME-type verification (magic bytes), filename sanitization, CORS restriction, and strict user record isolation.
              </p>
            </div>
          </div>

          <div style={{ marginTop: 12, display: 'flex', gap: 12 }}>
            <Button onClick={() => go('upload')}>
              Analyze Resume Now <ChevronRight size={15} />
            </Button>
            <Button kind="ghost" onClick={() => go('contact')}>
              Contact Engineering
            </Button>
          </div>
        </div>
      </section>
      <Footer go={go} />
    </>
  );
}
