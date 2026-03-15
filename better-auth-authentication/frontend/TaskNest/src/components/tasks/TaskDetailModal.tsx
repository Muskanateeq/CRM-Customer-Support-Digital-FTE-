/**
 * TaskDetailModal Component
 * Displays comprehensive task details in a modal
 */

'use client';

import React from 'react';
import { Task, TaskPriority, RecurrencePattern } from '@/lib/types';
import Modal from '@/components/ui/Modal';
import { useFocusTrap } from '@/hooks/useFocusTrap';
import './TaskDetailModal.css';

interface TaskDetailModalProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: number) => void;
}

/**
 * Format date for display
 */
function formatDate(dateString?: string): string {
  if (!dateString) return 'Not set';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Format time for display
 */
function formatTime(timeString?: string): string {
  if (!timeString) return '';
  return timeString;
}

/**
 * Check if task is overdue
 */
function isOverdue(dueDate?: string): boolean {
  if (!dueDate) return false;
  const due = new Date(dueDate);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  due.setHours(0, 0, 0, 0);
  return due < today;
}

/**
 * Get priority badge class
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
 * Format recurrence pattern for display
 */
function formatRecurrence(pattern?: RecurrencePattern): string {
  if (!pattern) return 'None';

  const { type, interval } = pattern;

  if (interval === 1) {
    return `Every ${type}`;
  } else {
    return `Every ${interval} ${type}${interval > 1 ? 's' : ''}`;
  }
}

export default function TaskDetailModal({
  task,
  isOpen,
  onClose,
  onEdit,
  onDelete,
}: TaskDetailModalProps) {
  // Implement focus trap for accessibility
  const modalRef = useFocusTrap<HTMLDivElement>({
    isActive: isOpen,
    onEscape: onClose,
    initialFocus: true,
    returnFocus: true,
  });

  if (!task) return null;

  const overdue = isOverdue(task.due_date);

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Task Details">
      <div className="task-detail-modal" ref={modalRef}>
        {/* Header with Title and Status */}
        <div className="task-detail-header">
          <h2 className="task-detail-title">{task.title}</h2>
          <div className="task-detail-status">
            {task.completed ? (
              <span className="status-badge completed">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Completed
              </span>
            ) : (
              <span className="status-badge active">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
                Active
              </span>
            )}
          </div>
        </div>

        {/* Priority Badge */}
        <div className="task-detail-section">
          <label className="task-detail-label">Priority</label>
          <div className={`priority-badge ${getPriorityClass(task.priority)}`}>
            {getPriorityIcon(task.priority)} {task.priority}
          </div>
        </div>

        {/* Description */}
        {task.description && (
          <div className="task-detail-section">
            <label className="task-detail-label">Description</label>
            <p className="task-detail-description">{task.description}</p>
          </div>
        )}

        {/* Due Date and Time */}
        <div className="task-detail-section">
          <label className="task-detail-label">Due Date</label>
          <div className={`task-detail-due ${overdue ? 'overdue' : ''}`}>
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <span>
              {formatDate(task.due_date)}
              {task.due_time && ` at ${formatTime(task.due_time)}`}
            </span>
            {overdue && <span className="overdue-indicator">Overdue</span>}
          </div>
        </div>

        {/* Tags */}
        {task.tags && task.tags.length > 0 && (
          <div className="task-detail-section">
            <label className="task-detail-label">Tags</label>
            <div className="task-detail-tags">
              {task.tags.map((tag) => (
                <span key={tag.id} className="tag-chip">
                  {tag.name}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Recurrence Pattern */}
        {task.recurrence_pattern && (
          <div className="task-detail-section">
            <label className="task-detail-label">Recurrence</label>
            <div className="task-detail-recurrence">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              <span>{formatRecurrence(task.recurrence_pattern)}</span>
            </div>
          </div>
        )}

        {/* Timestamps */}
        <div className="task-detail-section">
          <label className="task-detail-label">Created</label>
          <div className="task-detail-timestamp">
            {formatDate(task.created_at)}
          </div>
        </div>

        {task.updated_at && task.updated_at !== task.created_at && (
          <div className="task-detail-section">
            <label className="task-detail-label">Last Updated</label>
            <div className="task-detail-timestamp">
              {formatDate(task.updated_at)}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="task-detail-actions">
          {onEdit && (
            <button
              onClick={() => {
                onEdit(task);
                onClose();
              }}
              className="task-detail-btn edit"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
              Edit Task
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => {
                onDelete(task.id);
                onClose();
              }}
              className="task-detail-btn delete"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
              Delete Task
            </button>
          )}
        </div>
      </div>
    </Modal>
  );
}
