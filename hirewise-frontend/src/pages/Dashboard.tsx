import React, { useEffect, useState } from 'react';
import { AlertCircle, BarChart3, BriefcaseBusiness, ChevronRight, FileText, Plus, RefreshCw, Sparkles, Users } from 'lucide-react';
import { AppShell } from '../components/AppShell';
import { Button } from '../components/Button';
import { Metric } from '../components/Metric';
import { DashboardSkeleton } from '../components/LoadingSkeleton';
import { Page } from '../components/Navbar';
import { AnalysisRecord, fetchHistory, User } from '../services/api';

interface DashboardProps {
  go: (p: Page) => void;
  onSelectAnalysis: (a: AnalysisRecord) => void;
  currentUser: User | null;
  onOpenAuthModal: () => void;
}

export function Dashboard({ go, onSelectAnalysis, currentUser, onOpenAuthModal }: DashboardProps) {
  const [history, setHistory] = useState<AnalysisRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  const loadData = async () => {
    if (!currentUser) {
      setLoading(false);
      setHistory([]);
      return;
    }
    setLoading(true);
    setErrorMsg('');
    try {
      const records = await fetchHistory();
      setHistory(records);
    } catch (err: any) {
      console.error('Failed to fetch dashboard data:', err);
      setErrorMsg(err.message || 'Could not load analysis records from backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [currentUser]);

  // Compute real aggregated values from user's actual history
  const totalAnalyses = history.length;
  const avgScore = totalAnalyses > 0
    ? (history.reduce((acc, curr) => acc + curr.ats_score, 0) / totalAnalyses).toFixed(1)
    : '0.0';
  const topMatches = history.filter(h => h.ats_score >= 80).length;

  // Real Score Distribution Breakdown (Low: <60, Mid: 60-79, High: >=80)
  const lowCount = history.filter(h => h.ats_score < 60).length;
  const midCount = history.filter(h => h.ats_score >= 60 && h.ats_score < 80).length;
  const highCount = history.filter(h => h.ats_score >= 80).length;

  return (
    <AppShell go={go} active="Overview" currentUser={currentUser} recordsCount={totalAnalyses} onOpenAuthModal={onOpenAuthModal} onLogout={() => {}}>
      <div className="pageIntro">
        <div>
          <span className="eyebrow">
            <Sparkles size={14} /> AI Talent Analytics
          </span>
          <h2>{currentUser ? `${currentUser.full_name}'s Dashboard` : 'Talent Dashboard'} <span>✦</span></h2>
          <p>{currentUser ? 'Real-time telemetry computed from your saved resume analyses' : 'Sign in to access your saved resume evaluations and history'}</p>
        </div>
        <Button onClick={() => go('upload')}>
          <Plus size={16} /> New Analysis
        </Button>
      </div>

      {errorMsg && (
        <div style={{ background: '#ef444415', border: '1px solid #ef444455', color: '#fca5a5', padding: '14px 18px', borderRadius: 10, marginBottom: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
          <Button kind="ghost" onClick={loadData} style={{ fontSize: 12, padding: '4px 10px' }}>
            <RefreshCw size={14} /> Retry
          </Button>
        </div>
      )}

      {loading ? (
        <DashboardSkeleton />
      ) : (
        <>
          {/* Real Computed Metrics */}
          <div className="metricGrid">
            <Metric label="User Resumes Saved" value={totalAnalyses.toString()} delta={currentUser ? 'Verified in DB' : 'Sign in to save'} icon={FileText} />
            <Metric label="Average ATS Score" value={avgScore} delta="Out of 100" icon={BarChart3} />
            <Metric label="Top Candidate Matches" value={topMatches.toString()} delta="ATS Score ≥ 80%" icon={Sparkles} />
            <Metric label="Authentication State" value={currentUser ? 'Authenticated' : 'Demo Mode'} delta={currentUser ? currentUser.email : 'Click to Sign In'} icon={BriefcaseBusiness} />
          </div>

          {!currentUser && (
            <div style={{ background: '#2563eb15', border: '1px solid #2563eb40', padding: '16px 20px', borderRadius: 12, marginTop: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <strong style={{ color: '#93c5fd', display: 'block' }}>Operating in Anonymous Demo Mode</strong>
                <span style={{ fontSize: 12, color: '#94a3b8' }}>Sign in or create an account to save your resume evaluations and access history across devices.</span>
              </div>
              <Button onClick={onOpenAuthModal} style={{ padding: '8px 16px', fontSize: 12 }}>
                Sign In / Register
              </Button>
            </div>
          )}

          {/* Real Score Distribution Breakdown & Low Data State */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 20, marginTop: 24 }}>
            <section className="panel" style={{ padding: 24 }}>
              <header style={{ marginBottom: 16 }}>
                <h3>ATS Candidate Score Distribution</h3>
                <p>Computed live from your analyzed resume records</p>
              </header>

              {totalAnalyses === 0 ? (
                <div style={{ padding: '30px 20px', textAlign: 'center', background: '#ffffff03', borderRadius: 12, border: '1px dashed #ffffff15' }}>
                  <BarChart3 size={32} style={{ margin: '0 auto 10px', color: '#60a5fa', opacity: 0.7 }} />
                  <strong style={{ display: 'block', color: '#f8fafc' }}>No Resume Analytics Available Yet</strong>
                  <p style={{ fontSize: 12, color: '#94a3b8', margin: '4px 0 16px' }}>
                    Upload candidate resumes to generate real ATS score distributions and performance telemetry.
                  </p>
                  <Button onClick={() => go('upload')} style={{ fontSize: 12, padding: '6px 14px' }}>
                    <Plus size={14} /> Upload First Resume
                  </Button>
                </div>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16 }}>
                  <div style={{ background: '#ef444410', border: '1px solid #ef444430', padding: 16, borderRadius: 10, textAlign: 'center' }}>
                    <span style={{ fontSize: 12, color: '#fca5a5', textTransform: 'uppercase', fontWeight: 600 }}>Needs Improvement (&lt;60)</span>
                    <h2 style={{ margin: '8px 0 0', color: '#fca5a5', fontSize: 28 }}>{lowCount}</h2>
                    <small style={{ color: '#94a3b8' }}>{totalAnalyses > 0 ? ((lowCount / totalAnalyses) * 100).toFixed(0) : 0}% of candidates</small>
                  </div>

                  <div style={{ background: '#f59e0b10', border: '1px solid #f59e0b30', padding: 16, borderRadius: 10, textAlign: 'center' }}>
                    <span style={{ fontSize: 12, color: '#fcd34d', textTransform: 'uppercase', fontWeight: 600 }}>Average (60-79)</span>
                    <h2 style={{ margin: '8px 0 0', color: '#fcd34d', fontSize: 28 }}>{midCount}</h2>
                    <small style={{ color: '#94a3b8' }}>{totalAnalyses > 0 ? ((midCount / totalAnalyses) * 100).toFixed(0) : 0}% of candidates</small>
                  </div>

                  <div style={{ background: '#10b98110', border: '1px solid #10b98130', padding: 16, borderRadius: 10, textAlign: 'center' }}>
                    <span style={{ fontSize: 12, color: '#86efac', textTransform: 'uppercase', fontWeight: 600 }}>Top Match (≥80)</span>
                    <h2 style={{ margin: '8px 0 0', color: '#86efac', fontSize: 28 }}>{highCount}</h2>
                    <small style={{ color: '#94a3b8' }}>{totalAnalyses > 0 ? ((highCount / totalAnalyses) * 100).toFixed(0) : 0}% of candidates</small>
                  </div>
                </div>
              )}
            </section>
          </div>

          {/* Recent History Table */}
          <div className="dashGrid" style={{ marginTop: 24 }}>
            <section className="panel" style={{ gridColumn: '1 / -1' }}>
              <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3>Recent Saved Resumes</h3>
                  <p>Click any candidate to open the interactive ATS report and rewriter.</p>
                </div>
                {totalAnalyses > 0 && <button onClick={() => go('history')}>View All ({totalAnalyses})</button>}
              </header>

              {history.length === 0 ? (
                <div style={{ padding: 40, textAlign: 'center', color: '#94a3b8' }}>
                  <FileText size={32} style={{ margin: '0 auto 10px', opacity: 0.5 }} />
                  {currentUser ? 'No saved resume analyses found. Upload a resume to populate your dashboard!' : 'Sign in to view your saved resume history.'}
                </div>
              ) : (
                <div className="tableWrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Candidate</th>
                        <th>File Name</th>
                        <th>ATS Score</th>
                        <th>ATS Level</th>
                        <th>Skills Count</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {history.slice(0, 5).map(record => (
                        <tr key={record.id} style={{ cursor: 'pointer' }} onClick={() => { onSelectAnalysis(record); go('results'); }}>
                          <td>
                            <div className="person">
                              <div className="miniAvatar">
                                {record.candidate_name ? record.candidate_name.substring(0, 2).toUpperCase() : 'CD'}
                              </div>
                              <span>
                                <b>{record.candidate_name || 'Candidate'}</b>
                                <small>{record.candidate_email || 'No email provided'}</small>
                              </span>
                            </div>
                          </td>
                          <td>
                            <span style={{ fontSize: 12, color: '#94a3b8' }}>{record.file_name}</span>
                          </td>
                          <td>
                            <b className="scoreText">{record.ats_score} / 100</b>
                          </td>
                          <td>
                            <span className={'tag ' + (record.ats_score >= 80 ? 'best' : '')}>{record.ats_level}</span>
                          </td>
                          <td>{record.parsed_data?.skills?.length || 0} skills</td>
                          <td>
                            <Button kind="ghost" onClick={() => { onSelectAnalysis(record); go('results'); }}>
                              View Report <ChevronRight size={14} />
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </div>
        </>
      )}
    </AppShell>
  );
}
