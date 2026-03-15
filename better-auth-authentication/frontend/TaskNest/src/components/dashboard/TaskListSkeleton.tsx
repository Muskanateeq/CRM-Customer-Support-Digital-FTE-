/**
 * TaskListSkeleton Component
 * Loading skeleton for task list
 */

'use client';

import React from 'react';
import './TaskListSkeleton.css';

export default function TaskListSkeleton() {
  return (
    <div className="task-list-skeleton">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="task-skeleton-item">
          <div className="task-skeleton-checkbox"></div>
          <div className="task-skeleton-content">
            <div className="task-skeleton-title"></div>
            <div className="task-skeleton-meta"></div>
          </div>
          <div className="task-skeleton-priority"></div>
        </div>
      ))}
    </div>
  );
}
