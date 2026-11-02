import React, { CSSProperties } from 'react';

interface ScoreGaugeProps {
  value?: number;
  label?: string;
}

export function ScoreGauge({ value = 85, label = 'ATS Score' }: ScoreGaugeProps) {
  const normalizedValue = Math.min(100, Math.max(0, value));
  return (
    <div className="score" style={{ '--score': `${normalizedValue * 3.6}deg` } as CSSProperties}>
      <div>
        <b>{normalizedValue}</b>
        <span>{label}</span>
      </div>
    </div>
  );
}
