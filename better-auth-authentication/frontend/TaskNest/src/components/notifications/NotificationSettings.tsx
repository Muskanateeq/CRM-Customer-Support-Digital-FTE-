/**
 * NotificationSettings Component - Notification Preferences
 *
 * Features:
 * - Enable/disable notifications
 * - Configure notification timing (minutes before due)
 * - Test notification button
 * - Permission status display
 * - LocalStorage persistence
 */

'use client';

import React, { useState, useEffect } from 'react';
import Button from '@/components/ui/Button';
import './NotificationSettings.css';

export interface NotificationSettingsProps {
  isEnabled: boolean;
  permission: NotificationPermission;
  onToggle: () => void;
  onRequestPermission: () => Promise<void>;
}

export default function NotificationSettings({
  isEnabled,
  permission,
  onToggle,
  onRequestPermission,
}: NotificationSettingsProps) {
  const [notifyBefore, setNotifyBefore] = useState(15);
  const [isSaving, setIsSaving] = useState(false);

  /**
   * Load settings from localStorage
   */
  useEffect(() => {
    const saved = localStorage.getItem('notification_minutes_before');
    if (saved) {
      setNotifyBefore(parseInt(saved, 10));
    }
  }, []);

  /**
   * Save notification timing preference
   */
  const handleSaveSettings = () => {
    setIsSaving(true);
    localStorage.setItem('notification_minutes_before', String(notifyBefore));
    setTimeout(() => {
      setIsSaving(false);
    }, 500);
  };

  /**
   * Send test notification
   */
  const handleTestNotification = () => {
    if (permission === 'granted') {
      new Notification('🔔 Test Notification', {
        body: 'This is how your task reminders will look!',
        icon: '/favicon.ico',
        badge: '/favicon.ico',
      });
    }
  };

  /**
   * Get permission status text
   */
  const getPermissionText = () => {
    switch (permission) {
      case 'granted':
        return 'Granted';
      case 'denied':
        return 'Blocked';
      default:
        return 'Not requested';
    }
  };

  return (
    <div className="notification-settings-container">
      {/* Header */}
      <div className="notification-settings-header">
        <div>
          <h2 className="notification-settings-title">Notification Settings</h2>
          <p className="notification-settings-subtitle">
            Configure how you receive task reminders
          </p>
        </div>
        <div className="notification-settings-icon">
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
          </svg>
        </div>
      </div>

      {/* Permission Status */}
      <div className="notification-settings-permission">
        <div className="notification-settings-permission-content">
          <div>
            <p className="notification-settings-permission-label">Browser Permission</p>
            <p className={`notification-settings-permission-status ${
              permission === 'granted' ? 'granted' : permission === 'denied' ? 'denied' : 'default'
            }`}>
              {getPermissionText()}
            </p>
          </div>
          {permission === 'default' && (
            <Button
              variant="gradient"
              onClick={onRequestPermission}
              className="text-sm"
            >
              Request Permission
            </Button>
          )}
          {permission === 'denied' && (
            <div className="notification-settings-permission-error">
              Please enable notifications in your browser settings
            </div>
          )}
        </div>
      </div>

      {/* Enable/Disable Toggle */}
      <div className="notification-settings-toggle-container">
        <div>
          <p className="notification-settings-toggle-label">Enable Notifications</p>
          <p className="notification-settings-toggle-description">
            Receive reminders for upcoming tasks
          </p>
        </div>
        <button
          onClick={onToggle}
          disabled={permission !== 'granted'}
          className={`notification-settings-toggle ${
            isEnabled ? 'enabled' : 'disabled'
          } ${permission !== 'granted' ? 'disabled-permission' : ''}`}
        >
          <span className={`notification-settings-toggle-handle ${isEnabled ? 'enabled' : ''}`} />
        </button>
      </div>

      {/* Notification Timing */}
      {isEnabled && permission === 'granted' && (
        <div className="notification-settings-timing">
          <div>
            <label className="notification-settings-timing-label">
              Notify me before task is due
            </label>
            <div className="notification-settings-timing-controls">
              <input
                type="range"
                min="5"
                max="60"
                step="5"
                value={notifyBefore}
                onChange={(e) => setNotifyBefore(parseInt(e.target.value, 10))}
                className="notification-settings-slider"
              />
              <div className="notification-settings-timing-input-group">
                <input
                  type="number"
                  min="5"
                  max="60"
                  value={notifyBefore}
                  onChange={(e) => setNotifyBefore(parseInt(e.target.value, 10) || 5)}
                  className="notification-settings-number-input"
                />
                <span className="notification-settings-timing-unit">min</span>
              </div>
            </div>
            <p className="notification-settings-timing-hint">
              You&apos;ll be notified {notifyBefore} minutes before a task is due
            </p>
          </div>

          <Button
            variant="gradient"
            onClick={handleSaveSettings}
            isLoading={isSaving}
            className="w-full"
            icon={
              !isSaving && (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              )
            }
          >
            {isSaving ? 'Saving...' : 'Save Settings'}
          </Button>
        </div>
      )}

      {/* Test Notification */}
      {isEnabled && permission === 'granted' && (
        <div className="notification-settings-test">
          <Button
            variant="secondary"
            onClick={handleTestNotification}
            className="w-full"
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            }
          >
            Send Test Notification
          </Button>
        </div>
      )}

      {/* Info Box */}
      <div className="notification-settings-info">
        <div className="notification-settings-info-content">
          <div className="notification-settings-info-icon">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="notification-settings-info-text">
            <p className="notification-settings-info-title">How it works</p>
            <ul className="notification-settings-info-list">
              <li>Notifications check every minute for upcoming tasks</li>
              <li>You&apos;ll only be notified once per task</li>
              <li>Notifications work even when the tab is in the background</li>
              <li>Click a notification to focus the TaskNest window</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
