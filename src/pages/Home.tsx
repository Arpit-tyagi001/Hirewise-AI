import React from 'react';
import { BarChart3, Check, ChevronRight, FileText, ShieldCheck, Sparkles, Upload, Zap } from 'lucide-react';
import { Button } from '../components/Button';
import { ScoreGauge } from '../components/ScoreGauge';
import { Footer } from '../components/Footer';
import { Page } from '../components/Navbar';

export function Home({ go }: { go: (p: Page) => void }) {
  return (
    <>
      <section className="hero">
        <div className="orb one" />
        <div className="orb two" />
        <div className="eyebrow">
          <Sparkles size={14} /> Production ATS Pipeline
        </div>
        <h1>
          AI Resume Analysis &<br />
          <em>Job Description Matcher.</em>
        </h1>
        <p>
          Parse PDF and DOCX resumes instantly, calculate objective 10-point ATS score breakdown, and run real-time Job Description skill gap analysis.
        </p>
        <div className="heroCtas">
          <Button onClick={() => go('upload')}>
            Upload & Analyze Resume <Upload size={16} />
          </Button>
          <Button kind="ghost" onClick={() => go('dashboard')}>
            View Live Dashboard <ChevronRight size={16} />
          </Button>
        </div>
        <div className="trusted">
          <span>Powered by FastAPI backend + PostgreSQL + Python Rule-Based NLP</span>
        </div>
        
        {/* Sample Analysis Preview Card - Clearly labeled as Sample Demo */}
        <div className="heroPreview">
          <div className="previewTop">
            <span>Sample Candidate Evaluation (Demo Preview)</span>
            <span className="live">
              <i /> FastAPI Active (Port 8000)
            </span>
          </div>
          <div className="candidateRow">
            <div className="portrait">AM</div>
            <div>
              <strong>Alex Morgan (Sample Profile)</strong>
              <span>Senior Full Stack Engineer</span>
            </div>
            <div className="match">91.5% ATS score</div>
          </div>
          <div className="analysisGrid">
            <div className="skillList">
              <span className="label">Sample Extracted Skills</span>
              {['Python & FastAPI', 'React & TypeScript', 'PostgreSQL & Docker'].map(s => (
                <div key={s}>
                  <Check size={14} />
                  {s}
                  <b>Matched</b>
                </div>
              ))}
            </div>
            <ScoreGauge value={92} />
          </div>
        </div>
      </section>

      <section className="features">
        <div className="sectionHead">
          <span className="eyebrow">
            <Zap size={14} /> Core Capabilities
          </span>
          <h2>
            Everything needed for
            <br />
            ATS Resume Evaluation.
          </h2>
        </div>
        <div className="featureGrid">
          {[
            [FileText, 'PDF & DOCX Parser', 'Extracts Name, Email, Phone, Skills, Experience, Education, Projects, and Certifications.'],
            [BarChart3, '10-Dimension ATS Engine', 'Evaluates Skills, Verbs, Formatting, Contact info, Keyword density, and Completeness.'],
            [Sparkles, 'JD Gap Analysis & Rewriter', 'Matches resume text against target Job Descriptions using TF-IDF cosine similarity & rule/LLM rewriter.'],
            [ShieldCheck, 'JWT Auth & User Isolation', 'Multi-tenant authentication model isolating user analysis history and rewrite sessions.']
          ].map(([Icon, title, desc]: any) => (
            <article className="feature" key={title}>
              <span className="featureIcon">
                <Icon size={20} />
              </span>
              <h3>{title}</h3>
              <p>{desc}</p>
              <button onClick={() => go('upload')}>
                Try Now <ChevronRight size={15} />
              </button>
            </article>
          ))}
        </div>
      </section>
      <Footer go={go} />
    </>
  );
}
