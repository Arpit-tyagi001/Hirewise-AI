import React from 'react';
import { Logo } from './Logo';
import { Page } from './Navbar';

export function Footer({ go }: { go: (p: Page) => void }) {
  return (
    <footer className="siteFooter">
      <div>
        <Logo />
        <p>Production ATS Resume Analysis & JD Matching Pipeline.</p>
      </div>
      <div>
        <span>Product</span>
        <button onClick={() => go('home')}>Home</button>
        <button onClick={() => go('dashboard')}>Dashboard</button>
        <button onClick={() => go('upload')}>Upload Resume</button>
      </div>
      <div>
        <span>System</span>
        <button onClick={() => go('history')}>History</button>
        <button onClick={() => go('pricing')}>Pricing</button>
        <button onClick={() => go('about')}>About</button>
        <button onClick={() => go('contact')}>Contact</button>
      </div>
      <div>
        <span>Legal</span>
        <button onClick={() => go('contact')}>Privacy Policy</button>
        <button onClick={() => go('contact')}>Terms of Service</button>
      </div>
      <small>© 2026 HireWise AI. All Rights Reserved.</small>
    </footer>
  );
}
