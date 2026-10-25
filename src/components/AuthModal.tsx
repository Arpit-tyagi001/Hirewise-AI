import React, { useState } from 'react';
import { ArrowRight, X } from 'lucide-react';
import { Button } from './Button';
import { loginUser, registerUser, User } from '../services/api';
import toast from 'react-hot-toast';
interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAuthSuccess: (user: User, token: string) => void;
}

export function AuthModal({ isOpen, onClose, onAuthSuccess }: AuthModalProps) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true);

    try {
      if (isRegister) {
        const data = await registerUser({ email, password, full_name: fullName });
        onAuthSuccess(data.user, data.access_token);
        toast.success("Account created Succcessfully!");
      } else {
        const data = await loginUser({ email, password });
        onAuthSuccess(data.user, data.access_token);
        toast.success("Welcome back!");
      }
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'Authentication failed.');
      toast.error(err.message || 'Authentication failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 100,
        background: 'rgba(2, 6, 23, 0.85)',
        backdropFilter: 'blur(8px)',
        display: 'grid',
        placeItems: 'center',
        padding: 20
      }}
    >
      <div
        style={{
          background: '#0c1525',
          border: '1px solid #ffffff15',
          borderRadius: 16,
          width: '100%',
          maxWidth: 420,
          padding: 28,
          position: 'relative'
        }}
      >
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: 18, right: 18, color: '#94a3b8', background: 'none', border: 'none', cursor: 'pointer' }}
        >
          <X size={20} />
        </button>

        <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
          <Button kind={!isRegister ? 'primary' : 'ghost'} onClick={() => setIsRegister(false)} style={{ flex: 1 }}>
            Sign In
          </Button>
          <Button kind={isRegister ? 'primary' : 'ghost'} onClick={() => setIsRegister(true)} style={{ flex: 1 }}>
            Register
          </Button>
        </div>

        <h3 style={{ margin: '0 0 6px', fontSize: 20 }}>{!isRegister ? 'Sign In to HireWise AI' : 'Create Account'}</h3>
        <p style={{ margin: '0 0 20px', color: '#94a3b8', fontSize: 13 }}>
          {!isRegister
            ? 'Access your private resume analysis history and dashboard'
            : 'Join HireWise AI to save and manage candidate evaluations'}
        </p>

        {errorMsg && (
          <div
            style={{
              background: '#ef444418',
              border: '1px solid #ef444455',
              color: '#fca5a5',
              padding: '10px 12px',
              borderRadius: 8,
              fontSize: 12,
              marginBottom: 16
            }}
          >
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 14 }}>
          {isRegister && (
            <div>
              <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 4 }}>Full Name</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={e => setFullName(e.target.value)}
                placeholder="Jane Doe"
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  background: '#060b18',
                  border: '1px solid #ffffff15',
                  borderRadius: 8,
                  color: '#f8fafc',
                  fontSize: 13
                }}
              />
            </div>
          )}

          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 4 }}>Work Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@company.com"
              style={{
                width: '100%',
                padding: '10px 12px',
                background: '#060b18',
                border: '1px solid #ffffff15',
                borderRadius: 8,
                color: '#f8fafc',
                fontSize: 13
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 4 }}>Password</label>
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              style={{
                width: '100%',
                padding: '10px 12px',
                background: '#060b18',
                border: '1px solid #ffffff15',
                borderRadius: 8,
                color: '#f8fafc',
                fontSize: 13
              }}
            />
          </div>

          <Button disabled={loading} type="submit" style={{ marginTop: 10 }}>
            {loading ? 'Processing...' : isRegister ? 'Create Account' : 'Sign In'} <ArrowRight size={16} />
          </Button>
        </form>
      </div>
    </div>
  );
}
