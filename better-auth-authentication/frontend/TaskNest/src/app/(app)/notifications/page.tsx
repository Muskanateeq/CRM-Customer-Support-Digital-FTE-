/**
 * Notifications Page - TaskNest
 * Notification center with history and filtering
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import {
  getNotifications,
  markAsRead,
  markAllAsRead,
  deleteNotification,
  type Notification,
} from '@/lib/notificationsApi';
import './notifications.css';

type FilterType = 'all' | 'task_update' | 'mention' | 'assignment' | 'reminder';
type FilterStatus = 'all' | 'unread' | 'read';

export default function NotificationsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading, getToken } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filterType, setFilterType] = useState<FilterType>('all');
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');

  /**
   * Redirect if not authenticated
   */
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  /**
   * Load notifications
   */
  const loadNotifications = async () => {
    if (!isAuthenticated) return;

    try {
      setIsLoading(true);
      const data = await getNotifications(false, 100);
      setNotifications(data);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, getToken]);

  /**
   * Handle mark as read
   */
  const handleMarkAsRead = async (notificationId: number) => {
    try {
      await markAsRead(notificationId);

      // Update local state
      setNotifications(prev =>
        prev.map(n => (n.id === notificationId ? { ...n, read: true } : n))
      );
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  /**
   * Handle mark all as read
   */
  const handleMarkAllAsRead = async () => {
    try {
      await markAllAsRead();

      // Update local state
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  /**
   * Handle delete notification
   */
  const handleDelete = async (notificationId: number) => {
    if (!confirm('Delete this notification?')) return;

    try {
      await deleteNotification(notificationId);

      // Update local state
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  /**
   * Filter notifications
   */
  const filteredNotifications = notifications.filter(notification => {
    // Filter by type
    if (filterType !== 'all' && notification.type !== filterType) {
      return false;
    }

    // Filter by status
    if (filterStatus === 'unread' && notification.read) {
      return false;
    }
    if (filterStatus === 'read' && !notification.read) {
      return false;
    }

    return true;
  });

  /**
   * Get notification icon
   */
  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'task_update':
        return '📝';
      case 'mention':
        return '@';
      case 'assignment':
        return '👤';
      case 'reminder':
        return '⏰';
      default:
        return '🔔';
    }
  };

  /**
   * Format time ago
   */
  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;

    return date.toLocaleDateString();
  };

  if (authLoading || !isAuthenticated) {
    return null;
  }

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="notifications-page">
      {/* Header */}
      <div className="notifications-header">
        <div>
          <h1 className="notifications-title">Notifications</h1>
          <p className="notifications-subtitle">
            {unreadCount > 0 ? `${unreadCount} unread notification${unreadCount > 1 ? 's' : ''}` : 'All caught up!'}
          </p>
        </div>

        {unreadCount > 0 && (
          <button onClick={handleMarkAllAsRead} className="btn-mark-all">
            Mark All as Read
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="notifications-filters">
        <div className="filter-group">
          <label>Type:</label>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as FilterType)}
            className="filter-select"
          >
            <option value="all">All Types</option>
            <option value="task_update">Task Updates</option>
            <option value="mention">Mentions</option>
            <option value="assignment">Assignments</option>
            <option value="reminder">Reminders</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Status:</label>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as FilterStatus)}
            className="filter-select"
          >
            <option value="all">All</option>
            <option value="unread">Unread</option>
            <option value="read">Read</option>
          </select>
        </div>
      </div>

      {/* Notifications List */}
      {isLoading ? (
        <div className="notifications-loading">Loading notifications...</div>
      ) : filteredNotifications.length === 0 ? (
        <div className="notifications-empty">
          <div className="empty-icon">🔔</div>
          <h3>No notifications</h3>
          <p>You&apos;re all caught up!</p>
        </div>
      ) : (
        <div className="notifications-list">
          {filteredNotifications.map((notification) => (
            <div
              key={notification.id}
              className={`notification-item ${notification.read ? 'read' : 'unread'}`}
            >
              <div className="notification-icon">
                {getNotificationIcon(notification.type)}
              </div>

              <div className="notification-content">
                <p className="notification-text">{notification.content}</p>
                <span className="notification-time">
                  {formatTimeAgo(notification.created_at)}
                </span>
              </div>

              <div className="notification-actions">
                {!notification.read && (
                  <button
                    onClick={() => handleMarkAsRead(notification.id)}
                    className="action-btn"
                    title="Mark as read"
                  >
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="18" height="18">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </button>
                )}
                <button
                  onClick={() => handleDelete(notification.id)}
                  className="action-btn delete"
                  title="Delete"
                >
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="18" height="18">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
