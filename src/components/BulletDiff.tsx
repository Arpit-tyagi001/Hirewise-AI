import React from 'react';
import { Check, X, Sparkles, ArrowRight, CheckCircle2, ShieldCheck, Tag } from 'lucide-react';

export interface BulletRewriteItem {
  id: string;
  section: string;
  context_label: string;
  original_bullet: string;
  rewritten_bullet: string;
  reason: string;
  keywords_added?: string[];
  source?: string;
  status: 'suggested' | 'accepted' | 'rejected';
}

interface BulletDiffProps {
  item: BulletRewriteItem;
  onToggleAccept: (id: string, accept: boolean) => void;
}

export const BulletDiff: React.FC<BulletDiffProps> = ({ item, onToggleAccept }) => {
  const isAccepted = item.status === 'accepted';
  const isRejected = item.status === 'rejected';

  return (
    <div
      style={{
        background: isAccepted ? '#10b9810a' : isRejected ? '#ef44440a' : '#ffffff05',
        border: `1px solid ${isAccepted ? '#10b98155' : isRejected ? '#ef444433' : '#ffffff15'}`,
        borderRadius: 12,
        padding: 16,
        marginBottom: 14,
        transition: 'all 0.2s ease-in-out'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', color: '#93c5fd', background: '#2563eb18', padding: '2px 8px', borderRadius: 6 }}>
            {item.context_label}
          </span>
          <span style={{ fontSize: 11, color: '#94a3b8', display: 'flex', alignItems: 'center', gap: 4 }}>
            <Sparkles size={12} style={{ color: '#60a5fa' }} /> {item.reason}
          </span>
        </div>

        <div style={{ display: 'flex', gap: 6 }}>
          <button
            onClick={() => onToggleAccept(item.id, true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              padding: '6px 12px',
              fontSize: 12,
              fontWeight: 600,
              borderRadius: 6,
              border: isAccepted ? '1px solid #10b981' : '1px solid #ffffff20',
              background: isAccepted ? '#10b981' : '#ffffff0a',
              color: isAccepted ? '#022c22' : '#e2e8f0',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            <Check size={14} /> {isAccepted ? 'Accepted' : 'Accept Edit'}
          </button>

          <button
            onClick={() => onToggleAccept(item.id, false)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              padding: '6px 10px',
              fontSize: 12,
              fontWeight: 600,
              borderRadius: 6,
              border: isRejected ? '1px solid #ef4444' : '1px solid #ffffff15',
              background: isRejected ? '#ef444420' : 'transparent',
              color: isRejected ? '#fca5a5' : '#94a3b8',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            <X size={14} /> {isRejected ? 'Rejected' : 'Keep Original'}
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        {/* Original Bullet */}
        <div style={{ background: '#090d16', border: '1px solid #ef444425', borderRadius: 8, padding: 12 }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: '#fca5a5', textTransform: 'uppercase', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 4 }}>
            <span>Original Bullet</span>
          </div>
          <p style={{ margin: 0, fontSize: 12, color: '#cbd5e1', lineHeight: 1.5 }}>
            {item.original_bullet}
          </p>
        </div>

        {/* Rewritten Bullet */}
        <div style={{ background: '#09121a', border: `1px solid ${isAccepted ? '#10b98166' : '#3b82f644'}`, borderRadius: 8, padding: 12 }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: isAccepted ? '#4ade80' : '#60a5fa', textTransform: 'uppercase', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 4 }}>
            <span>Suggested Tailored Bullet</span>
            {isAccepted && <CheckCircle2 size={12} style={{ color: '#4ade80' }} />}
          </div>
          <p style={{ margin: 0, fontSize: 12, color: '#f8fafc', fontWeight: 500, lineHeight: 1.5 }}>
            {item.rewritten_bullet}
          </p>
        </div>
      </div>

      {item.keywords_added && item.keywords_added.length > 0 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 10 }}>
          <Tag size={12} style={{ color: '#60a5fa' }} />
          <span style={{ fontSize: 11, color: '#94a3b8' }}>Contextual keywords inserted:</span>
          {item.keywords_added.map(kw => (
            <span key={kw} style={{ fontSize: 10, background: '#2563eb20', border: '1px solid #2563eb50', color: '#93c5fd', padding: '1px 6px', borderRadius: 4 }}>
              + {kw}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
