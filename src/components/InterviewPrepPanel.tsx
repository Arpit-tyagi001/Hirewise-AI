import React, { useState, useEffect } from 'react';
import { Sparkles, Copy, Check, RefreshCw, AlertCircle, ShieldCheck, Target, Layers, HelpCircle, ChevronDown, ChevronUp, Cpu, Award, Zap } from 'lucide-react';
import { generateInterviewPrep } from '../services/api';

interface StarBreakdown {
  situation: string;
  task: string;
  action: string;
  result: string;
}

interface InterviewQuestion {
  id: number | string;
  category: string;
  question: string;
  intent: string;
  star_breakdown?: StarBreakdown;
  talking_points?: string[];
}

interface InterviewPrepData {
  candidate_name?: string;
  job_title?: string;
  company_name?: string;
  summary?: string;
  mode?: string;
  questions: InterviewQuestion[];
}

interface InterviewPrepPanelProps {
  analysisId: number;
  candidateName?: string;
  initialJobDescription?: string;
  token?: string | null;
  savedInterviewPrepData?: any;
}

export const InterviewPrepPanel: React.FC<InterviewPrepPanelProps> = ({
  analysisId,
  candidateName = 'Candidate',
  initialJobDescription = 'We are seeking a Senior Software Engineer proficient in Python, FastAPI, React, TypeScript, and modern distributed systems.',
  token,
  savedInterviewPrepData
}) => {
  const [jobDescription, setJobDescription] = useState(initialJobDescription);
  const [apiKey, setApiKey] = useState(localStorage.getItem('hirewise_groq_key') || '');
  const [showKeyInput, setShowKeyInput] = useState(false);

  const [prepData, setPrepData] = useState<InterviewPrepData | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [activeCategory, setActiveCategory] = useState<string>('ALL');
  const [expandedIds, setExpandedIds] = useState<Record<string, boolean>>({});
  const [copiedId, setCopiedId] = useState<string | number | null>(null);
  const [allCopied, setAllCopied] = useState(false);

  // Hydrate from saved data
  useEffect(() => {
    if (savedInterviewPrepData) {
      const data = savedInterviewPrepData.interview_prep || savedInterviewPrepData;
      if (data && Array.isArray(data.questions)) {
        setPrepData(data);
        // Default expand all
        const exp: Record<string, boolean> = {};
        data.questions.forEach((q: any) => { exp[q.id] = true; });
        setExpandedIds(exp);
      }
    }
  }, [savedInterviewPrepData]);

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
      const res = await generateInterviewPrep(analysisId, jobDescription, apiKey.trim() || undefined);
      const data: InterviewPrepData = res.interview_prep;
      setPrepData(data);

      const exp: Record<string, boolean> = {};
      (data.questions || []).forEach(q => { exp[q.id] = true; });
      setExpandedIds(exp);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || 'Failed to generate interview preparation.');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (id: string | number) => {
    setExpandedIds(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const handleCopyQuestion = async (q: InterviewQuestion) => {
    let text = `QUESTION (${q.category}):\n${q.question}\n\n`;
    text += `INTERVIEWER INTENT:\n${q.intent}\n\n`;
    if (q.star_breakdown) {
      text += `STAR FRAMEWORK:\n`;
      text += `• Situation: ${q.star_breakdown.situation}\n`;
      text += `• Task: ${q.star_breakdown.task}\n`;
      text += `• Action: ${q.star_breakdown.action}\n`;
      text += `• Result: ${q.star_breakdown.result}\n\n`;
    }
    if (q.talking_points && q.talking_points.length > 0) {
      text += `KEY TALKING POINTS: ${q.talking_points.join(', ')}\n`;
    }

    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(q.id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      setErrorMsg('Failed to copy to clipboard.');
    }
  };

  const handleCopyAll = async () => {
    if (!prepData || !prepData.questions) return;
    let text = `=== AI INTERVIEW PREPARATION GUIDE ===\n`;
    text += `Candidate: ${prepData.candidate_name || candidateName}\n`;
    text += `Target Role: ${prepData.job_title || 'Software Engineer'}\n`;
    if (prepData.summary) text += `Strategy Summary: ${prepData.summary}\n\n`;
    text += `------------------------------------------------------------\n\n`;

    prepData.questions.forEach((q, idx) => {
      text += `[#${idx + 1}] CATEGORY: ${q.category}\n`;
      text += `QUESTION: ${q.question}\n`;
      text += `EVALUATION INTENT: ${q.intent}\n`;
      if (q.star_breakdown) {
        text += `STAR BREAKDOWN:\n`;
        text += `  - Situation: ${q.star_breakdown.situation}\n`;
        text += `  - Task:      ${q.star_breakdown.task}\n`;
        text += `  - Action:    ${q.star_breakdown.action}\n`;
        text += `  - Result:    ${q.star_breakdown.result}\n`;
      }
      if (q.talking_points && q.talking_points.length > 0) {
        text += `KEY POINTS: ${q.talking_points.join(', ')}\n`;
      }
      text += `\n------------------------------------------------------------\n\n`;
    });

    try {
      await navigator.clipboard.writeText(text);
      setAllCopied(true);
      setTimeout(() => setAllCopied(false), 2000);
    } catch {
      setErrorMsg('Failed to copy all questions.');
    }
  };

  const questions = prepData?.questions || [];
  const filteredQuestions = activeCategory === 'ALL'
    ? questions
    : questions.filter(q => q.category === activeCategory);

  const categories = ['ALL', 'Technical Architecture', 'Skill Gap Strategy', 'Behavioral STAR'];

  const getCategoryBadgeStyle = (cat: string) => {
    switch (cat) {
      case 'Technical Architecture':
        return { bg: '#3b82f620', border: '#3b82f640', color: '#60a5fa', icon: <Cpu size={12} /> };
      case 'Skill Gap Strategy':
        return { bg: '#f59e0b20', border: '#f59e0b40', color: '#fbbf24', icon: <Zap size={12} /> };
      case 'Behavioral STAR':
        return { bg: '#8b5cf620', border: '#8b5cf640', color: '#c084fc', icon: <Award size={12} /> };
      default:
        return { bg: '#ffffff10', border: '#ffffff20', color: '#94a3b8', icon: <HelpCircle size={12} /> };
    }
  };

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
            <Target size={14} /> AI Interview Preparation Suite
          </span>
          <h3 style={{ fontSize: 20, margin: '4px 0', color: '#f8fafc' }}>Technical & STAR Interview Simulator</h3>
          <p style={{ margin: 0, fontSize: 13, color: '#94a3b8' }}>
            Predicts probable interview questions based on JD gaps and generates candidate-tailored STAR talking frameworks.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: '#8b5cf615', border: '1px solid #8b5cf640', padding: '6px 14px', borderRadius: 20, color: '#c084fc', fontSize: 12, fontWeight: 600 }}>
          <Layers size={16} />
          <span>STAR Method Framework</span>
        </div>
      </header>

      {errorMsg && (
        <div style={{ background: '#ef444415', border: '1px solid #ef444455', color: '#fca5a5', padding: '10px 14px', borderRadius: 8, fontSize: 12, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <AlertCircle size={16} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Target Job Description Area */}
      <div style={{ marginBottom: 20 }}>
        <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#cbd5e1', marginBottom: 6 }}>
          Target Job Description (JD)
        </label>
        <textarea
          style={{ width: '100%', minHeight: 90, background: '#060b18', border: '1px solid #ffffff18', borderRadius: 10, padding: 12, color: '#f8fafc', fontSize: 12, lineHeight: 1.5 }}
          value={jobDescription}
          onChange={e => setJobDescription(e.target.value)}
          placeholder="Paste Job Description here to formulate custom interview questions..."
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
            {loading ? 'Synthesizing Interview Prep...' : 'Generate AI Interview Prep'}
          </button>
        </div>

        {/* API Key Banner */}
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

      {/* Generated Questions List */}
      {prepData && questions.length > 0 && (
        <div style={{ marginTop: 24, paddingTop: 20, borderTop: '1px solid #ffffff15' }}>
          {/* Strategy Summary Banner */}
          {prepData.summary && (
            <div
              style={{
                background: '#1e1b4b30',
                border: '1px solid #6366f140',
                borderRadius: 12,
                padding: '14px 18px',
                marginBottom: 20,
                display: 'flex',
                alignItems: 'flex-start',
                gap: 12
              }}
            >
              <Target size={20} style={{ color: '#818cf8', flexShrink: 0, marginTop: 2 }} />
              <div>
                <strong style={{ display: 'block', color: '#c7d2fe', fontSize: 13, marginBottom: 4 }}>
                  Target Role Strategy Brief
                </strong>
                <p style={{ margin: 0, fontSize: 13, color: '#e0e7ff', lineHeight: 1.5 }}>
                  {prepData.summary}
                </p>
              </div>
            </div>
          )}

          {/* Category Filter Bar & Export Actions */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 18, flexWrap: 'wrap', gap: 12 }}>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {categories.map(cat => {
                const count = cat === 'ALL'
                  ? questions.length
                  : questions.filter(q => q.category === cat).length;
                const isSelected = activeCategory === cat;
                return (
                  <button
                    key={cat}
                    onClick={() => setActiveCategory(cat)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                      padding: '6px 12px',
                      borderRadius: 20,
                      fontSize: 12,
                      fontWeight: 600,
                      cursor: 'pointer',
                      background: isSelected ? '#3b82f6' : '#ffffff0c',
                      color: isSelected ? '#ffffff' : '#94a3b8',
                      border: isSelected ? '1px solid #60a5fa' : '1px solid #ffffff15',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <span>{cat}</span>
                    <span style={{ fontSize: 10, background: isSelected ? '#1d4ed8' : '#ffffff15', padding: '1px 6px', borderRadius: 10 }}>
                      {count}
                    </span>
                  </button>
                );
              })}
            </div>

            <button
              onClick={handleCopyAll}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '8px 14px',
                background: allCopied ? '#10b981' : '#ffffff10',
                color: allCopied ? '#022c22' : '#f8fafc',
                border: '1px solid #ffffff20',
                borderRadius: 8,
                fontSize: 12,
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              {allCopied ? <Check size={14} /> : <Copy size={14} />}
              {allCopied ? 'All Copied to Clipboard!' : 'Copy Entire Prep Sheet'}
            </button>
          </div>

          {/* Question Cards */}
          <div style={{ display: 'grid', gap: 16 }}>
            {filteredQuestions.map((q, idx) => {
              const isExpanded = expandedIds[q.id] ?? true;
              const catStyle = getCategoryBadgeStyle(q.category);
              const isCopied = copiedId === q.id;

              return (
                <div
                  key={q.id || idx}
                  style={{
                    background: '#0a1022',
                    border: '1px solid #1e293b',
                    borderRadius: 12,
                    padding: 18,
                    transition: 'border-color 0.15s ease'
                  }}
                >
                  {/* Card Top: Category, Number, Copy, Toggle */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                      <span
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 4,
                          fontSize: 11,
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          padding: '3px 9px',
                          borderRadius: 6,
                          background: catStyle.bg,
                          border: `1px solid ${catStyle.border}`,
                          color: catStyle.color
                        }}
                      >
                        {catStyle.icon} {q.category}
                      </span>
                      <span style={{ fontSize: 11, color: '#64748b', fontWeight: 600 }}>Question #{idx + 1}</span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <button
                        onClick={() => handleCopyQuestion(q)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 4,
                          padding: '4px 8px',
                          borderRadius: 6,
                          background: isCopied ? '#10b981' : '#ffffff0c',
                          color: isCopied ? '#022c22' : '#cbd5e1',
                          border: '1px solid #ffffff15',
                          fontSize: 11,
                          cursor: 'pointer'
                        }}
                      >
                        {isCopied ? <Check size={12} /> : <Copy size={12} />}
                        {isCopied ? 'Copied' : 'Copy'}
                      </button>

                      <button
                        onClick={() => toggleExpand(q.id)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          padding: 4,
                          borderRadius: 6,
                          background: '#ffffff0c',
                          color: '#94a3b8',
                          border: 'none',
                          cursor: 'pointer'
                        }}
                      >
                        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      </button>
                    </div>
                  </div>

                  {/* Question Title */}
                  <h4 style={{ margin: '12px 0 8px 0', fontSize: 15, color: '#f8fafc', fontWeight: 600, lineHeight: 1.4 }}>
                    {q.question}
                  </h4>

                  {/* Interviewer Intent Box */}
                  <div
                    style={{
                      background: '#1e293b40',
                      borderLeft: '3px solid #60a5fa',
                      borderRadius: '0 8px 8px 0',
                      padding: '8px 12px',
                      marginBottom: 12
                    }}
                  >
                    <span style={{ fontSize: 11, color: '#93c5fd', fontWeight: 700, display: 'block', marginBottom: 2 }}>
                      🎯 INTERVIEWER INTENT / EVALUATION ANGLE
                    </span>
                    <span style={{ fontSize: 12, color: '#cbd5e1', lineHeight: 1.4 }}>
                      {q.intent}
                    </span>
                  </div>

                  {/* Expandable STAR Framework Details */}
                  {isExpanded && (
                    <div style={{ marginTop: 12 }}>
                      {q.star_breakdown && (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 10, marginTop: 8 }}>
                          <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, padding: 10 }}>
                            <span style={{ fontSize: 11, color: '#38bdf8', fontWeight: 700, display: 'block', marginBottom: 4 }}>
                              S • SITUATION
                            </span>
                            <span style={{ fontSize: 12, color: '#94a3b8', lineHeight: 1.4 }}>
                              {q.star_breakdown.situation}
                            </span>
                          </div>

                          <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, padding: 10 }}>
                            <span style={{ fontSize: 11, color: '#fbbf24', fontWeight: 700, display: 'block', marginBottom: 4 }}>
                              T • TASK
                            </span>
                            <span style={{ fontSize: 12, color: '#94a3b8', lineHeight: 1.4 }}>
                              {q.star_breakdown.task}
                            </span>
                          </div>

                          <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, padding: 10 }}>
                            <span style={{ fontSize: 11, color: '#a78bfa', fontWeight: 700, display: 'block', marginBottom: 4 }}>
                              A • ACTION
                            </span>
                            <span style={{ fontSize: 12, color: '#94a3b8', lineHeight: 1.4 }}>
                              {q.star_breakdown.action}
                            </span>
                          </div>

                          <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, padding: 10 }}>
                            <span style={{ fontSize: 11, color: '#4ade80', fontWeight: 700, display: 'block', marginBottom: 4 }}>
                              R • RESULT
                            </span>
                            <span style={{ fontSize: 12, color: '#94a3b8', lineHeight: 1.4 }}>
                              {q.star_breakdown.result}
                            </span>
                          </div>
                        </div>
                      )}

                      {/* Key Talking Points */}
                      {q.talking_points && q.talking_points.length > 0 && (
                        <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                          <span style={{ fontSize: 11, color: '#64748b', fontWeight: 600 }}>Key Talking Points:</span>
                          {q.talking_points.map((pt, pIdx) => (
                            <span
                              key={pIdx}
                              style={{
                                fontSize: 11,
                                background: '#1e293b',
                                color: '#e2e8f0',
                                border: '1px solid #334155',
                                padding: '2px 8px',
                                borderRadius: 12
                              }}
                            >
                              {pt}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </article>
  );
};