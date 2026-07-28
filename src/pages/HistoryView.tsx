import React, { useEffect, useState } from 'react';
import { AlertCircle, ChevronRight, FileText, RefreshCw, Search, Trash2 } from 'lucide-react';
import { AppShell } from '../components/AppShell';
import { Button } from '../components/Button';
import { TableSkeleton } from '../components/LoadingSkeleton';
import { Page } from '../components/Navbar';
import { AnalysisRecord, deleteAnalysis, fetchHistory, User } from '../services/api';

interface HistoryViewProps {
  go: (p: Page) => void;
  onSelectAnalysis: (a: AnalysisRecord) => void;
  currentUser: User | null;
  onOpenAuthModal: () => void;
}

export function HistoryView({ go, onSelectAnalysis, currentUser, onOpenAuthModal }: HistoryViewProps) {
  const [history, setHistory] = useState<AnalysisRecord[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  const loadHistory = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const records = await fetchHistory();
      setHistory(records);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || 'Failed to load history records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [currentUser]);

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm(`Delete analysis record #${id}?`)) return;
    try {
      await deleteAnalysis(id);
      setHistory(history.filter(item => item.id !== id));
    } catch (err: any) {
      alert(err.message || 'Could not delete record.');
    }
  };

  const filtered = history.filter(item =>
    (item.candidate_name || '').toLowerCase().includes(query.toLowerCase()) ||
    (item.file_name || '').toLowerCase().includes(query.toLowerCase())
  );

  return (
    <AppShell go={go} active="History & Records" currentUser={currentUser} recordsCount={history.length} onOpenAuthModal={onOpenAuthModal} onLogout={() => {}}>
      <div className="crumb">Workspace <ChevronRight size={13} /> Saved Analysis History</div>
      <div className="pageIntro">
        <div>
          <h2>Evaluation History</h2>
          <p>{currentUser ? `Saved records isolated for ${currentUser.email}` : 'Demo Mode — Showing records created in this session'}</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <Button kind="ghost" onClick={loadHistory}>
            <RefreshCw size={15} /> Refresh
          </Button>
          <Button onClick={() => go('upload')}>
            New Analysis <ChevronRight size={15} />
          </Button>
        </div>
      </div>

      {errorMsg && (
        <div style={{ background: '#ef444415', border: '1px solid #ef444455', color: '#fca5a5', padding: '12px 16px', borderRadius: 10, marginBottom: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
          <Button kind="ghost" onClick={loadHistory} style={{ fontSize: 12 }}>Retry</Button>
        </div>
      )}

      <div className="searchBar" style={{ marginBottom: 20, display: 'flex', gap: 10, background: '#09101f', padding: '8px 14px', borderRadius: 10, border: '1px solid #ffffff15' }}>
        <Search size={18} style={{ color: '#64748b', alignSelf: 'center' }} />
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Filter candidate name or filename..."
          style={{ background: 'none', border: 'none', color: '#f8fafc', width: '100%', outline: 'none', fontSize: 13 }}
        />
      </div>

      <section className="panel">
        {loading ? (
          <TableSkeleton />
        ) : filtered.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#94a3b8' }}>
            <FileText size={32} style={{ margin: '0 auto 10px', opacity: 0.5 }} />
            {query ? 'No matching candidate evaluations found.' : 'No saved resume analyses yet.'}
          </div>
        ) : (
          <div className="tableWrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Candidate Name</th>
                  <th>File Name</th>
                  <th>ATS Score</th>
                  <th>Level</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(record => (
                  <tr key={record.id} style={{ cursor: 'pointer' }} onClick={() => { onSelectAnalysis(record); go('results'); }}>
                    <td>#{record.id}</td>
                    <td>
                      <b>{record.candidate_name || 'Candidate'}</b>
                    </td>
                    <td>{record.file_name}</td>
                    <td><b className="scoreText">{record.ats_score} / 100</b></td>
                    <td><span className={'tag ' + (record.ats_score >= 80 ? 'best' : '')}>{record.ats_level}</span></td>
                    <td>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <Button kind="ghost" onClick={() => { onSelectAnalysis(record); go('results'); }} style={{ fontSize: 12, padding: '4px 8px' }}>
                          Open Report
                        </Button>
                        <Button kind="ghost" onClick={(e) => handleDelete(record.id, e)} style={{ color: '#ef4444', fontSize: 12, padding: '4px 8px' }}>
                          <Trash2 size={13} />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </AppShell>
  );
}
