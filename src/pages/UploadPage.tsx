import React, { useState } from 'react';
import { AlertCircle, CheckCircle2, ChevronRight, Sparkles, Upload } from 'lucide-react';
import { AppShell } from '../components/AppShell';
import { Button } from '../components/Button';
import { Page } from '../components/Navbar';
import { AnalysisRecord, matchJobDescription, uploadAndAnalyzeResume, User } from '../services/api';

interface UploadPageProps {
  go: (p: Page) => void;
  onAnalysisComplete: (a: AnalysisRecord) => void;
  currentUser: User | null;
}

export function UploadPage({ go, onAnalysisComplete, currentUser }: UploadPageProps) {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState<string>(
    'We are seeking a Senior Full Stack Engineer proficient in Python, FastAPI, React, TypeScript, and PostgreSQL. The ideal candidate will design REST APIs, build modern reactive frontends, and implement automated ATS systems.'
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setErrorMsg('');
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setErrorMsg('Please select a PDF or DOCX resume file.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg('');

    try {
      // 1. Upload & Analyze resume
      let analysisRecord = await uploadAndAnalyzeResume(file);

      // 2. If JD provided, trigger match-jd
      if (jobDescription.trim()) {
        try {
          const jdData = await matchJobDescription(analysisRecord.id, jobDescription);
          analysisRecord.jd_match_data = jdData.match_result;
        } catch (jdErr) {
          console.warn('JD match warning:', jdErr);
        }
      }

      setIsSubmitting(false);
      onAnalysisComplete(analysisRecord);
      go('results');
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || 'An error occurred while analyzing the resume file.');
      setIsSubmitting(false);
    }
  };

  return (
    <AppShell go={go} active="Analyze Resume" currentUser={currentUser} onOpenAuthModal={() => {}} onLogout={() => {}}>
      <div className="crumb">Workspace <ChevronRight size={13} /> Analyze Resume</div>
      <div className="analyzeHead">
        <span className="eyebrow"><Sparkles size={14} /> Real-Time Pipeline</span>
        <h2>Upload & Analyze Resume</h2>
        <p>
          {currentUser
            ? `Analyzing as ${currentUser.full_name} (${currentUser.email}). Record will be saved to your account history.`
            : 'Operating in Anonymous Demo Mode. Sign in to save records to your account history.'}
        </p>
      </div>

      {errorMsg && (
        <div style={{ background: '#ef444415', border: '1px solid #ef444455', color: '#fca5a5', padding: '12px 16px', borderRadius: 10, marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
          <AlertCircle size={18} />
          <span>{errorMsg}</span>
        </div>
      )}

      <div className="uploadColumns">
        <section className="uploadCard">
          <span className="step">01</span>
          <h3>Upload Resume Document</h3>
          <p>PDF or DOCX file format (up to 10 MB)</p>
          <label className={'dropzone ' + (file ? 'done' : '')}>
            <input type="file" accept=".pdf,.docx,.doc" onChange={handleFileChange} />
            {file ? (
              <>
                <CheckCircle2 size={32} style={{ color: '#4ade80' }} />
                <b style={{ color: '#86efac' }}>{file.name}</b>
                <span>{(file.size / 1024).toFixed(1)} KB • Ready for extraction</span>
              </>
            ) : (
              <>
                <span className="uploadIcon"><Upload size={24} /></span>
                <b>Click to browse or drop resume file here</b>
                <span>Supports .pdf and .docx resume files</span>
              </>
            )}
          </label>
        </section>

        <section className="uploadCard">
          <span className="step">02</span>
          <h3>Job Description (Optional)</h3>
          <p>Paste the target Job Description to generate skill gap analysis</p>
          <textarea
            aria-label="Job description"
            value={jobDescription}
            onChange={e => setJobDescription(e.target.value)}
            placeholder="Paste target job requirements, skills, and qualifications here..."
          />
          <span className="characters">{jobDescription.length} characters</span>
        </section>
      </div>

      <div className="analyzeAction">
        <div>
          <Sparkles size={20} />
          <span>
            <b>AI Resume Analysis Engine Ready</b>
            <small>Runs python-docx/pypdf parsing, 10-dimension ATS scoring & scikit-learn JD match</small>
          </span>
        </div>
        <Button onClick={handleAnalyze} disabled={isSubmitting || !file}>
          {isSubmitting ? 'Analyzing Resume...' : 'Analyze Resume Now'} <Sparkles size={16} />
        </Button>
      </div>
    </AppShell>
  );
}
