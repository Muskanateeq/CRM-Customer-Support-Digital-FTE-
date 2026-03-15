/**
 * FilterPanel Component
 * Advanced filtering panel for tasks
 */

'use client';

import React from 'react';
import { TaskFilters } from '@/hooks/useTasks';
import { TaskPriority } from '@/lib/types';
import './FilterPanel.css';

interface FilterPanelProps {
  filters: TaskFilters;
  onFiltersChange: (filters: TaskFilters) => void;
  onClearFilters: () => void;
  availableTags?: Array<{ id: number; name: string; color?: string }>;
}

export default function FilterPanel({
  filters,
  onFiltersChange,
  onClearFilters,
  availableTags = [],
}: FilterPanelProps) {
  // Count active filters
  const activeFilterCount = [
    filters.status && filters.status !== 'all' ? 1 : 0,
    filters.priority ? 1 : 0,
    filters.tag_ids && filters.tag_ids.length > 0 ? 1 : 0,
    filters.due_date_filter ? 1 : 0,
  ].reduce((sum, val) => sum + val, 0);

  // Handle status filter change
  const handleStatusChange = (status: 'all' | 'pending' | 'completed') => {
    onFiltersChange({ ...filters, status });
  };

  // Handle priority filter change
  const handlePriorityChange = (priority: TaskPriority | undefined) => {
    onFiltersChange({ ...filters, priority });
  };

  // Handle tag filter change
  const handleTagToggle = (tagId: number) => {
    const currentTags = filters.tag_ids || [];
    const newTags = currentTags.includes(tagId)
      ? currentTags.filter(id => id !== tagId)
      : [...currentTags, tagId];
    onFiltersChange({ ...filters, tag_ids: newTags });
  };

  // Handle due date filter change
  const handleDueDateChange = (
    dueDateFilter: 'overdue' | 'today' | 'week' | 'month' | 'none' | undefined
  ) => {
    onFiltersChange({ ...filters, due_date_filter: dueDateFilter });
  };

  return (
    <div className="filter-panel">
      <div className="filter-panel-header">
        <h3 className="filter-panel-title">
          Filters
          {activeFilterCount > 0 && (
            <span className="filter-panel-badge">{activeFilterCount}</span>
          )}
        </h3>
        {activeFilterCount > 0 && (
          <button
            className="filter-panel-clear"
            onClick={onClearFilters}
            aria-label="Clear all filters"
          >
            Clear All
          </button>
        )}
      </div>

      {/* Status Filter */}
      <div className="filter-section">
        <label className="filter-section-label">Status</label>
        <div className="filter-options">
          <button
            className={`filter-option ${
              !filters.status || filters.status === 'all' ? 'active' : ''
            }`}
            onClick={() => handleStatusChange('all')}
          >
            All
          </button>
          <button
            className={`filter-option ${
              filters.status === 'pending' ? 'active' : ''
            }`}
            onClick={() => handleStatusChange('pending')}
          >
            Active
          </button>
          <button
            className={`filter-option ${
              filters.status === 'completed' ? 'active' : ''
            }`}
            onClick={() => handleStatusChange('completed')}
          >
            Completed
          </button>
        </div>
      </div>

      {/* Priority Filter */}
      <div className="filter-section">
        <label className="filter-section-label">Priority</label>
        <div className="filter-options">
          <button
            className={`filter-option ${!filters.priority ? 'active' : ''}`}
            onClick={() => handlePriorityChange(undefined)}
          >
            All
          </button>
          <button
            className={`filter-option priority-high ${
              filters.priority === TaskPriority.HIGH ? 'active' : ''
            }`}
            onClick={() => handlePriorityChange(TaskPriority.HIGH)}
          >
            High
          </button>
          <button
            className={`filter-option priority-medium ${
              filters.priority === TaskPriority.MEDIUM ? 'active' : ''
            }`}
            onClick={() => handlePriorityChange(TaskPriority.MEDIUM)}
          >
            Medium
          </button>
          <button
            className={`filter-option priority-low ${
              filters.priority === TaskPriority.LOW ? 'active' : ''
            }`}
            onClick={() => handlePriorityChange(TaskPriority.LOW)}
          >
            Low
          </button>
        </div>
      </div>

      {/* Due Date Filter */}
      <div className="filter-section">
        <label className="filter-section-label">Due Date</label>
        <div className="filter-options">
          <button
            className={`filter-option ${
              !filters.due_date_filter ? 'active' : ''
            }`}
            onClick={() => handleDueDateChange(undefined)}
          >
            All
          </button>
          <button
            className={`filter-option ${
              filters.due_date_filter === 'overdue' ? 'active' : ''
            }`}
            onClick={() => handleDueDateChange('overdue')}
          >
            Overdue
          </button>
          <button
            className={`filter-option ${
              filters.due_date_filter === 'today' ? 'active' : ''
            }`}
            onClick={() => handleDueDateChange('today')}
          >
            Today
          </button>
          <button
            className={`filter-option ${
              filters.due_date_filter === 'week' ? 'active' : ''
            }`}
            onClick={() => handleDueDateChange('week')}
          >
            This Week
          </button>
          <button
            className={`filter-option ${
              filters.due_date_filter === 'month' ? 'active' : ''
            }`}
            onClick={() => handleDueDateChange('month')}
          >
            This Month
          </button>
          <button
            className={`filter-option ${
              filters.due_date_filter === 'none' ? 'active' : ''
            }`}
            onClick={() => handleDueDateChange('none')}
          >
            No Due Date
          </button>
        </div>
      </div>

      {/* Tags Filter */}
      {availableTags.length > 0 && (
        <div className="filter-section">
          <label className="filter-section-label">Tags</label>
          <div className="filter-tags">
            {availableTags.map((tag) => (
              <button
                key={tag.id}
                className={`filter-tag ${
                  filters.tag_ids?.includes(tag.id) ? 'active' : ''
                }`}
                onClick={() => handleTagToggle(tag.id)}
                style={{
                  backgroundColor: filters.tag_ids?.includes(tag.id)
                    ? tag.color || '#e49b0f'
                    : 'transparent',
                  borderColor: tag.color || '#e5e7eb',
                  color: filters.tag_ids?.includes(tag.id) ? 'white' : '#374151',
                }}
              >
                {tag.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
