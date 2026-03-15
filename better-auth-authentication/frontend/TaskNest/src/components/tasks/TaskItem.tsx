/**
 * TaskItem Component
 * Dark Golden Theme - Modern SaaS Design
 */

'use client';

import React, { useState } from 'react';
import { Task, TaskPriority } from '@/lib/types';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import './TaskItem.css';

/**
 * TaskItem Props
 */
interface TaskItemProps {
  task: Task;
  onToggleComplete: (id: number, completed: boolean) => Promise<void>;
  onEdit: (task: Task) => void;
  onDelete: (id: number) => Promise<void>;
  isSelected?: boolean;
  onSelect?: (task: Task) => void;
}

/**
 * Get priority icon
 */
function getPriorityIcon(priority: TaskPriority): string {
  switch (priority) {
    case TaskPriority.HIGH:
      return '🔥';
    case TaskPriority.MEDIUM:
      return '⚡';
    case TaskPriority.LOW:
      return '📌';
    default:
      return '📌';
  }
}

/**
 * Get priority class
 */
function getPriorityClass(priority: TaskPriority): string {
  switch (priority) {
    case TaskPriority.HIGH:
      return 'high';
    case TaskPriority.MEDIUM:
      return 'medium';
    case TaskPriority.LOW:
      return 'low';
    default:
      return 'low';
  }
}

/**
 * Format due date display
 */
function formatDueDate(dueDate?: string, dueTime?: string): {
  text: string;
  isOverdue: boolean;
  isDueToday: boolean;
} {
  if (!dueDate) {
    return { text: '', isOverdue: false, isDueToday: false };
  }

  const due = new Date(dueDate);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  due.setHours(0, 0, 0, 0);

  const diffTime = due.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  const isOverdue = diffDays < 0;
  const isDueToday = diffDays === 0;

  let text = '';
  if (isOverdue) {
    text = `Overdue by ${Math.abs(diffDays)} day${Math.abs(diffDays) !== 1 ? 's' : ''}`;
  } else if (isDueToday) {
    text = dueTime ? `Due today at ${dueTime}` : 'Due today';
  } else if (diffDays === 1) {
    text = dueTime ? `Due tomorrow at ${dueTime}` : 'Due tomorrow';
  } else if (diffDays <= 7) {
    text = `Due in ${diffDays} days`;
  } else {
    text = `Due ${due.toLocaleDateString()}`;
  }

  return { text, isOverdue, isDueToday };
}

/**
 * TaskItem Component
 */
export default function TaskItem({
  task,
  onToggleComplete,
  onEdit,
  onDelete,
  isSelected = false,
  onSelect,
}: TaskItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const dueDateInfo = formatDueDate(task.due_date, task.due_time);

  /**
   * Handle task click for selection
   */
  const handleTaskClick = () => {
    if (onSelect) {
      onSelect(task);
    }
  };

  /**
   * Handle completion toggle
   */
  const handleToggle = async () => {
    if (isToggling) return;

    setIsToggling(true);
    try {
      await onToggleComplete(task.id, !task.completed);
    } catch (error) {
      console.error('Failed to toggle task:', error);
    } finally {
      setIsToggling(false);
    }
  };

  /**
   * Handle delete
   */
  const handleDelete = async () => {
    setShowDeleteConfirm(true);
  };

  /**
   * Confirm delete
   */
  const confirmDelete = async () => {
    if (isDeleting) return;

    setIsDeleting(true);
    setShowDeleteConfirm(false);

    try {
      await onDelete(task.id);
    } catch (error) {
      console.error('Failed to delete task:', error);
      setIsDeleting(false);
    }
  };

  /**
   * Cancel delete
   */
  const cancelDelete = () => {
    setShowDeleteConfirm(false);
  };

  return (
    <div
      className={`task-item ${
        task.priority === TaskPriority.HIGH ? 'priority-high' : ''
      } ${task.completed ? 'completed' : ''} ${
        isDeleting ? 'deleting' : ''
      } ${isSelected ? 'selected' : ''}`}
      onClick={handleTaskClick}
    >
      {/* Hover gradient effect */}
      <div className="task-item-gradient" />

      <div className="task-item-content">
        {/* Header Row */}
        <div className="task-item-header">
          {/* Checkbox */}
          <button
            onClick={handleToggle}
            disabled={isToggling}
            className={`task-item-checkbox ${
              task.completed ? 'checked' : ''
            } ${isToggling ? 'disabled' : ''}`}
          >
            {task.completed && (
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={3}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            )}
          </button>

          {/* Content */}
          <div className="task-item-body">
            {/* Title */}
            <h3
              className={`task-item-title ${task.completed ? 'completed' : ''}`}
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {task.title}
            </h3>

            {/* Badges Row */}
            <div className="task-item-badges">
              {/* Priority Badge */}
              <span className={`task-item-priority ${getPriorityClass(task.priority)}`}>
                {getPriorityIcon(task.priority)} {task.priority}
              </span>

              {/* Due Date Badge */}
              {dueDateInfo.text && (
                <span
                  className={`task-item-due ${
                    dueDateInfo.isOverdue
                      ? 'overdue'
                      : dueDateInfo.isDueToday
                      ? 'today'
                      : 'upcoming'
                  }`}
                >
                  🗓️ {dueDateInfo.text}
                </span>
              )}

              {/* Tag Badges */}
              {task.tags && task.tags.length > 0 && (
                <>
                  {task.tags.map((tag) => (
                    <span key={tag.id} className="task-item-tag">
                      🏷️ {tag.name}
                    </span>
                  ))}
                </>
              )}

              {/* Recurring Badge */}
              {task.recurrence_pattern && (
                <span className="task-item-recurring">
                  🔄 Recurring
                </span>
              )}
            </div>

            {/* Description (Expanded) */}
            {isExpanded && task.description && (
              <p className="task-item-description">
                {task.description}
              </p>
            )}
          </div>

          {/* Action Buttons */}
          <div className="task-item-actions">
            {/* Edit Button */}
            <button
              onClick={() => onEdit(task)}
              className="task-item-action edit"
              title="Edit task"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
            </button>

            {/* Delete Button */}
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="task-item-action delete"
              title="Delete task"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Expand/Collapse Indicator */}
        {task.description && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="task-item-expand"
          >
            {isExpanded ? '▲ Show less' : '▼ Show more'}
          </button>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Delete Task"
        message={`Are you sure you want to delete "${task.title}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        variant="danger"
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </div>
  );
}
