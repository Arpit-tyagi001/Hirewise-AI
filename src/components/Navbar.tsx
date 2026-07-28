import React, { useState } from 'react';
import { ChevronRight, LogOut, Menu, Moon, Sun, User as UserIcon, X } from 'lucide-react';
import { Logo } from './Logo';
import { Button } from './Button';
import { User } from '../services/api';

export type Page = 'home' | 'dashboard' | 'upload' | 'results' | 'history' | 'pricing' | 'about' | 'contact';

interface NavbarProps {
  page: Page;
  setPage: (p: Page) => void;
  theme: string;
  setTheme: () => void;
  currentUser: User | null;
  onOpenAuthModal: () => void;
  onLogout: () => void;
}

export function Navbar({
  page,
  setPage,
  theme,
  setTheme,
  currentUser,
  onOpenAuthModal,
  onLogout
}: NavbarProps) {
  const [open, setOpen] = useState(false);
  const nav: { label: string; page: Page }[] = [
    { label: 'Home', page: 'home' },
    { label: 'Dashboard', page: 'dashboard' },
    { label: 'Upload Resume', page: 'upload' },
    { label: 'History', page: 'history' },
    { label: 'Pricing', page: 'pricing' }
  ];

  return (
    <header className="navbar">
      <Logo />
      <nav className={open ? 'open' : ''}>
        {nav.map(n => (
          <button
            key={n.label}
            onClick={() => {
              setPage(n.page);
              setOpen(false);
            }}
            className={page === n.page ? 'active' : ''}
          >
            {n.label}
          </button>
        ))}
      </nav>
      <div className="navActions">
        <button className="iconBtn" onClick={setTheme} aria-label="Toggle color theme">
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {currentUser ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 12, color: '#93c5fd', fontWeight: 600 }}>
              {currentUser.full_name || currentUser.email}
            </span>
            <Button kind="ghost" onClick={onLogout} style={{ padding: '6px 12px', fontSize: 12 }}>
              <LogOut size={14} /> Logout
            </Button>
          </div>
        ) : (
          <Button kind="ghost" onClick={onOpenAuthModal} style={{ padding: '6px 14px', fontSize: 12 }}>
            <UserIcon size={14} /> Sign In
          </Button>
        )}

        <Button onClick={() => setPage('upload')}>
          Analyze Resume <ChevronRight size={16} />
        </Button>

        <button className="menu" onClick={() => setOpen(!open)} aria-label="Open navigation">
          {open ? <X /> : <Menu />}
        </button>
      </div>
    </header>
  );
}
