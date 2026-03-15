/**
 * SortDropdown Component
 * Dark Golden Theme - Modern SaaS Design
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { TaskSortBy, TaskSortOrder } from '@/lib/types';
import './SortDropdown.css';

export interface SortOption {
  sort_by: TaskSortBy;
  sort_order: TaskSortOrder;
}

export interface SortDropdownProps {
  currentSort: SortOption;
  onChange: (sort: SortOption) => void;
}

interface SortConfig {
  label: string;
  icon: string;
  sort_by: TaskSortBy;
}

const SORT_OPTIONS: SortConfig[] = [
  { label: 'Created Date', icon: '📅', sort_by: 'created_at' },
  { label: 'Due Date', icon: '⏰', sort_by: 'due_date' },
  { label: 'Priority', icon: '🔥', sort_by: 'priority' },
  { label: 'Title', icon: '📝', sort_by: 'title' },
];

export default function SortDropdown({ currentSort, onChange }: SortDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  /**
   * Get current sort label
   */
  const getCurrentLabel = () => {
    const option = SORT_OPTIONS.find((opt) => opt.sort_by === currentSort.sort_by);
    return option ? option.label : 'Sort';
  };

  /**
   * Handle click outside
   */
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  /**
   * Handle sort change
   */
  const handleSortChange = (sort_by: TaskSortBy) => {
    // If clicking the same sort, toggle order
    if (sort_by === currentSort.sort_by) {
      onChange({
        sort_by,
        sort_order: currentSort.sort_order === 'asc' ? 'desc' : 'asc',
      });
    } else {
      // Default to descending for new sort
      onChange({
        sort_by,
        sort_order: 'desc',
      });
    }
    setIsOpen(false);
  };

  return (
    <div ref={dropdownRef} className="sort-dropdown">
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="sort-dropdown-trigger"
      >
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
          />
        </svg>
        <span className="sort-dropdown-label">{getCurrentLabel()}</span>
        <svg
          className={`sort-dropdown-arrow ${isOpen ? 'open' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="sort-dropdown-menu">
          {/* Header */}
          <div className="sort-dropdown-header">
            <h3 className="sort-dropdown-header-title">Sort by</h3>
          </div>

          {/* Sort Options */}
          <div className="sort-dropdown-options">
            {SORT_OPTIONS.map((option) => {
              const isActive = currentSort.sort_by === option.sort_by;
              return (
                <button
                  key={option.sort_by}
                  onClick={() => handleSortChange(option.sort_by)}
                  className={`sort-dropdown-option ${isActive ? 'active' : ''}`}
                >
                  <div className="sort-dropdown-option-left">
                    <span className="sort-dropdown-option-icon">{option.icon}</span>
                    <span className="sort-dropdown-option-label">{option.label}</span>
                  </div>

                  {/* Sort Order Indicator */}
                  {isActive && (
                    <div className="sort-dropdown-order">
                      <svg
                        className={`sort-dropdown-order-arrow ${
                          currentSort.sort_order === 'asc' ? 'asc' : ''
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                      <span className="sort-dropdown-order-text">
                        {currentSort.sort_order === 'asc' ? 'A-Z' : 'Z-A'}
                      </span>
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Footer Hint */}
          <div className="sort-dropdown-footer">
            <p className="sort-dropdown-footer-text">
              Click again to reverse order
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
