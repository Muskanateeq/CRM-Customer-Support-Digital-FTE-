/**
 * Settings Page - TaskNest
 * Comprehensive user preferences and account settings with backend integration
 * Dark Golden Theme - Modern SaaS Design
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { clearAllActivities } from '@/lib/activities-api';
import { getTrash, restoreTask, permanentDeleteTask, emptyTrash } from '@/lib/trash-api';
import { Task } from '@/lib/types';
import ChangePasswordModal from '@/components/settings/ChangePasswordModal';
import {
  getSettings,
  updateSettings,
  updateProfile,
  exportUserData,
  deleteAccount,
  type UserSettings,
  type SettingsUpdate,
} from '@/lib/settingsApi';
import './settings.css';

type SettingsTab = 'profile' | 'notifications' | 'appearance' | 'tasks' | 'data' | 'trash' | 'about';

export default function SettingsPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading, getToken, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile');
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [userName, setUserName] = useState('');
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [trashedTasks, setTrashedTasks] = useState<Task[]>([]);
  const [isLoadingTrash, setIsLoadingTrash] = useState(false);

  /**
   * Redirect if not authenticated
   */
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  /**
   * Load settings from backend
   */
  useEffect(() => {
    const loadSettings = async () => {
      if (!isAuthenticated) return;

      try {
        const token = await getToken();
        if (!token) return;

        const userSettings = await getSettings(token);
        setSettings(userSettings);
        setUserName(user?.name || '');
      } catch (error) {
        console.error('Failed to load settings:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadSettings();
  }, [isAuthenticated, getToken, user]);

  /**
   * Handle setting change with backend sync
   */
  const handleSettingChange = async (updates: SettingsUpdate) => {
    if (!settings) return;

    try {
      setIsSaving(true);
      const token = await getToken();
      if (!token) return;

      const updatedSettings = await updateSettings(token, updates);
      setSettings(updatedSettings);
    } catch (error) {
      console.error('Failed to update settings:', error);
      alert('Failed to save settings. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Handle profile name update
   */
  const handleNameUpdate = async () => {
    if (!userName.trim()) {
      alert('Name cannot be empty');
      return;
    }

    try {
      setIsSaving(true);
      const token = await getToken();
      if (!token) return;

      await updateProfile(token, { name: userName });
      alert('Profile updated successfully');
    } catch (error) {
      console.error('Failed to update profile:', error);
      alert('Failed to update profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Handle export data
   */
  const handleExportData = async () => {
    try {
      setIsSaving(true);
      const token = await getToken();
      if (!token) return;

      const data = await exportUserData(token);

      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `tasknest-data-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);

      alert('Data exported successfully');
    } catch (error) {
      console.error('Failed to export data:', error);
      alert('Failed to export data. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Load trash when trash tab is active
   */
  useEffect(() => {
    const loadTrash = async () => {
      if (activeTab !== 'trash' || !isAuthenticated) return;

      try {
        setIsLoadingTrash(true);
        const tasks = await getTrash({ limit: 100 });
        setTrashedTasks(tasks);
      } catch (error) {
        console.error('Failed to load trash:', error);
      } finally {
        setIsLoadingTrash(false);
      }
    };

    loadTrash();
  }, [activeTab, isAuthenticated]);

  /**
   * Handle clear history
   */
  const handleClearHistory = async () => {
    if (!confirm('Are you sure you want to clear all activity history? This cannot be undone.')) return;

    try {
      setIsSaving(true);
      await clearAllActivities();
      alert('Activity history cleared successfully');
    } catch (error) {
      console.error('Failed to clear history:', error);
      alert('Failed to clear history. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Handle restore task
   */
  const handleRestoreTask = async (taskId: number) => {
    try {
      setIsSaving(true);
      await restoreTask(taskId);
      setTrashedTasks(prev => prev.filter(t => t.id !== taskId));
      alert('Task restored successfully');
    } catch (error) {
      console.error('Failed to restore task:', error);
      alert('Failed to restore task. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Handle permanent delete
   */
  const handlePermanentDelete = async (taskId: number) => {
    if (!confirm('Permanently delete this task? This cannot be undone.')) return;

    try {
      setIsSaving(true);
      await permanentDeleteTask(taskId);
      setTrashedTasks(prev => prev.filter(t => t.id !== taskId));
      alert('Task permanently deleted');
    } catch (error) {
      console.error('Failed to delete task:', error);
      alert('Failed to delete task. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Handle empty trash
   */
  const handleEmptyTrash = async () => {
    if (!confirm('Permanently delete all tasks in trash? This cannot be undone.')) return;

    try {
      setIsSaving(true);
      const result = await emptyTrash();
      setTrashedTasks([]);
      alert(result.message);
    } catch (error) {
      console.error('Failed to empty trash:', error);
      alert('Failed to empty trash. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Handle account deletion
   */
  const handleDeleteAccount = async () => {
    const confirmation = prompt(
      'This action is permanent and cannot be undone. All your data will be deleted.\n\nType your email to confirm:'
    );

    if (confirmation !== user?.email) {
      alert('Email does not match. Account deletion cancelled.');
      return;
    }

    try {
      setIsSaving(true);
      const token = await getToken();
      if (!token) return;

      await deleteAccount(token);
      alert('Account deleted successfully');
      logout();
      router.push('/');
    } catch (error) {
      console.error('Failed to delete account:', error);
      alert('Failed to delete account. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  if (authLoading || !isAuthenticated || isLoading) {
    return (
      <div className="settings-page">
        <div className="settings-loading">Loading settings...</div>
      </div>
    );
  }

  if (!settings) {
    return (
      <div className="settings-page">
        <div className="settings-error">Failed to load settings</div>
      </div>
    );
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: '👤' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
    { id: 'appearance', label: 'Appearance', icon: '🎨' },
    { id: 'tasks', label: 'Task Preferences', icon: '✅' },
    { id: 'trash', label: 'Trash', icon: '🗑️' },
    { id: 'data', label: 'Data & Privacy', icon: '🔒' },
    { id: 'about', label: 'About', icon: 'ℹ️' },
  ];

  return (
    <div className="settings-page">
      {/* Header */}
      <div className="settings-header">
        <h1 className="settings-title">Settings</h1>
        <p className="settings-subtitle">Manage your account preferences and application settings</p>
      </div>

      <div className="settings-container">
        {/* Sidebar Tabs */}
        <div className="settings-sidebar">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as SettingsTab)}
              className={`settings-tab ${activeTab === tab.id ? 'active' : ''}`}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="settings-content">
          {/* Profile Settings */}
          {activeTab === 'profile' && (
            <div className="settings-section">
              <h2 className="section-title">Profile Settings</h2>
              <p className="section-description">Manage your personal information</p>

              <div className="settings-group">
                <label className="setting-label">Name</label>
                <div className="input-with-button">
                  <input
                    type="text"
                    value={userName}
                    onChange={(e) => setUserName(e.target.value)}
                    className="setting-input"
                    placeholder="Enter your name"
                  />
                  <button
                    onClick={handleNameUpdate}
                    disabled={isSaving || userName === user?.name}
                    className="btn-secondary"
                  >
                    {isSaving ? 'Saving...' : 'Update'}
                  </button>
                </div>
                <p className="setting-hint">Your display name across TaskNest</p>
              </div>

              <div className="settings-group">
                <label className="setting-label">Email</label>
                <input
                  type="email"
                  value={user?.email || ''}
                  disabled
                  className="setting-input disabled"
                />
                <p className="setting-hint">Email cannot be changed</p>
              </div>

              <div className="settings-group">
                <label className="setting-label">Password</label>
                <button
                  onClick={() => setIsPasswordModalOpen(true)}
                  className="btn-secondary"
                >
                  Change Password
                </button>
                <p className="setting-hint">Update your password to keep your account secure</p>
              </div>
            </div>
          )}

          {/* Notification Settings */}
          {activeTab === 'notifications' && (
            <div className="settings-section">
              <h2 className="section-title">Notification Settings</h2>
              <p className="section-description">Control how you receive notifications</p>

              <div className="settings-group">
                <div className="setting-toggle">
                  <div>
                    <label className="setting-label">Email Notifications</label>
                    <p className="setting-hint">Receive notifications via email</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={settings.email_notifications}
                      onChange={(e) => handleSettingChange({ email_notifications: e.target.checked })}
                      disabled={isSaving}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
              </div>

              <div className="settings-group">
                <div className="setting-toggle">
                  <div>
                    <label className="setting-label">Browser Notifications</label>
                    <p className="setting-hint">Receive push notifications in your browser</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={settings.browser_notifications}
                      onChange={(e) => handleSettingChange({ browser_notifications: e.target.checked })}
                      disabled={isSaving}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
              </div>

              <div className="settings-group">
                <div className="setting-toggle">
                  <div>
                    <label className="setting-label">Task Due Reminders</label>
                    <p className="setting-hint">Get reminded when tasks are due</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={settings.task_reminders}
                      onChange={(e) => handleSettingChange({ task_reminders: e.target.checked })}
                      disabled={isSaving}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
              </div>

              <div className="settings-group">
                <label className="setting-label">Do Not Disturb Hours</label>
                <div className="dnd-hours">
                  <div>
                    <label>Start</label>
                    <input
                      type="time"
                      value={settings.dnd_start || '22:00'}
                      onChange={(e) => handleSettingChange({ dnd_start: e.target.value })}
                      className="setting-input small"
                      disabled={isSaving}
                    />
                  </div>
                  <span>to</span>
                  <div>
                    <label>End</label>
                    <input
                      type="time"
                      value={settings.dnd_end || '08:00'}
                      onChange={(e) => handleSettingChange({ dnd_end: e.target.value })}
                      className="setting-input small"
                      disabled={isSaving}
                    />
                  </div>
                </div>
                <p className="setting-hint">No notifications during these hours</p>
              </div>
            </div>
          )}

          {/* Appearance Settings */}
          {activeTab === 'appearance' && (
            <div className="settings-section">
              <h2 className="section-title">Appearance Settings</h2>
              <p className="section-description">Customize how TaskNest looks</p>

              <div className="settings-group">
                <label className="setting-label">Theme</label>
                <div className="setting-options">
                  <button
                    className={`option-btn ${settings.theme === 'dark' ? 'active' : ''}`}
                    onClick={() => handleSettingChange({ theme: 'dark' })}
                    disabled={isSaving}
                  >
                    🌙 Dark
                  </button>
                  <button
                    className={`option-btn ${settings.theme === 'light' ? 'active' : ''}`}
                    onClick={() => handleSettingChange({ theme: 'light' })}
                    disabled={isSaving}
                  >
                    ☀️ Light
                  </button>
                </div>
              </div>

              <div className="settings-group">
                <label className="setting-label">Font Size</label>
                <div className="setting-options">
                  {['small', 'medium', 'large'].map((size) => (
                    <button
                      key={size}
                      className={`option-btn ${settings.font_size === size ? 'active' : ''}`}
                      onClick={() => handleSettingChange({ font_size: size })}
                      disabled={isSaving}
                    >
                      {size.charAt(0).toUpperCase() + size.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              <div className="settings-group">
                <label className="setting-label">View Mode</label>
                <div className="setting-options">
                  {['compact', 'comfortable', 'spacious'].map((mode) => (
                    <button
                      key={mode}
                      className={`option-btn ${settings.view_mode === mode ? 'active' : ''}`}
                      onClick={() => handleSettingChange({ view_mode: mode })}
                      disabled={isSaving}
                    >
                      {mode.charAt(0).toUpperCase() + mode.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Task Preferences */}
          {activeTab === 'tasks' && (
            <div className="settings-section">
              <h2 className="section-title">Task Preferences</h2>
              <p className="section-description">Set default options for task management</p>

              <div className="settings-group">
                <label className="setting-label">Default Priority</label>
                <select
                  value={settings.default_priority}
                  onChange={(e) => handleSettingChange({ default_priority: e.target.value })}
                  className="setting-select"
                  disabled={isSaving}
                >
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>

              <div className="settings-group">
                <label className="setting-label">Default Sort By</label>
                <select
                  value={settings.default_sort}
                  onChange={(e) => handleSettingChange({ default_sort: e.target.value })}
                  className="setting-select"
                  disabled={isSaving}
                >
                  <option value="created_date">Created Date</option>
                  <option value="due_date">Due Date</option>
                  <option value="priority">Priority</option>
                  <option value="title">Title</option>
                </select>
              </div>

              <div className="settings-group">
                <div className="setting-toggle">
                  <div>
                    <label className="setting-label">Show Completed Tasks</label>
                    <p className="setting-hint">Display completed tasks by default</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={settings.show_completed}
                      onChange={(e) => handleSettingChange({ show_completed: e.target.checked })}
                      disabled={isSaving}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Trash Management */}
          {activeTab === 'trash' && (
            <div className="settings-section">
              <h2 className="section-title">Trash</h2>
              <p className="section-description">Manage deleted tasks and restore them if needed</p>

              {isLoadingTrash ? (
                <div style={{ padding: '40px', textAlign: 'center', color: '#9ca3af' }}>
                  Loading trash...
                </div>
              ) : trashedTasks.length === 0 ? (
                <div style={{ padding: '40px', textAlign: 'center', color: '#9ca3af' }}>
                  <div style={{ fontSize: '48px', marginBottom: '16px' }}>🗑️</div>
                  <p>Trash is empty</p>
                </div>
              ) : (
                <>
                  <div className="settings-group">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                      <label className="setting-label">{trashedTasks.length} deleted task{trashedTasks.length !== 1 ? 's' : ''}</label>
                      <button
                        onClick={handleEmptyTrash}
                        disabled={isSaving}
                        className="btn-danger"
                        style={{ padding: '6px 12px', fontSize: '13px' }}
                      >
                        {isSaving ? 'Emptying...' : 'Empty Trash'}
                      </button>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      {trashedTasks.map((task) => (
                        <div
                          key={task.id}
                          style={{
                            background: 'rgba(255, 255, 255, 0.03)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '8px',
                            padding: '16px',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                          }}
                        >
                          <div style={{ flex: 1 }}>
                            <h4 style={{ margin: 0, fontSize: '15px', fontWeight: 500, color: '#f3f4f6' }}>
                              {task.title}
                            </h4>
                            {task.description && (
                              <p style={{ margin: '4px 0 0', fontSize: '13px', color: '#9ca3af' }}>
                                {task.description}
                              </p>
                            )}
                            <div style={{ marginTop: '8px', display: 'flex', gap: '12px', fontSize: '12px', color: '#6b7280' }}>
                              <span>Priority: {task.priority}</span>
                              {task.due_date && <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>}
                            </div>
                          </div>
                          <div style={{ display: 'flex', gap: '8px' }}>
                            <button
                              onClick={() => handleRestoreTask(task.id)}
                              disabled={isSaving}
                              className="btn-secondary"
                              style={{ padding: '6px 12px', fontSize: '13px' }}
                            >
                              ♻️ Restore
                            </button>
                            <button
                              onClick={() => handlePermanentDelete(task.id)}
                              disabled={isSaving}
                              className="btn-danger"
                              style={{ padding: '6px 12px', fontSize: '13px' }}
                            >
                              🗑️ Delete
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          )}

          {/* Data & Privacy */}
          {activeTab === 'data' && (
            <div className="settings-section">
              <h2 className="section-title">Data & Privacy</h2>
              <p className="section-description">Manage your data and account</p>

              <div className="settings-group">
                <label className="setting-label">Export Data</label>
                <button
                  onClick={handleExportData}
                  disabled={isSaving}
                  className="btn-secondary"
                >
                  {isSaving ? 'Exporting...' : 'Download All Data'}
                </button>
                <p className="setting-hint">Download all your tasks, tags, and settings as JSON</p>
              </div>

              <div className="settings-group">
                <label className="setting-label">Clear History</label>
                <button
                  onClick={handleClearHistory}
                  className="btn-secondary"
                >
                  Clear Activity History
                </button>
                <p className="setting-hint">Remove all local activity tracking data</p>
              </div>

              <div className="settings-group danger-zone">
                <label className="setting-label">Delete Account</label>
                <button
                  onClick={handleDeleteAccount}
                  disabled={isSaving}
                  className="btn-danger"
                >
                  {isSaving ? 'Deleting...' : 'Delete Account'}
                </button>
                <p className="setting-hint danger">
                  Permanently delete your account and all data. This action cannot be undone.
                </p>
              </div>
            </div>
          )}

          {/* About */}
          {activeTab === 'about' && (
            <div className="settings-section">
              <h2 className="section-title">About TaskNest</h2>
              <p className="section-description">Application information and resources</p>

              <div className="about-content">
                <div className="about-item">
                  <strong>Version</strong>
                  <span>1.0.0</span>
                </div>
                <div className="about-item">
                  <strong>Build</strong>
                  <span>Phase 2 - Full Stack</span>
                </div>
                <div className="about-item">
                  <strong>Last Updated</strong>
                  <span>{new Date().toLocaleDateString()}</span>
                </div>

                <div className="about-links">
                  <a href="#" className="about-link">Documentation</a>
                  <a href="#" className="about-link">Privacy Policy</a>
                  <a href="#" className="about-link">Terms of Service</a>
                  <a href="#" className="about-link">Support</a>
                </div>

                <div className="about-footer">
                  <p>© 2024 TaskNest. All rights reserved.</p>
                  <p>Built with Next.js, FastAPI, and PostgreSQL</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Change Password Modal */}
      <ChangePasswordModal
        isOpen={isPasswordModalOpen}
        onClose={() => setIsPasswordModalOpen(false)}
      />
    </div>
  );
}
