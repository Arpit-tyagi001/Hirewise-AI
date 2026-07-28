/**
 * Centralized API Service for HireWise AI Application.
 * Configured via VITE_API_URL environment variable.
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  created_at?: string;
}

export interface AnalysisRecord {
  id: number;
  user_id?: number | null;
  file_name: string;
  file_type: string;
  candidate_name: string;
  candidate_email: string;
  parsed_data: any;
  ats_score: number;
  ats_level: string;
  section_scores: Record<string, { score: number; max: number }>;
  suggestions: Array<{ type: string; priority: string; category: string; title: string; message: string }>;
  jd_match_data?: any;
  created_at?: string;
}

export function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('hirewise_token');
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export async function registerUser(payload: { email: string; password: string; full_name?: string }) {
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Registration failed.');
  }
  return data;
}

export async function loginUser(payload: { email: string; password: string }) {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Login failed.');
  }
  return data;
}

export async function getCurrentUser(): Promise<User> {
  const res = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    throw new Error('Unauthorized or session expired');
  }
  return res.json();
}

export async function fetchHistory(): Promise<AnalysisRecord[]> {
  const res = await fetch(`${API_BASE_URL}/history`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.detail || 'Failed to fetch analysis history.');
  }
  return res.json();
}

export async function fetchAnalysisById(id: number): Promise<AnalysisRecord> {
  const res = await fetch(`${API_BASE_URL}/analysis/${id}`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.detail || `Failed to fetch analysis #${id}.`);
  }
  return res.json();
}

export async function deleteAnalysis(id: number): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/analysis/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.detail || `Failed to delete analysis #${id}.`);
  }
}

export async function uploadAndAnalyzeResume(file: File): Promise<AnalysisRecord> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to analyze resume file.');
  }
  return data;
}

export async function matchJobDescription(analysisId: number, jobDescription: string) {
  const headers = { ...getAuthHeaders(), 'Content-Type': 'application/json' };
  const res = await fetch(`${API_BASE_URL}/match-jd`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ analysis_id: analysisId, job_description: jobDescription })
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to calculate JD match.');
  }
  return data;
}

export async function rewriteResumeBullets(analysisId: number, jobDescription: string) {
  const headers = { ...getAuthHeaders(), 'Content-Type': 'application/json' };
  const res = await fetch(`${API_BASE_URL}/rewrite-resume`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ analysis_id: analysisId, job_description: jobDescription })
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to generate bullet rewrites.');
  }
  return data;
}

export async function exportTailoredResume(analysisId: number, acceptedRewrites: any[]) {
  const headers = { ...getAuthHeaders(), 'Content-Type': 'application/json' };
  const res = await fetch(`${API_BASE_URL}/export-tailored-resume`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ analysis_id: analysisId, accepted_rewrites: acceptedRewrites })
  });

  if (!res.ok) {
    throw new Error('Failed to generate tailored DOCX export.');
  }
  return res.blob();
}
