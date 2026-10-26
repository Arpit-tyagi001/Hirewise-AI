import React, { useState } from 'react';
import { AlertCircle, Check, ChevronRight, FileText, Sparkles, X, BarChart3, Target, Layers, FileCheck } from 'lucide-react';
import { AppShell } from '../components/AppShell';
import { Button } from '../components/Button';
import { ScoreGauge } from '../components/ScoreGauge';
import { RewriterPanel } from '../components/RewriterPanel';
import { CoverLetterPanel } from '../components/CoverLetterPanel';
import { InterviewPrepPanel } from '../components/InterviewPrepPanel';
import { Page } from '../components/Navbar';
import { AnalysisRecord, User } from '../services/api';

interface ResultsProps {
  go: (p: Page) => void;
  analysis: AnalysisRecord | null;
  currentUser: User | null;
}

type TabKey = 'breakdown' | 'rewriter' | 'cover_letter' | 'interview_prep';

export function Results({ go, analysis, currentUser }: ResultsProps) {
  const [activeTab, setActiveTab] = useState<TabKey>('breakdown');

  if (!analysis) {
    return (
      <AppShell go={go} active="Overview" currentUser={currentUser} onOpenAuthModal={() => {}} onLogout={() => {}}>
        <div style={{ padding: 40, textAlign: 'center' }}>
          <AlertCircle size={32} style={{ color: '#f87171', margin: '0 auto 10px' }} />
          <h3>No Resume Analysis Selected</h3>
          <p style={{ color: '#94a3b8' }}>Please upload a resume or select a saved record from history.</p>
          <Button onClick={() => go('upload')} style={{ marginTop: 16 }}>
            Upload Resume
          </Button>
        </div>
      </AppShell>
    );
  }

  const parsed = analysis.parsed_data || {};
  const jdMatch = analysis.jd_match_data;

  const tabs: Array<{ id: TabKey; label: string; icon: React.ReactNode; badge?: string }> = [
    { id: 'breakdown', label: 'ATS & JD Gap Analysis', icon: <BarChart3 size={15} /> },
    { id: 'rewriter', label: 'AI Bullet Rewriter', icon: <Sparkles size={15} /> },
    { id: 'cover_letter', label: 'Cover Letter Generator', icon: <FileCheck size={15} />, badge: analysis.cover_letter_data ? 'Saved' : undefined },
    { id: 'interview_prep', label: 'AI Interview Prep Suite', icon: <Target size={15} />, badge: analysis.interview_prep_data ? 'Ready' : undefined }
  ];

  return (
    <AppShell go={go} active="Overview" currentUser={currentUser} onOpenAuthModal={() => {}} onLogout={() => {}}>
      <div className="crumb">
        Workspace <ChevronRight size={13} /> Evaluation Report <ChevronRight size={13} /> {analysis.candidate_name || 'Candidate'}
      </div>

      <header className="resultsHead">
        <div>
          <span className="eyebrow">
            <Sparkles size={14} /> Evaluation Report #{analysis.id}
          </span>
          <h2>{analysis.candidate_name || 'Candidate Evaluation'}</h2>
          <p>{analysis.file_name} • Extracted Skills: {parsed.skills?.length || 0}</p>
        </div>
        <div className="headActions">
          <Button kind="ghost" onClick={() => go('history')}>
            View History
          </Button>
          <Button onClick={() => go('upload')}>
            New Analysis <ChevronRight size={16} />
          </Button>
        </div>
      </header>

      {/* Top Scores Overview */}
      <section className="scoreWrap">
        <ScoreGauge value={analysis.ats_score} label="ATS Score" />
        <div className="overallMeta">
          <div>
            <span>ATS Assessment</span>
            <strong>{analysis.ats_level} Match</strong>
          </div>
          <div>
            <span>Contact Email</span>
            <strong>{analysis.candidate_email || 'Not Specified'}</strong>
          </div>
          <div>
            <span>File Format</span>
            <strong>{analysis.file_type?.toUpperCase() || 'DOCUMENT'}</strong>
          </div>
          <div>
            <span>Parsed Skills</span>
            <strong>{parsed.skills?.length || 0} Skills Verified</strong>
          </div>
        </div>
      </section>

      {/* Modern Tab Navigation Bar */}
      <div
        style={{
          display: 'flex',
          gap: 8,
          marginTop: 28,
          marginBottom: 20,
          borderBottom: '1px solid #1e293b',
          paddingBottom: 12,
          overflowX: 'auto'
        }}
      >
        {tabs.map(t => {
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '9px 16px',
                borderRadius: 10,
                fontSize: 13,
                fontWeight: isActive ? 700 : 500,
                cursor: 'pointer',
                background: isActive ? 'linear-gradient(135deg, #1e3a8a, #2563eb)' : '#0b1329',
                color: isActive ? '#ffffff' : '#94a3b8',
                border: isActive ? '1px solid #60a5fa' : '1px solid #1e293b',
                boxShadow: isActive ? '0 4px 14px rgba(37, 99, 235, 0.25)' : 'none',
                transition: 'all 0.15s ease',
                whiteSpace: 'nowrap'
              }}
            >
              {t.icon}
              <span>{t.label}</span>
              {t.badge && (
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 700,
                    padding: '1px 6px',
                    borderRadius: 8,
                    background: isActive ? '#ffffff25' : '#10b98125',
                    color: isActive ? '#ffffff' : '#86efac',
                    border: `1px solid ${isActive ? '#ffffff40' : '#10b98140'}`
                  }}
                >
                  {t.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab 1: ATS & JD Gap Analysis */}
      {activeTab === 'breakdown' && (
        <div className="scoreColumns">
          <section className="panel">
            <header>
              <h3>10-Dimension Score Breakdown</h3>
              <p>Objective category breakdown</p>
            </header>
            <div className="breakdownList">
              {Object.entries(analysis.section_scores || {}).map(([key, val]: any) => (
                <div key={key} className="breakRow">
                  <span>{key.replace(/_/g, ' ')}</span>
                  <div className="bar">
                    <div className="fill" style={{ width: `${(val.score / val.max) * 100}%` }} />
                  </div>
                  <b>{val.score} / {val.max}</b>
                </div>
              ))}
            </div>
          </section>

          {jdMatch ? (
            <section className="panel">
              <header>
                <h3>Job Description Gap Analysis</h3>
                <p>TF-IDF & Skill Overlap Engine</p>
              </header>
              <div style={{ padding: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                  <span>Overall Skill Alignment</span>
                  <b style={{ color: '#60a5fa' }}>{((jdMatch.match_percentage ?? jdMatch.match_score) || 0).toFixed(1)}%</b>
                </div>
                <div style={{ display: 'grid', gap: 10 }}>
                  <div>
                    <span style={{ fontSize: 12, color: '#86efac', fontWeight: 600 }}>Matched Skills ({jdMatch.matching_skills?.length || 0})</span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 6 }}>
                      {(jdMatch.matching_skills || []).map((sk: string) => (
                        <span key={sk} style={{ fontSize: 11, background: '#10b98120', color: '#86efac', border: '1px solid #10b98140', padding: '2px 8px', borderRadius: 4 }}>
                          <Check size={10} style={{ display: 'inline', marginRight: 4 }} />{sk}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div style={{ marginTop: 8 }}>
                    <span style={{ fontSize: 12, color: '#fca5a5', fontWeight: 600 }}>Missing JD Skills ({jdMatch.missing_skills?.length || 0})</span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 6 }}>
                      {(jdMatch.missing_skills || []).map((sk: string) => (
                        <span key={sk} style={{ fontSize: 11, background: '#ef444420', color: '#fca5a5', border: '1px solid #ef444440', padding: '2px 8px', borderRadius: 4 }}>
                          <X size={10} style={{ display: 'inline', marginRight: 4 }} />{sk}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </section>
          ) : (
            <section className="panel">
              <header>
                <h3>Job Description Matching</h3>
                <p>Align candidate profile with specific role criteria</p>
              </header>
              <div style={{ padding: 20, textAlign: 'center', color: '#94a3b8' }}>
                <p style={{ fontSize: 13, marginBottom: 16 }}>
                  No target job description has been matched yet. Switch to the <strong>AI Bullet Rewriter</strong>, <strong>Cover Letter</strong>, or <strong>Interview Prep</strong> tabs to target a job description!
                </p>
                <Button onClick={() => setActiveTab('rewriter')}>
                  Open Bullet Rewriter <ChevronRight size={14} />
                </Button>
              </div>
            </section>
          )}
        </div>
      )}

      {/* Tab 2: AI Bullet Rewriter */}
      {activeTab === 'rewriter' && (
        <section>
          <RewriterPanel analysisId={analysis.id} token={localStorage.getItem('hirewise_token')} />
        </section>
      )}

      {/* Tab 3: Cover Letter Generator */}
      {activeTab === 'cover_letter' && (
        <section>
          <CoverLetterPanel
            analysisId={analysis.id}
            candidateName={analysis.candidate_name}
            token={localStorage.getItem('hirewise_token')}
            savedCoverLetterData={analysis.cover_letter_data}
          />
        </section>
      )}

      {/* Tab 4: AI Interview Prep Suite */}
      {activeTab === 'interview_prep' && (
        <section>
          <InterviewPrepPanel
            analysisId={analysis.id}
            candidateName={analysis.candidate_name}
            token={localStorage.getItem('hirewise_token')}
            savedInterviewPrepData={analysis.interview_prep_data}
          />
        </section>
      )}
    </AppShell>
  );
}