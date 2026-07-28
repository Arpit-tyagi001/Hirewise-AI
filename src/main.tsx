import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';
import { Navbar, Page } from './components/Navbar';
import { AuthModal } from './components/AuthModal';
import { Home } from './pages/Home';
import { Dashboard } from './pages/Dashboard';
import { UploadPage } from './pages/UploadPage';
import { Results } from './pages/Results';
import { HistoryView } from './pages/HistoryView';
import { Pricing } from './pages/Pricing';
import { About } from './pages/About';
import { Contact } from './pages/Contact';
import { AnalysisRecord, getCurrentUser, User } from './services/api';

function App() {
  const [page, setPage] = useState<Page>('home');
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisRecord | null>(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);

  useEffect(() => {
    document.body.classList.toggle('dark', theme === 'dark');
    document.body.classList.toggle('light', theme === 'light');
  }, [theme]);

  // Restore authenticated session on load if token present
  useEffect(() => {
    const token = localStorage.getItem('hirewise_token');
    if (token) {
      getCurrentUser()
        .then(user => setCurrentUser(user))
        .catch(err => {
          console.warn('Session expired or invalid:', err);
          localStorage.removeItem('hirewise_token');
          setCurrentUser(null);
        });
    }
  }, []);

  const handleAuthSuccess = (user: User, token: string) => {
    localStorage.setItem('hirewise_token', token);
    setCurrentUser(user);
    setAuthModalOpen(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('hirewise_token');
    setCurrentUser(null);
    if (page === 'history') {
      setPage('home');
    }
  };

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  return (
    <div className="app font-sans antialiased text-slate-100 min-h-screen">
      {/* Show top Navbar on public pages */}
      {page !== 'dashboard' && page !== 'upload' && page !== 'results' && page !== 'history' && (
        <Navbar
          page={page}
          setPage={setPage}
          theme={theme}
          setTheme={toggleTheme}
          currentUser={currentUser}
          onOpenAuthModal={() => setAuthModalOpen(true)}
          onLogout={handleLogout}
        />
      )}

      {/* Pages Router */}
      {page === 'home' && <Home go={setPage} />}
      {page === 'pricing' && <Pricing go={setPage} />}
      {page === 'about' && <About go={setPage} />}
      {page === 'contact' && <Contact go={setPage} />}

      {page === 'dashboard' && (
        <Dashboard
          go={setPage}
          onSelectAnalysis={setCurrentAnalysis}
          currentUser={currentUser}
          onOpenAuthModal={() => setAuthModalOpen(true)}
        />
      )}

      {page === 'upload' && (
        <UploadPage
          go={setPage}
          onAnalysisComplete={setCurrentAnalysis}
          currentUser={currentUser}
        />
      )}

      {page === 'results' && (
        <Results
          go={setPage}
          analysis={currentAnalysis}
          currentUser={currentUser}
        />
      )}

      {page === 'history' && (
        <HistoryView
          go={setPage}
          onSelectAnalysis={setCurrentAnalysis}
          currentUser={currentUser}
          onOpenAuthModal={() => setAuthModalOpen(true)}
        />
      )}

      {/* Global Auth Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />
    </div>
  );
}

const rootElement = document.getElementById('root');
if (rootElement) {
  createRoot(rootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}
