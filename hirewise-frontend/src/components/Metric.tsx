import React from 'react';

interface MetricProps {
  label: string;
  value: string;
  delta: string;
  icon: any;
}

export function Metric({ label, value, delta, icon: Icon }: MetricProps) {
  return (
    <article className="metric">
      <div className="metricIcon">
        <Icon size={18} />
      </div>
      <span>{label}</span>
      <strong>{value}</strong>
      <small className="up">↗ {delta}</small>
    </article>
  );
}
