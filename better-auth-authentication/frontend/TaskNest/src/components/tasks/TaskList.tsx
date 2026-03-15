/**
 * TaskList Component
 * Dark Golden Theme - Modern SaaS Design
 */

'use client';

import React from 'react';
import { Task } from '@/lib/types';
import TaskItem from './TaskItem';
import './TaskList.css';

/**
 * TaskList Props
 */
interface TaskListProps {
  tasks: Task[];
  isLoading: boolean;
  onToggleComplete: (id: number, completed: boolean) => Promise<void>;
  onEdit: (task: Task) => void;
  onDelete: (id: number) => Promise<void>;
}

/**
 * Loading Skeleton with Shimmer Effect
 */
function TaskSkeleton() {
  return (
    <div className="task-skeleton">
      <div className="task-skeleton-content">
        <div className="task-skeleton-checkbox"></div>
        <div className="task-skeleton-body">
          <div className="task-skeleton-title"></div>
          <div className="task-skeleton-badges">
            <div className="task-skeleton-badge"></div>
            <div className="task-skeleton-badge"></div>
          </div>
        </div>
        <div className="task-skeleton-actions">
          <div className="task-skeleton-action"></div>
          <div className="task-skeleton-action"></div>
        </div>
      </div>
      <div className="task-skeleton-shimmer"></div>
    </div>
  );
}

/**
 * Empty State with Animations
 */
function EmptyState() {
  return (
    <div className="task-list-empty">
      {/* Animated Icon */}
      <div className="task-list-empty-icon-wrapper">
        <div className="task-list-empty-ring-outer"></div>
        <div className="task-list-empty-ring-middle"></div>
        <div className="task-list-empty-icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
            />
          </svg>
        </div>
      </div>

      {/* Text content */}
      <h3 className="task-list-empty-title">No tasks yet</h3>
      <p className="task-list-empty-text">
        Your task list is empty. Start organizing your work by creating your first task!
      </p>

      {/* Call to action */}
      <div className="task-list-empty-cta">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 4v16m8-8H4"
          />
        </svg>
        <span>Click &quot;New Task&quot; above to get started</span>
      </div>

      {/* Features list */}
      <div className="task-list-empty-features">
        <div className="task-list-empty-feature">
          <div className="task-list-empty-feature-icon">🎯</div>
          <h4 className="task-list-empty-feature-title">Set Priorities</h4>
          <p className="task-list-empty-feature-text">Organize tasks by priority levels</p>
        </div>
        <div className="task-list-empty-feature">
          <div className="task-list-empty-feature-icon">📅</div>
          <h4 className="task-list-empty-feature-title">Set Deadlines</h4>
          <p className="task-list-empty-feature-text">Never miss important dates</p>
        </div>
        <div className="task-list-empty-feature">
          <div className="task-list-empty-feature-icon">✓</div>
          <h4 className="task-list-empty-feature-title">Track Progress</h4>
          <p className="task-list-empty-feature-text">Mark tasks as complete</p>
        </div>
      </div>
    </div>
  );
}

/**
 * TaskList Component
 */
export default function TaskList({
  tasks,
  isLoading,
  onToggleComplete,
  onEdit,
  onDelete,
}: TaskListProps) {
  // Loading state with staggered skeletons
  if (isLoading) {
    return (
      <div className="task-list-container">
        <TaskSkeleton />
        <TaskSkeleton />
        <TaskSkeleton />
        <TaskSkeleton />
      </div>
    );
  }

  // Empty state
  if (tasks.length === 0) {
    return <EmptyState />;
  }

  // Task list with stagger animation
  return (
    <div className="task-list-container">
      {tasks.map((task, index) => (
        <div
          key={task.id}
          style={{
            animation: 'fadeInUp 0.8s ease-out',
            animationDelay: `${index * 50}ms`,
            animationFillMode: 'both',
          }}
        >
          <TaskItem
            task={task}
            onToggleComplete={onToggleComplete}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        </div>
      ))}

      {/* Task count */}
      <div className="task-list-count">
        <div className="task-list-count-badge">
          <div className="task-list-count-dot"></div>
          <span className="task-list-count-text">
            {tasks.length} task{tasks.length !== 1 ? 's' : ''} in your list
          </span>
        </div>
      </div>
    </div>
  );
}
