/**
 * SearchBar Component
 * Dark Golden Theme - Modern SaaS Design
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import './SearchBar.css';

export interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  debounceMs?: number;
}

export default function SearchBar({
  value,
  onChange,
  placeholder = 'Search tasks...',
  debounceMs = 300,
}: SearchBarProps) {
  const [localValue, setLocalValue] = useState(value);
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | undefined>(undefined);

  /**
   * Sync local value with prop value
   */
  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  /**
   * Debounced onChange
   */
  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(() => {
      if (localValue !== value) {
        onChange(localValue);
      }
    }, debounceMs);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [localValue, value, onChange, debounceMs]);

  /**
   * Handle keyboard shortcut (Ctrl/Cmd + K)
   */
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  /**
   * Handle clear
   */
  const handleClear = () => {
    setLocalValue('');
    onChange('');
    inputRef.current?.focus();
  };

  return (
    <div className="search-bar">
      {/* Search Icon */}
      <div className={`search-bar-icon ${isFocused ? 'focused' : ''}`}>
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>

      {/* Input */}
      <input
        ref={inputRef}
        type="text"
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder={placeholder}
        className="search-bar-input"
      />

      {/* Right Side Actions */}
      <div className="search-bar-actions">
        {/* Clear Button */}
        {localValue && (
          <button
            onClick={handleClear}
            className="search-bar-clear"
            aria-label="Clear search"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}

        {/* Keyboard Shortcut Hint */}
        {!isFocused && !localValue && (
          <div className="search-bar-shortcut">
            <kbd>⌘</kbd>
            <kbd>K</kbd>
          </div>
        )}
      </div>

      {/* Search Results Count (if searching) */}
      {localValue && (
        <div className="search-bar-indicator">
          Searching for &quot;{localValue}&quot;...
        </div>
      )}
    </div>
  );
}
