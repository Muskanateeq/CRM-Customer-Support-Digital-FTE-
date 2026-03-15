/**
 * TaskListSkeleton Component - Loading Placeholder for Task List
 *
 * Features:
 * - Multiple task skeletons
 * - Configurable count
 * - Staggered animation
 */

'use client';

import React from 'react';
import TaskSkeleton from './TaskSkeleton';

export interface TaskListSkeletonProps {
  count?: number;
}

export default function TaskListSkeleton({ count = 5 }: TaskListSkeletonProps) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          style={{
            animationDelay: `${index * 100}ms`,
          }}
        >
          <TaskSkeleton />
        </div>
      ))}
    </div>
  );
}
