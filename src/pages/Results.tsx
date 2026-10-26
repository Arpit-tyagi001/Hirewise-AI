import React from 'react';
import { AlertCircle, Check, ChevronRight, FileText, Sparkles, X } from 'lucide-react';
import { AppShell } from '../components/AppShell';
import { Button } from '../components/Button';
import { ScoreGauge } from '../components/ScoreGauge';
import { RewriterPanel } from '../components/RewriterPanel';
import { Page } from '../components/Navbar';
import { AnalysisRecord, User } from '../services/api';

interface ResultsProps {
  go: (p: Page) => void;
  analysis: AnalysisRecord | null;
  currentUser: User | null;
}

export function Results({ go, analysis, currentUser }: ResultsProps) {
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

      {/* Breakdown Cards Grid */}
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

        {jdMatch && (
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
        )}
      </div>

      {/* JD-Aware Resume Rewriter Component */}
      <section style={{ marginTop: 24 }}>
        <RewriterPanel analysisId={analysis.id} token={localStorage.getItem('hirewise_token')} />
      </section>
    </AppShell>
  );
}
