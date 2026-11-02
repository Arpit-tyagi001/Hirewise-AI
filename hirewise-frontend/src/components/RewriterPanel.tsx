import React, { useState } from 'react';
import { Sparkles, Download, RefreshCw, ShieldCheck, CheckCircle2, AlertCircle, FileText } from 'lucide-react';
import { BulletDiff, BulletRewriteItem } from './BulletDiff';

import { API_BASE_URL } from '../services/api';

interface RewriterPanelProps {
  analysisId: number;
  initialJobDescription?: string;
  token: string | null;
}

export const RewriterPanel: React.FC<RewriterPanelProps> = ({
  analysisId,
  initialJobDescription = 'We are seeking a Senior Full Stack Engineer proficient in Python, FastAPI, React, TypeScript, and PostgreSQL.',
  token
}) => {
  const [jobDescription, setJobDescription] = useState(initialJobDescription);
  const [apiKey, setApiKey] = useState(localStorage.getItem('hirewise_groq_key') || '');
  const [showKeyInput, setShowKeyInput] = useState(false);
  const [rewrites, setRewrites] = useState<BulletRewriteItem[]>([]);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleApiKeyChange = (val: string) => {
    setApiKey(val);
    if (val.trim()) {
      localStorage.setItem('hirewise_groq_key', val.trim());
    } else {
      localStorage.removeItem('hirewise_groq_key');
    }
  };

  const handleGenerateRewrites = async () => {
    if (!jobDescription.trim()) {
      setErrorMsg('Please enter a target Job Description.');
      return;
    }

    setLoading(true);
    setErrorMsg('');

    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch(`${API_BASE_URL}/rewrite-resume`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          analysis_id: analysisId,
          job_description: jobDescription,
          api_key: apiKey.trim() || undefined
        })
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to generate bullet rewrites.');
      }

      const data = await res.json();
      setSessionId(data.session_id);
      // Mark all rewrites as 'accepted' by default
      const initialItems: BulletRewriteItem[] = (data.rewrites || []).map((rw: any) => ({
        ...rw,
        status: 'accepted'
      }));
      setRewrites(initialItems);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || 'An error occurred while calling the rewriter backend.');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAccept = (id: string, accept: boolean) => {
    setRewrites(prev =>
      prev.map(item => {
        if (item.id === id) {
          return { ...item, status: accept ? 'accepted' : 'rejected' };
        }
        return item;
      })
    );
  };

  const handleExportDOCX = async () => {
    setExporting(true);
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch(`${API_BASE_URL}/export-tailored-resume`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          analysis_id: analysisId,
          accepted_rewrites: rewrites
        })
      });

      if (!res.ok) {
        throw new Error('Failed to generate DOCX export.');
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Tailored_Resume_Analysis_${analysisId}.docx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error(err);
      alert('Failed to download tailored DOCX resume.');
    } finally {
      setExporting(false);
    }
  };

  const acceptedCount = rewrites.filter(r => r.status === 'accepted').length;

  return (
    <article className="panel" style={{ border: '1px solid #3b82f655', background: 'linear-gradient(145deg, #091326, #050b18)', marginTop: 24, borderRadius: 16, padding: 24 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <span className="eyebrow" style={{ color: '#60a5fa' }}>
            <Sparkles size={14} /> JD-Aware Resume Tailoring Engine
          </span>
          <h3 style={{ fontSize: 20, margin: '4px 0', color: '#f8fafc' }}>Bullet-by-Bullet Resume Rewriter</h3>
          <p style={{ margin: 0, fontSize: 13, color: '#94a3b8' }}>
            Upgrades weak action verbs and aligns possessed technical skills with target Job Description.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#10b98115', border: '1px solid #10b98140', padding: '6px 12px', borderRadius: 20, color: '#4ade80', fontSize: 12, fontWeight: 600 }}>
          <ShieldCheck size={16} />
          <span>Zero Fabrications Constraint Enforced</span>
        </div>
      </header>

      {errorMsg && (
        <div style={{ background: '#ef444415', border: '1px solid #ef444455', color: '#fca5a5', padding: '10px 14px', borderRadius: 8, fontSize: 12, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <AlertCircle size={16} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Job Description Input Area */}
      <div style={{ marginBottom: 20 }}>
        <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#cbd5e1', marginBottom: 6 }}>
          Target Job Description Text
        </label>
        <textarea
          style={{ width: '100%', minHeight: 90, background: '#060b18', border: '1px solid #ffffff15', borderRadius: 10, padding: 12, color: '#f8fafc', fontSize: 12, lineHeight: 1.5 }}
          value={jobDescription}
          onChange={e => setJobDescription(e.target.value)}
          placeholder="Paste Job Description here to generate bullet-by-bullet rewrites..."
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 10 }}>
          <span style={{ fontSize: 11, color: '#64748b' }}>{jobDescription.length} characters</span>
          <button
            onClick={handleGenerateRewrites}
            disabled={loading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '10px 18px',
              background: 'linear-gradient(135deg, #2563eb, #3b82f6)',
              color: '#ffffff',
              border: 'none',
              borderRadius: 8,
              fontWeight: 600,
              fontSize: 13,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1
            }}
          >
            {loading ? <RefreshCw className="animate-spin" size={16} /> : <Sparkles size={16} />}
            {loading ? 'Generating Rewrites...' : 'Generate Tailored Bullet Rewrites'}
          </button>
        </div>

        <div style={{ marginTop: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 10px', background: '#ffffff04', borderRadius: 8, border: '1px solid #ffffff0a' }}>
          <button
            type="button"
            onClick={() => setShowKeyInput(!showKeyInput)}
            style={{ fontSize: 11, color: '#93c5fd', background: 'none', border: 'none', cursor: 'pointer', padding: 0, textDecoration: 'underline' }}
          >
            {showKeyInput ? 'Hide Groq API Key Setting' : '⚙️ Custom Groq API Key (Optional)'}
          </button>
          <span style={{ fontSize: 11, color: apiKey ? '#86efac' : '#94a3b8' }}>
            {apiKey ? '🤖 Custom Groq LLM Enabled' : '⚡ Smart Technical NLP Engine Active'}
          </span>
        </div>

        {showKeyInput && (
          <div style={{ marginTop: 8, background: '#0b1329', border: '1px solid #1e293b', borderRadius: 8, padding: 10 }}>
            <label style={{ display: 'block', fontSize: 11, color: '#94a3b8', marginBottom: 4 }}>
              Groq Cloud API Key (Get a free key at <a href="https://console.groq.com/keys" target="_blank" rel="noreferrer" style={{ color: '#60a5fa' }}>console.groq.com</a>)
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={e => handleApiKeyChange(e.target.value)}
              placeholder="gsk_..."
              style={{ width: '100%', background: '#020617', border: '1px solid #334155', borderRadius: 6, padding: '6px 10px', color: '#f8fafc', fontSize: 12 }}
            />
          </div>
        )}
      </div>

      {/* Generated Bullet Rewrites List */}
      {rewrites.length > 0 && (
        <div style={{ marginTop: 24, paddingTop: 20, borderTop: '1px solid #ffffff15' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div>
              <h4 style={{ margin: 0, fontSize: 16, color: '#f8fafc' }}>
                Suggested Bullet Edits ({acceptedCount} of {rewrites.length} Accepted)
              </h4>
              <span style={{ fontSize: 12, color: '#94a3b8' }}>
                Review each suggested rewrite. Accept or reject edits individually before exporting.
              </span>
            </div>

            <button
              onClick={handleExportDOCX}
              disabled={exporting || acceptedCount === 0}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '10px 18px',
                background: acceptedCount > 0 ? '#10b981' : '#ffffff10',
                color: acceptedCount > 0 ? '#022c22' : '#94a3b8',
                border: 'none',
                borderRadius: 8,
                fontWeight: 700,
                fontSize: 13,
                cursor: acceptedCount > 0 && !exporting ? 'pointer' : 'not-allowed',
                transition: 'all 0.15s ease'
              }}
            >
              {exporting ? <RefreshCw className="animate-spin" size={16} /> : <Download size={16} />}
              {exporting ? 'Exporting...' : `Download Tailored Resume (.docx)`}
            </button>
          </div>

          <div>
            {rewrites.map(item => (
              <BulletDiff key={item.id} item={item} onToggleAccept={handleToggleAccept} />
            ))}
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 16 }}>
            <button
              onClick={handleExportDOCX}
              disabled={exporting || acceptedCount === 0}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '12px 22px',
                background: 'linear-gradient(135deg, #10b981, #059669)',
                color: '#ffffff',
                border: 'none',
                borderRadius: 10,
                fontWeight: 700,
                fontSize: 14,
                cursor: acceptedCount > 0 && !exporting ? 'pointer' : 'not-allowed'
              }}
            >
              <Download size={18} /> Download Tailored Resume (.docx)
            </button>
          </div>
        </div>
      )}
    </article>
  );
};
