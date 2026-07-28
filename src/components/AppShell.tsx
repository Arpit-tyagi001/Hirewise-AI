import React, { ReactNode } from 'react';
import { ChevronRight, LayoutDashboard, LogOut, Sparkles, Users, X } from 'lucide-react';
import { Logo } from './Logo';
import { Page } from './Navbar';
import { User } from '../services/api';

interface AppShellProps {
  children: ReactNode;
  go: (p: Page) => void;
  active: string;
  currentUser: User | null;
  recordsCount?: number;
  onOpenAuthModal: () => void;
  onLogout: () => void;
}

export function AppShell({
  children,
  go,
  active,
  currentUser,
  recordsCount = 0,
  onOpenAuthModal,
  onLogout
}: AppShellProps) {
  const links: [string, any, Page, number | null][] = [
    ['Overview', LayoutDashboard, 'dashboard', null],
    ['Analyze Resume', Sparkles, 'upload', null],
    ['History & Records', Users, 'history', recordsCount]
  ];

  return (
    <div className="appShell">
      <aside>
        <Logo />
        <div className="workspace">
          <span>WORKSPACE</span>
          <button>
            {currentUser ? `${currentUser.full_name || 'User'}'s Workspace` : 'Demo Workspace'}{' '}
            <ChevronRight size={14} />
          </button>
        </div>
        <nav>
          {links.map(([l, Icon, p, badge]) => (
            <button className={l === active ? 'selected' : ''} onClick={() => go(p)} key={l}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Icon size={17} />
                {l}
              </div>
              {badge !== null && badge > 0 && (
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    background: '#2563eb',
                    color: '#ffffff',
                    padding: '2px 8px',
                    borderRadius: 10
                  }}
                >
                  {badge}
                </span>
              )}
            </button>
          ))}
        </nav>
        <div className="asideBottom">
          <button onClick={() => go('home')}>
            <ChevronRight size={17} /> Back to Landing Page
          </button>

          {currentUser ? (
            <div className="profile" style={{ justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', gap: 9, alignItems: 'center' }}>
                <div className="portrait">
                  {currentUser.full_name ? currentUser.full_name.substring(0, 2).toUpperCase() : 'US'}
                </div>
                <span>
                  <b>{currentUser.full_name || 'User'}</b>
                  <small>{currentUser.email}</small>
                </span>
              </div>
              <button onClick={onLogout} title="Logout" style={{ color: '#ef4444', padding: 4 }}>
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <div className="profile" style={{ cursor: 'pointer' }} onClick={onOpenAuthModal}>
              <div className="portrait" style={{ background: '#334155' }}>
                DM
              </div>
              <span>
                <b>Demo Mode</b>
                <small style={{ color: '#60a5fa' }}>Click to Sign In / Register</small>
              </span>
            </div>
          )}
        </div>
      </aside>
      <main className="dashMain">
        <div className="mobileDash">
          <Logo />
          <button onClick={() => go('home')}>
            <X size={18} />
          </button>
        </div>
        {children}
      </main>
    </div>
  );
}
