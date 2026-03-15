/**
 * FilterPanel Component
 * Filter icon button with dropdown for task filtering
 * Dark Golden Theme
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { TaskPriority, TaskFilterOptions } from '@/lib/types';
import { useTags } from '@/hooks/useTags';
import './FilterPanel.css';

export interface FilterPanelProps {
  filters: TaskFilterOptions;
  onFilterChange: (filters: TaskFilterOptions) => void;
  taskCount: number;
}

export default function FilterPanel({
  filters,
  onFilterChange,
  taskCount: _taskCount,
}: FilterPanelProps) {
  const { tags } = useTags();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  /**
   * Close dropdown when clicking outside
   */
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  /**
   * Toggle tag filter
   */
  const toggleTagFilter = (tagId: number) => {
    const currentTagIds = filters.tag_ids || [];
    const newTagIds = currentTagIds.includes(tagId)
      ? currentTagIds.filter((id) => id !== tagId)
      : [...currentTagIds, tagId];

    onFilterChange({
      ...filters,
      tag_ids: newTagIds.length > 0 ? newTagIds : undefined,
    });
  };

  /**
   * Set priority filter
   */
  const setPriorityFilter = (priority?: TaskPriority) => {
    onFilterChange({
      ...filters,
      priority,
    });
  };

  /**
   * Set status filter
   */
  const setStatusFilter = (status: 'all' | 'pending' | 'completed') => {
    onFilterChange({
      ...filters,
      status,
    });
  };

  /**
   * Clear all filters
   */
  const clearAllFilters = () => {
    onFilterChange({
      status: 'all',
    });
  };

  /**
   * Check if any filters are active
   */
  const hasActiveFilters =
    filters.priority ||
    (filters.tag_ids && filters.tag_ids.length > 0) ||
    (filters.status && filters.status !== 'all');

  /**
   * Count active filters
   */
  const activeFiltersCount = [
    filters.priority ? 1 : 0,
    filters.tag_ids?.length || 0,
    filters.status && filters.status !== 'all' ? 1 : 0,
  ].reduce((a, b) => a + b, 0);

  /**
   * Get priority icon
   */
  const getPriorityIcon = (priority: TaskPriority) => {
    switch (priority) {
      case TaskPriority.HIGH:
        return '🔥';
      case TaskPriority.MEDIUM:
        return '⚡';
      case TaskPriority.LOW:
        return '📌';
      default:
        return '⚪';
    }
  };

  return (
    <div className="filter-dropdown" ref={dropdownRef}>
      {/* Filter Icon Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="filter-dropdown-trigger"
        aria-label="Filters"
      >
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
          />
        </svg>
        <span className="filter-dropdown-label">Filters</span>
        {activeFiltersCount > 0 && (
          <span className="filter-dropdown-badge">{activeFiltersCount}</span>
        )}
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="filter-dropdown-menu">
          {/* Header */}
          <div className="filter-dropdown-header">
            <h3 className="filter-dropdown-header-title">Filter Tasks</h3>
            {hasActiveFilters && (
              <button onClick={clearAllFilters} className="filter-dropdown-clear">
                Clear All
              </button>
            )}
          </div>

          {/* Filter Sections */}
          <div className="filter-dropdown-body">
            {/* Status Section */}
            <div className="filter-dropdown-section">
              <label className="filter-dropdown-section-label">Status</label>
              <div className="filter-dropdown-radio-group">
                <label className="filter-dropdown-radio">
                  <input
                    type="radio"
                    name="status"
                    checked={(filters.status || 'all') === 'all'}
                    onChange={() => setStatusFilter('all')}
                  />
                  <span className="filter-dropdown-radio-custom"></span>
                  <span className="filter-dropdown-radio-label">All Tasks</span>
                </label>
                <label className="filter-dropdown-radio">
                  <input
                    type="radio"
                    name="status"
                    checked={filters.status === 'pending'}
                    onChange={() => setStatusFilter('pending')}
                  />
                  <span className="filter-dropdown-radio-custom"></span>
                  <span className="filter-dropdown-radio-label">Pending</span>
                </label>
                <label className="filter-dropdown-radio">
                  <input
                    type="radio"
                    name="status"
                    checked={filters.status === 'completed'}
                    onChange={() => setStatusFilter('completed')}
                  />
                  <span className="filter-dropdown-radio-custom"></span>
                  <span className="filter-dropdown-radio-label">Completed</span>
                </label>
              </div>
            </div>

            {/* Priority Section */}
            <div className="filter-dropdown-section">
              <label className="filter-dropdown-section-label">Priority</label>
              <div className="filter-dropdown-radio-group">
                <label className="filter-dropdown-radio">
                  <input
                    type="radio"
                    name="priority"
                    checked={!filters.priority}
                    onChange={() => setPriorityFilter(undefined)}
                  />
                  <span className="filter-dropdown-radio-custom"></span>
                  <span className="filter-dropdown-radio-label">
                    <span className="filter-priority-icon">⚪</span>
                    All Priorities
                  </span>
                </label>
                {Object.values(TaskPriority).map((priority) => (
                  <label key={priority} className="filter-dropdown-radio">
                    <input
                      type="radio"
                      name="priority"
                      checked={filters.priority === priority}
                      onChange={() => setPriorityFilter(priority)}
                    />
                    <span className="filter-dropdown-radio-custom"></span>
                    <span className="filter-dropdown-radio-label">
                      <span className="filter-priority-icon">{getPriorityIcon(priority)}</span>
                      {priority.charAt(0).toUpperCase() + priority.slice(1)}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Tags Section */}
            {tags.length > 0 && (
              <div className="filter-dropdown-section">
                <label className="filter-dropdown-section-label">Tags</label>
                <div className="filter-dropdown-checkbox-group">
                  {tags.map((tag) => {
                    const isSelected = filters.tag_ids?.includes(tag.id) || false;
                    return (
                      <label key={tag.id} className="filter-dropdown-checkbox">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleTagFilter(tag.id)}
                        />
                        <span className="filter-dropdown-checkbox-custom">
                          {isSelected && (
                            <svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={3}
                                d="M5 13l4 4L19 7"
                              />
                            </svg>
                          )}
                        </span>
                        <span className="filter-dropdown-checkbox-label">{tag.name}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
