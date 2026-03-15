/**
 * GroupByDropdown Component
 * Dropdown for selecting task grouping option
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import './GroupByDropdown.css';

export type GroupByOption = 'none' | 'date' | 'priority' | 'status';

interface GroupByDropdownProps {
  value: GroupByOption;
  onChange: (value: GroupByOption) => void;
}

const GROUP_OPTIONS = [
  { value: 'none' as GroupByOption, label: 'No Grouping' },
  { value: 'date' as GroupByOption, label: 'Group by Date' },
  { value: 'priority' as GroupByOption, label: 'Group by Priority' },
  { value: 'status' as GroupByOption, label: 'Group by Status' },
];

export default function GroupByDropdown({ value, onChange }: GroupByDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Get current option label
  const currentOption = GROUP_OPTIONS.find(opt => opt.value === value);
  const currentLabel = currentOption?.label || 'Group by';

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

  // Handle option selection
  const handleSelect = (option: GroupByOption) => {
    onChange(option);
    setIsOpen(false);
  };

  return (
    <div className="group-by-dropdown" ref={dropdownRef}>
      <button
        className="group-by-dropdown-trigger"
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="true"
        aria-expanded={isOpen}
        aria-label="Group tasks"
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
            d="M4 6h16M4 10h16M4 14h16M4 18h16"
          />
        </svg>
        <span>{currentLabel}</span>
        <svg
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          width="16"
          height="16"
          className={`group-by-dropdown-arrow ${isOpen ? 'open' : ''}`}
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
        <div className="group-by-dropdown-menu" role="menu">
          {GROUP_OPTIONS.map((option) => (
            <button
              key={option.value}
              className={`group-by-dropdown-item ${
                value === option.value ? 'active' : ''
              }`}
              onClick={() => handleSelect(option.value)}
              role="menuitem"
            >
              <span>{option.label}</span>
              {value === option.value && (
                <svg
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  width="20"
                  height="20"
                  className="group-by-dropdown-item-check"
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
