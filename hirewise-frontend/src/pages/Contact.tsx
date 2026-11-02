import React, { useState } from 'react';
import { CheckCircle2, Mail, MessageSquare, Send, User } from 'lucide-react';
import { Button } from '../components/Button';
import { Footer } from '../components/Footer';
import { Page } from '../components/Navbar';

export function Contact({ go }: { go: (p: Page) => void }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || !message) return;

    setLoading(true);
    // Simulate brief client submission confirmation delay
    setTimeout(() => {
      setLoading(false);
      setSubmitted(true);
    }, 600);
  };

  const handleReset = () => {
    setName('');
    setEmail('');
    setSubject('');
    setMessage('');
    setSubmitted(false);
  };

  return (
    <>
      <section className="contactSection" style={{ maxWidth: 900, margin: '40px auto', padding: '0 20px' }}>
        <div style={{ textAlign: 'center', marginBottom: 36 }}>
          <span className="eyebrow"><MessageSquare size={14} /> Get in Touch</span>
          <h1 style={{ fontSize: 36, margin: '10px 0 8px' }}>Contact Engineering Team</h1>
          <p style={{ color: '#94a3b8' }}>Have questions about our ATS scoring algorithms or enterprise API integrations?</p>
        </div>

        <div className="panel" style={{ padding: 32 }}>
          {submitted ? (
            <div style={{ textAlign: 'center', padding: '30px 20px' }}>
              <CheckCircle2 size={48} style={{ color: '#4ade80', margin: '0 auto 16px' }} />
              <h3 style={{ fontSize: 24, margin: '0 0 8px', color: '#f8fafc' }}>Message Received!</h3>
              <p style={{ color: '#94a3b8', maxWidth: 460, margin: '0 auto 24px' }}>
                Thank you, <strong>{name}</strong>. Our engineering team has received your message regarding <em>"{subject || 'General Inquiry'}"</em> and will reply to <code>{email}</code> shortly.
              </p>
              <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
                <Button onClick={handleReset} kind="ghost">
                  Send Another Message
                </Button>
                <Button onClick={() => go('upload')}>
                  Analyze Resume Now
                </Button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} style={{ display: 'grid', gap: 18 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 13, color: '#cbd5e1', marginBottom: 6 }}>Your Name *</label>
                  <div style={{ display: 'flex', alignItems: 'center', background: '#09101f', border: '1px solid #ffffff15', borderRadius: 8, padding: '0 12px' }}>
                    <User size={16} style={{ color: '#64748b', marginRight: 8 }} />
                    <input
                      type="text"
                      required
                      value={name}
                      onChange={e => setName(e.target.value)}
                      placeholder="Jane Doe"
                      style={{ width: '100%', padding: '10px 0', background: 'none', border: 'none', color: '#f8fafc', outline: 'none', fontSize: 13 }}
                    />
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 13, color: '#cbd5e1', marginBottom: 6 }}>Email Address *</label>
                  <div style={{ display: 'flex', alignItems: 'center', background: '#09101f', border: '1px solid #ffffff15', borderRadius: 8, padding: '0 12px' }}>
                    <Mail size={16} style={{ color: '#64748b', marginRight: 8 }} />
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={e => setEmail(e.target.value)}
                      placeholder="jane@company.com"
                      style={{ width: '100%', padding: '10px 0', background: 'none', border: 'none', color: '#f8fafc', outline: 'none', fontSize: 13 }}
                    />
                  </div>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 13, color: '#cbd5e1', marginBottom: 6 }}>Subject</label>
                <input
                  type="text"
                  value={subject}
                  onChange={e => setSubject(e.target.value)}
                  placeholder="Enterprise API integration / Support"
                  style={{ width: '100%', padding: '10px 12px', background: '#09101f', border: '1px solid #ffffff15', borderRadius: 8, color: '#f8fafc', outline: 'none', fontSize: 13 }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: 13, color: '#cbd5e1', marginBottom: 6 }}>Message *</label>
                <textarea
                  required
                  rows={5}
                  value={message}
                  onChange={e => setMessage(e.target.value)}
                  placeholder="Tell us how we can help..."
                  style={{ width: '100%', padding: '10px 12px', background: '#09101f', border: '1px solid #ffffff15', borderRadius: 8, color: '#f8fafc', outline: 'none', fontSize: 13 }}
                />
              </div>

              <Button type="submit" disabled={loading} style={{ justifySelf: 'start', marginTop: 6 }}>
                {loading ? 'Sending Message...' : 'Send Message'} <Send size={15} />
              </Button>
            </form>
          )}
        </div>
      </section>
      <Footer go={go} />
    </>
  );
}
