import React from 'react';

export function DashboardSkeleton() {
  return (
    <div style={{ display: 'grid', gap: 20 }}>
      {/* Metric Cards Skeleton */}
      <div className="metricGrid">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="metric" style={{ opacity: 0.5, animation: 'pulse 1.5s infinite ease-in-out' }}>
            <div style={{ width: 36, height: 36, borderRadius: 8, background: '#ffffff15' }} />
            <div style={{ width: '60%', height: 12, background: '#ffffff15', borderRadius: 4, marginTop: 10 }} />
            <div style={{ width: '40%', height: 24, background: '#ffffff20', borderRadius: 6, marginTop: 8 }} />
          </div>
        ))}
      </div>

      {/* Table Skeleton */}
      <div className="panel" style={{ padding: 24, opacity: 0.6, animation: 'pulse 1.5s infinite ease-in-out' }}>
        <div style={{ width: '30%', height: 20, background: '#ffffff18', borderRadius: 4, marginBottom: 20 }} />
        <div style={{ display: 'grid', gap: 12 }}>
          {[1, 2, 3].map(row => (
            <div key={row} style={{ height: 48, background: '#ffffff08', borderRadius: 8 }} />
          ))}
        </div>
      </div>
    </div>
  );
}

export function TableSkeleton() {
  return (
    <div style={{ padding: 20, opacity: 0.6, animation: 'pulse 1.5s infinite ease-in-out' }}>
      {[1, 2, 3, 4].map(i => (
        <div key={i} style={{ height: 44, background: '#ffffff0a', borderRadius: 8, marginBottom: 10 }} />
      ))}
    </div>
  );
}
