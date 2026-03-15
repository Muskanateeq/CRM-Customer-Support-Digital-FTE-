/**
 * TaskSkeleton Component - Loading Placeholder for Task Items
 *
 * Features:
 * - Mimics TaskItem structure
 * - Animated shimmer effect
 * - Responsive design
 */

'use client';

import React from 'react';
import Skeleton from '@/components/ui/Skeleton';

export default function TaskSkeleton() {
  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-4 md:p-6 animate-fade-in">
      <div className="flex items-start gap-4">
        {/* Checkbox Skeleton */}
        <Skeleton width={24} height={24} rounded="md" className="flex-shrink-0 mt-1" />

        {/* Content Skeleton */}
        <div className="flex-1 min-w-0 space-y-3">
          {/* Title */}
          <Skeleton height={24} width="70%" rounded="md" />

          {/* Description */}
          <Skeleton height={16} width="90%" rounded="md" />
          <Skeleton height={16} width="60%" rounded="md" />

          {/* Tags and Metadata */}
          <div className="flex flex-wrap items-center gap-2 mt-3">
            <Skeleton width={80} height={24} rounded="full" />
            <Skeleton width={100} height={24} rounded="full" />
            <Skeleton width={90} height={24} rounded="full" />
          </div>
        </div>

        {/* Actions Skeleton */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <Skeleton width={36} height={36} rounded="lg" />
          <Skeleton width={36} height={36} rounded="lg" />
        </div>
      </div>
    </div>
  );
}
