import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import './styles.css';
import './motion.css';

// Components & Pages
import { AppShell } from './components/AppShell';
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

function AppLayout() {
  const [theme, setTheme] = useState<'dark' | 'light'>(
    (localStorage.getItem('hirewise_theme') as 'dark' | 'light') || 'dark'
  );
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisRecord | null>(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);

  // React Router hooks for URL management
  const location = useLocation();
  const navigate = useNavigate();

  // THE TRICK: Translate old state names into new URL routes to satisfy TypeScript
  const go = (page: string) => {
    const routeMap: Record<string, string> = {
      home: '/', pricing: '/pricing', about: '/about', contact: '/contact',
      upload: '/upload', dashboard: '/dashboard', results: '/results', history: '/history'
    };
    navigate(routeMap[page] || '/');
  };

  useEffect(() => {
    document.body.classList.toggle('dark', theme === 'dark');
    document.body.classList.toggle('light', theme === 'light');
    localStorage.setItem('hirewise_theme', theme);
  }, [theme]);

  useEffect(() => {
    const token = localStorage.getItem('hirewise_token');
    if (token) {
      getCurrentUser()
        .then(user => setCurrentUser(user))
        .catch(() => {
          localStorage.removeItem('hirewise_token');
          setCurrentUser(null);
        });
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('hirewise_token');
    setCurrentUser(null);
    navigate('/');
  };

  const toggleTheme = () => setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));

  // Check if current URL is an app page so we can hide the public Navbar
  const isAppPage = ['/dashboard', '/upload', '/results', '/history'].includes(location.pathname);

 return (
    <div className="app font-sans antialiased text-slate-100 min-h-screen">
      
      {!isAppPage && (
        <Navbar 
          page="home" 
          setPage={go as any} 
          theme={theme} 
          setTheme={toggleTheme} 
          currentUser={currentUser} 
          onOpenAuthModal={() => setAuthModalOpen(true)} 
          onLogout={handleLogout} 
        />
      )}

      {/* Removed the <AppShell> wrapper here! Let the routes render directly. */}
      <Routes>
        <Route path="/" element={<Home go={go as any} />} />
        <Route path="/pricing" element={<Pricing go={go as any} />} />
        <Route path="/about" element={<About go={go as any} />} />
        <Route path="/contact" element={<Contact go={go as any} />} />
        <Route path="/dashboard" element={<Dashboard go={go as any} onSelectAnalysis={setCurrentAnalysis} currentUser={currentUser} onOpenAuthModal={() => setAuthModalOpen(true)} />} />
        <Route path="/upload" element={<UploadPage go={go as any} onAnalysisComplete={setCurrentAnalysis} currentUser={currentUser} />} />
        <Route path="/results" element={<Results go={go as any} analysis={currentAnalysis} currentUser={currentUser} />} />
        <Route path="/history" element={<HistoryView go={go as any} onSelectAnalysis={setCurrentAnalysis} currentUser={currentUser} onOpenAuthModal={() => setAuthModalOpen(true)} />} />
      </Routes>

      <AuthModal isOpen={authModalOpen} onClose={() => setAuthModalOpen(false)} onAuthSuccess={(user, token) => {
        localStorage.setItem('hirewise_token', token);
        setCurrentUser(user);
        setAuthModalOpen(false);
      }} />
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}

const rootElement = document.getElementById('root');
if (rootElement) {
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}