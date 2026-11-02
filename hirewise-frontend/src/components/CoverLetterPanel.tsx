import React, { useState, useEffect } from 'react';
import { Sparkles, Download, Copy, Check, RefreshCw, FileText, Building2, Briefcase, AlertCircle, ShieldCheck, Sliders } from 'lucide-react';
import { generateCoverLetter, exportCoverLetter } from '../services/api';

interface CoverLetterPanelProps {
  analysisId: number;
  candidateName?: string;
  initialJobDescription?: string;
  token?: string | null;
  savedCoverLetterData?: any;
}

export const CoverLetterPanel: React.FC<CoverLetterPanelProps> = ({
  analysisId,
  candidateName = 'Candidate',
  initialJobDescription = 'We are seeking a Senior Software Engineer proficient in Python, FastAPI, React, TypeScript, and modern distributed systems.',
  token,
  savedCoverLetterData
}) => {
  const [jobDescription, setJobDescription] = useState(initialJobDescription);
  const [companyName, setCompanyName] = useState('Acme Corporation');
  const [jobTitle, setJobTitle] = useState('Senior Software Engineer');
  const [tone, setTone] = useState<'professional' | 'confident' | 'technical'>('professional');
  const [apiKey, setApiKey] = useState(localStorage.getItem('hirewise_groq_key') || '');
  const [showKeyInput, setShowKeyInput] = useState(false);

  const [coverLetterText, setCoverLetterText] = useState<string>('');
  const [coverLetterMeta, setCoverLetterMeta] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [copied, setCopied] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Hydrate from saved data if present
  useEffect(() => {
    if (savedCoverLetterData) {
      setCoverLetterMeta(savedCoverLetterData);
      if (savedCoverLetterData.cover_letter) {
        setCoverLetterText(savedCoverLetterData.cover_letter);
      } else if (Array.isArray(savedCoverLetterData.paragraphs)) {
        setCoverLetterText(savedCoverLetterData.paragraphs.join('\n\n'));
      }
      if (savedCoverLetterData.company_name) setCompanyName(savedCoverLetterData.company_name);
      if (savedCoverLetterData.job_title) setJobTitle(savedCoverLetterData.job_title);
      if (savedCoverLetterData.tone) setTone(savedCoverLetterData.tone);
    }
  }, [savedCoverLetterData]);

  const handleApiKeyChange = (val: string) => {
    setApiKey(val);
    if (val.trim()) {
      localStorage.setItem('hirewise_groq_key', val.trim());
    } else {
      localStorage.removeItem('hirewise_groq_key');
    }
  };

  const handleGenerate = async () => {
    if (!jobDescription.trim()) {
      setErrorMsg('Please provide a target job description.');
      return;
    }

    setLoading(true);
    setErrorMsg('');

    try {
      const data = await generateCoverLetter(
        analysisId,
        jobDescription,
        companyName.trim() || undefined,
        jobTitle.trim() || undefined,
        tone,
        apiKey.trim() || undefined
      );

      const cl = data.cover_letter;
      setCoverLetterMeta(cl);
      if (cl.cover_letter) {
        setCoverLetterText(cl.cover_letter);
      } else if (Array.isArray(cl.paragraphs)) {
        setCoverLetterText(cl.paragraphs.join('\n\n'));
      }
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || 'Failed to generate cover letter.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!coverLetterText) return;
    try {
      await navigator.clipboard.writeText(coverLetterText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setErrorMsg('Failed to copy text to clipboard.');
    }
  };

  const handleExportDOCX = async () => {
    if (!coverLetterText.trim()) return;
    setExporting(true);
    try {
      const blob = await exportCoverLetter(analysisId, coverLetterText, companyName, jobTitle);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const safeName = (candidateName || 'Candidate').replace(/\s+/g, '_');
      a.download = `Cover_Letter_${safeName}_${analysisId}.docx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error(err);
      setErrorMsg('Failed to export Cover Letter DOCX.');
    } finally {
      setExporting(false);
    }
  };

  const wordCount = coverLetterText.trim() ? coverLetterText.trim().split(/\s+/).length : 0;
  const readingTime = Math.max(1, Math.ceil(wordCount / 200));

  return (
    <article
      className="panel"
      style={{
        border: '1px solid #3b82f655',
        background: 'linear-gradient(145deg, #091326, #050b18)',
        borderRadius: 16,
        padding: 24
      }}
    >
      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <span className="eyebrow" style={{ color: '#60a5fa', display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            <FileText size={14} /> Tailored Cover Letter Generator
          </span>
          <h3 style={{ fontSize: 20, margin: '4px 0', color: '#f8fafc' }}>Hiring Manager Ready Cover Letter</h3>
          <p style={{ margin: 0, fontSize: 13, color: '#94a3b8' }}>
            Crafts a compelling, targeted letter mapping your verified achievements to employer needs with zero hallucinations.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#10b98115', border: '1px solid #10b98140', padding: '6px 14px', borderRadius: 20, color: '#4ade80', fontSize: 12, fontWeight: 600 }}>
          <ShieldCheck size={16} />
          <span>Resume-Grounded Facts Only</span>
        </div>
      </header>

      {errorMsg && (
        <div style={{ background: '#ef444415', border: '1px solid #ef444455', color: '#fca5a5', padding: '10px 14px', borderRadius: 8, fontSize: 12, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <AlertCircle size={16} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Target Role & Configuration Controls */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 16 }}>
        <div>
          <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#cbd5e1', marginBottom: 6 }}>
            <Building2 size={13} style={{ display: 'inline', marginRight: 4, verticalAlign: '-1px' }} />
            Target Company
          </label>
          <input
            type="text"
            value={companyName}
            onChange={e => setCompanyName(e.target.value)}
            placeholder="e.g. Acme Corporation"
            style={{ width: '100%', background: '#060b18', border: '1px solid #ffffff18', borderRadius: 8, padding: '9px 12px', color: '#f8fafc', fontSize: 13 }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#cbd5e1', marginBottom: 6 }}>
            <Briefcase size={13} style={{ display: 'inline', marginRight: 4, verticalAlign: '-1px' }} />
            Target Job Title
          </label>
          <input
            type="text"
            value={jobTitle}
            onChange={e => setJobTitle(e.target.value)}
            placeholder="e.g. Senior Software Engineer"
            style={{ width: '100%', background: '#060b18', border: '1px solid #ffffff18', borderRadius: 8, padding: '9px 12px', color: '#f8fafc', fontSize: 13 }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#cbd5e1', marginBottom: 6 }}>
            <Sliders size={13} style={{ display: 'inline', marginRight: 4, verticalAlign: '-1px' }} />
            Tone of Voice
          </label>
          <select
            value={tone}
            onChange={e => setTone(e.target.value as any)}
            style={{ width: '100%', background: '#060b18', border: '1px solid #ffffff18', borderRadius: 8, padding: '9px 12px', color: '#f8fafc', fontSize: 13 }}
          >
            <option value="professional">Professional & Polished</option>
            <option value="confident">High-Impact & Confident</option>
            <option value="technical">Engineering & Technical</option>
          </select>
        </div>
      </div>

      {/* Target Job Description */}
      <div style={{ marginBottom: 16 }}>
        <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#cbd5e1', marginBottom: 6 }}>
          Target Job Description (JD)
        </label>
        <textarea
          style={{ width: '100%', minHeight: 90, background: '#060b18', border: '1px solid #ffffff18', borderRadius: 10, padding: 12, color: '#f8fafc', fontSize: 12, lineHeight: 1.5 }}
          value={jobDescription}
          onChange={e => setJobDescription(e.target.value)}
          placeholder="Paste Job Description here..."
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 10 }}>
          <span style={{ fontSize: 11, color: '#64748b' }}>{jobDescription.length} characters</span>
          <button
            onClick={handleGenerate}
            disabled={loading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '10px 20px',
              background: 'linear-gradient(135deg, #2563eb, #3b82f6)',
              color: '#ffffff',
              border: 'none',
              borderRadius: 8,
              fontWeight: 600,
              fontSize: 13,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
              boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)'
            }}
          >
            {loading ? <RefreshCw className="animate-spin" size={16} /> : <Sparkles size={16} />}
            {loading ? 'Synthesizing Cover Letter...' : 'Generate Tailored Cover Letter'}
          </button>
        </div>

        {/* API Key Toggle Banner */}
        <div style={{ marginTop: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 12px', background: '#ffffff04', borderRadius: 8, border: '1px solid #ffffff0a' }}>
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

      {/* Output / Document Area */}
      {coverLetterText && (
        <div style={{ marginTop: 24, paddingTop: 20, borderTop: '1px solid #ffffff15' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14, flexWrap: 'wrap', gap: 10 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <h4 style={{ margin: 0, fontSize: 16, color: '#f8fafc' }}>Generated Cover Letter</h4>
              <span style={{ fontSize: 11, background: '#3b82f620', color: '#93c5fd', border: '1px solid #3b82f640', padding: '2px 8px', borderRadius: 12 }}>
                {wordCount} words • ~{readingTime} min read
              </span>
              {coverLetterMeta?.mode && (
                <span style={{ fontSize: 11, background: '#10b98120', color: '#86efac', border: '1px solid #10b98140', padding: '2px 8px', borderRadius: 12 }}>
                  Engine: {coverLetterMeta.mode.toUpperCase()}
                </span>
              )}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <button
                onClick={handleCopy}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '8px 14px',
                  background: copied ? '#10b981' : '#ffffff12',
                  color: copied ? '#022c22' : '#f8fafc',
                  border: '1px solid #ffffff20',
                  borderRadius: 8,
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                {copied ? <Check size={14} /> : <Copy size={14} />}
                {copied ? 'Copied to Clipboard!' : 'Copy Text'}
              </button>

              <button
                onClick={handleExportDOCX}
                disabled={exporting}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '8px 16px',
                  background: 'linear-gradient(135deg, #10b981, #059669)',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: 8,
                  fontSize: 12,
                  fontWeight: 700,
                  cursor: exporting ? 'not-allowed' : 'pointer',
                  boxShadow: '0 2px 8px rgba(16, 185, 129, 0.25)'
                }}
              >
                {exporting ? <RefreshCw className="animate-spin" size={14} /> : <Download size={14} />}
                {exporting ? 'Exporting...' : 'Download DOCX'}
              </button>
            </div>
          </div>

          <div
            style={{
              background: '#0b1329',
              border: '1px solid #1e293b',
              borderRadius: 12,
              padding: 24,
              boxShadow: 'inset 0 2px 8px rgba(0, 0, 0, 0.4)'
            }}
          >
            <div style={{ fontSize: 11, color: '#64748b', marginBottom: 12, display: 'flex', justifyContent: 'space-between' }}>
              <span>EDITABLE DOCUMENT PREVIEW</span>
              <span>Changes made below will be preserved in DOCX export</span>
            </div>
            <textarea
              value={coverLetterText}
              onChange={e => setCoverLetterText(e.target.value)}
              style={{
                width: '100%',
                minHeight: 340,
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: '#e2e8f0',
                fontSize: 14,
                lineHeight: 1.8,
                fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
                resize: 'vertical'
              }}
            />
          </div>
        </div>
      )}
    </article>
  );
};