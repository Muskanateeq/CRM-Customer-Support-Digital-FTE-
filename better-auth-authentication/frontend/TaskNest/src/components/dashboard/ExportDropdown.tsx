/**
 * ExportDropdown Component
 * Dropdown for exporting tasks to CSV or JSON
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Task } from '@/lib/types';
import { exportToCSV, exportToJSON } from '@/lib/taskExport';
import './ExportDropdown.css';

interface ExportDropdownProps {
  tasks: Task[];
}

export default function ExportDropdown({ tasks }: ExportDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

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

  // Handle CSV export
  const handleExportCSV = () => {
    exportToCSV(tasks);
    setIsOpen(false);
  };

  // Handle JSON export
  const handleExportJSON = () => {
    exportToJSON(tasks);
    setIsOpen(false);
  };

  return (
    <div className="export-dropdown" ref={dropdownRef}>
      <button
        className="export-dropdown-trigger"
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="true"
        aria-expanded={isOpen}
        aria-label="Export tasks"
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
            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
          />
        </svg>
        <span>Export</span>
      </button>

      {isOpen && (
        <div className="export-dropdown-menu" role="menu">
          <button
            className="export-dropdown-item"
            onClick={handleExportCSV}
            role="menuitem"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <span>Export as CSV</span>
          </button>

          <button
            className="export-dropdown-item"
            onClick={handleExportJSON}
            role="menuitem"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
              />
            </svg>
            <span>Export as JSON</span>
          </button>
        </div>
      )}
    </div>
  );
}
