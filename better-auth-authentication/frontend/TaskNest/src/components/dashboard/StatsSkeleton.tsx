/**
 * StatsSkeleton Component
 * Loading skeleton for statistics cards
 */

'use client';

import React from 'react';
import './StatsSkeleton.css';

export default function StatsSkeleton() {
  return (
    <div className="stats-skeleton-grid">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="stat-skeleton-card">
          <div className="stat-skeleton-header">
            <div className="stat-skeleton-label"></div>
            <div className="stat-skeleton-icon"></div>
          </div>
          <div className="stat-skeleton-value"></div>
          <div className="stat-skeleton-progress">
            <div className="stat-skeleton-bar"></div>
            <div className="stat-skeleton-text"></div>
          </div>
        </div>
      ))}
    </div>
  );
}
