/**
 * RecurrenceSelector Component
 * Dark Golden Theme - Modern SaaS Design
 */

'use client';

import React, { useState, useEffect } from 'react';
import { RecurrencePattern } from '@/lib/types';
import './RecurrenceSelector.css';

export interface RecurrenceSelectorProps {
  value?: RecurrencePattern;
  onChange: (pattern?: RecurrencePattern) => void;
  disabled?: boolean;
}

const DAYS_OF_WEEK = [
  { label: 'Sun', value: 0 },
  { label: 'Mon', value: 1 },
  { label: 'Tue', value: 2 },
  { label: 'Wed', value: 3 },
  { label: 'Thu', value: 4 },
  { label: 'Fri', value: 5 },
  { label: 'Sat', value: 6 },
];

export default function RecurrenceSelector({
  value,
  onChange,
  disabled = false,
}: RecurrenceSelectorProps) {
  const [isEnabled, setIsEnabled] = useState(!!value);
  const [type, setType] = useState<'daily' | 'weekly' | 'monthly' | 'custom'>(
    value?.type || 'daily'
  );
  const [interval, setInterval] = useState(value?.interval || 1);
  const [daysOfWeek, setDaysOfWeek] = useState<number[]>(value?.days_of_week || []);
  const [dayOfMonth, setDayOfMonth] = useState(value?.day_of_month || 1);
  const [endDate, setEndDate] = useState(value?.end_date || '');

  /**
   * Update parent when values change
   */
  useEffect(() => {
    if (!isEnabled) {
      onChange(undefined);
      return;
    }

    const pattern: RecurrencePattern = {
      type,
      interval,
      days_of_week: type === 'weekly' ? daysOfWeek : undefined,
      day_of_month: type === 'monthly' ? dayOfMonth : undefined,
      end_date: endDate || undefined,
    };

    onChange(pattern);
  }, [isEnabled, type, interval, daysOfWeek, dayOfMonth, endDate, onChange]);

  /**
   * Toggle day of week
   */
  const toggleDayOfWeek = (day: number) => {
    if (daysOfWeek.includes(day)) {
      setDaysOfWeek(daysOfWeek.filter((d) => d !== day));
    } else {
      setDaysOfWeek([...daysOfWeek, day].sort());
    }
  };

  /**
   * Handle enable/disable
   */
  const handleToggle = () => {
    setIsEnabled(!isEnabled);
    if (isEnabled) {
      onChange(undefined);
    }
  };

  return (
    <div className="recurrence-selector">
      <div className="recurrence-toggle">
        <label className="recurrence-toggle-label">
          <div
            className={`recurrence-checkbox ${isEnabled ? 'checked' : ''}`}
            onClick={() => !disabled && handleToggle()}
          />
          <span className="recurrence-toggle-text">Repeat this task</span>
        </label>
        <svg className="recurrence-toggle-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </div>

      {isEnabled && (
        <div className="recurrence-options">
          <div className="recurrence-type-grid">
            {(['daily', 'weekly', 'monthly', 'custom'] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setType(t)}
                disabled={disabled}
                className={`recurrence-type-btn ${type === t ? 'active' : ''}`}
              >
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>

          <div className="recurrence-interval">
            <label className="recurrence-label">Every</label>
            <div className="recurrence-interval-wrapper">
              <input
                type="number"
                min="1"
                max="365"
                value={interval}
                onChange={(e) => setInterval(parseInt(e.target.value) || 1)}
                disabled={disabled}
                className="recurrence-input"
              />
              <span className="recurrence-interval-text">
                {type === 'daily' && `day${interval > 1 ? 's' : ''}`}
                {type === 'weekly' && `week${interval > 1 ? 's' : ''}`}
                {type === 'monthly' && `month${interval > 1 ? 's' : ''}`}
                {type === 'custom' && 'days'}
              </span>
            </div>
          </div>

          {type === 'weekly' && (
            <div className="recurrence-interval">
              <label className="recurrence-label">On these days</label>
              <div className="recurrence-days-grid">
                {DAYS_OF_WEEK.map((day) => (
                  <button
                    key={day.value}
                    type="button"
                    onClick={() => toggleDayOfWeek(day.value)}
                    disabled={disabled}
                    className={`recurrence-day-btn ${daysOfWeek.includes(day.value) ? 'active' : ''}`}
                  >
                    {day.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {type === 'monthly' && (
            <div className="recurrence-day-month">
              <label className="recurrence-label">On day</label>
              <input
                type="number"
                min="1"
                max="31"
                value={dayOfMonth}
                onChange={(e) => setDayOfMonth(parseInt(e.target.value) || 1)}
                disabled={disabled}
                className="recurrence-input"
              />
            </div>
          )}

          <div className="recurrence-end-date">
            <label className="recurrence-label">End date (optional)</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              disabled={disabled}
              className="recurrence-input"
              style={{ width: '100%' }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
