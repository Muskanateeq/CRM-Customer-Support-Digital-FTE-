/**
 * SortDropdown Component
 * Dropdown for selecting task sort options
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { TaskSort } from '@/hooks/useTasks';
import './SortDropdown.css';

interface SortDropdownProps {
  sort: TaskSort;
  onSortChange: (sort: TaskSort) => void;
}

type SortOption = {
  label: string;
  value: TaskSort['sort_by'];
  description: string;
};

const SORT_OPTIONS: SortOption[] = [
  {
    label: 'Created Date',
    value: 'created_at',
    description: 'Newest first',
  },
  {
    label: 'Due Date',
    value: 'due_date',
    description: 'Overdue first, then upcoming',
  },
  {
    label: 'Priority',
    value: 'priority',
    description: 'High → Medium → Low',
  },
  {
    label: 'Title',
    value: 'title',
    description: 'Alphabetical (A-Z)',
  },
];

export default function SortDropdown({ sort, onSortChange }: SortDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Get current sort option label
  const currentOption = SORT_OPTIONS.find(opt => opt.value === sort.sort_by);
  const currentLabel = currentOption?.label || 'Sort';

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // Handle sort option selection
  const handleSelectSort = (sortBy: TaskSort['sort_by']) => {
    // Determine sort order based on sort type
    let sortOrder: 'asc' | 'desc' = 'desc';

    if (sortBy === 'title') {
      sortOrder = 'asc'; // A-Z
    } else if (sortBy === 'due_date') {
      sortOrder = 'asc'; // Overdue first (handled by backend)
    } else if (sortBy === 'priority') {
      sortOrder = 'desc'; // High → Medium → Low (handled by backend)
    } else if (sortBy === 'created_at') {
      sortOrder = 'desc'; // Newest first
    }

    onSortChange({ sort_by: sortBy, sort_order: sortOrder });
    setIsOpen(false);
  };

  return (
    <div className="sort-dropdown" ref={dropdownRef}>
      <button
        className="sort-dropdown-trigger"
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="true"
        aria-expanded={isOpen}
        aria-label="Sort tasks"
      >
        <svg
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          width="20"
          height="20"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
          />
        </svg>
        <span>{currentLabel}</span>
        <svg
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          width="16"
          height="16"
          className={`sort-dropdown-arrow ${isOpen ? 'open' : ''}`}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {isOpen && (
        <div className="sort-dropdown-menu" role="menu">
          {SORT_OPTIONS.map((option) => (
            <button
              key={option.value}
              className={`sort-dropdown-item ${
                sort.sort_by === option.value ? 'active' : ''
              }`}
              onClick={() => handleSelectSort(option.value)}
              role="menuitem"
            >
              <div className="sort-dropdown-item-content">
                <span className="sort-dropdown-item-label">{option.label}</span>
                <span className="sort-dropdown-item-description">
                  {option.description}
                </span>
              </div>
              {sort.sort_by === option.value && (
                <svg
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  width="20"
                  height="20"
                  className="sort-dropdown-item-check"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
