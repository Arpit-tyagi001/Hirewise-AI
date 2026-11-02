import React, { CSSProperties, ReactNode } from 'react';

interface ButtonProps {
  children: ReactNode;
  onClick?: (e?: any) => void;
  kind?: 'primary' | 'ghost';
  disabled?: boolean;
  style?: CSSProperties;
  type?: 'button' | 'submit' | 'reset';
}

export function Button({
  children,
  onClick,
  kind = 'primary',
  disabled = false,
  style,
  type = 'button'
}: ButtonProps) {
  return (
    <button
      type={type}
      className={`btn ${kind}`}
      onClick={onClick}
      disabled={disabled}
      style={{
        opacity: disabled ? 0.6 : 1,
        cursor: disabled ? 'not-allowed' : 'pointer',
        ...style
      }}
    >
      {children}
    </button>
  );
}
