import React from 'react';
import '../logo.css';

export function Logo() {
  return (
    <div className="logo" aria-label="HireWise AI">
      <svg className="logoSymbol" viewBox="0 0 40 40" role="img" aria-hidden="true">
        <defs>
          <linearGradient id="hirewise-gradient" x1="5" x2="35" y1="4" y2="36" gradientUnits="userSpaceOnUse">
            <stop stopColor="#67e8f9" />
            <stop offset=".48" stopColor="#3b82f6" />
            <stop offset="1" stopColor="#2563eb" />
          </linearGradient>
        </defs>
        <rect x="5" y="4" width="25" height="32" rx="7" fill="url(#hirewise-gradient)" />
        <path d="M12 12h11M12 17h8M12 22h5" stroke="white" strokeWidth="2.2" strokeLinecap="round" opacity=".92" />
        <circle cx="26" cy="27" r="9" fill="#0f172a" stroke="url(#hirewise-gradient)" strokeWidth="2.4" />
        <path d="m21.8 27.2 2.7 2.7 5.2-5.5" fill="none" stroke="url(#hirewise-gradient)" strokeWidth="2.7" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <span className="logoCopy">HireWise <b>AI</b></span>
    </div>
  );
}
