/**
 * BulkActionsToolbar Component
 * Floating toolbar for bulk task operations
 */

'use client';

import React from 'react';
import './BulkActionsToolbar.css';

interface BulkActionsToolbarProps {
  selectedCount: number;
  onMarkComplete: () => void;
  onMarkIncomplete: () => void;
  onDelete: () => void;
  onCancel: () => void;
}

export default function BulkActionsToolbar({
  selectedCount,
  onMarkComplete,
  onMarkIncomplete,
  onDelete,
  onCancel,
}: BulkActionsToolbarProps) {
  if (selectedCount === 0) return null;

  return (
    <div className="bulk-actions-toolbar">
      <div className="bulk-actions-count">
        <div className="bulk-actions-count-badge">{selectedCount}</div>
        <span className="bulk-actions-count-text">
          {selectedCount === 1 ? 'task selected' : 'tasks selected'}
        </span>
      </div>

      <div className="bulk-actions-buttons">
        <button
          className="bulk-action-btn complete"
          onClick={onMarkComplete}
          title="Mark selected tasks as complete"
        >
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>Complete</span>
        </button>

        <button
          className="bulk-action-btn"
          onClick={onMarkIncomplete}
          title="Mark selected tasks as incomplete"
        >
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>Incomplete</span>
        </button>

        <button
          className="bulk-action-btn delete"
          onClick={onDelete}
          title="Delete selected tasks"
        >
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
          <span>Delete</span>
        </button>

        <button
          className="bulk-action-btn cancel"
          onClick={onCancel}
          title="Cancel bulk selection"
        >
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
          <span>Cancel</span>
        </button>
      </div>
    </div>
  );
}
