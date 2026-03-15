/**
 * useInAppNotifications Hook
 *
 * Custom hook for in-app notification management (comments, mentions, assignments)
 */

import { useState, useCallback, useEffect } from 'react';
import {
  getNotifications,
  getUnreadCount,
  markAsRead as markAsReadApi,
  markAllAsRead as markAllAsReadApi,
  deleteNotification as deleteNotificationApi,
} from '@/lib/notifications-api';
import { Notification } from '@/lib/types';

export function useInAppNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch notifications
   */
  const fetchNotifications = useCallback(async (unreadOnly: boolean = false) => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await getNotifications(unreadOnly);
      setNotifications(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch notifications';
      setError(errorMessage);
      console.error('Failed to fetch notifications:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Fetch unread count
   */
  const fetchUnreadCount = useCallback(async () => {
    try {
      const data = await getUnreadCount();
      setUnreadCount(data.count);
    } catch (err) {
      console.error('Failed to fetch unread count:', err);
    }
  }, []);

  /**
   * Mark notification as read
   */
  const markAsRead = useCallback(
    async (notificationId: number) => {
      setError(null);

      try {
        const updatedNotification = await markAsReadApi(notificationId);
        setNotifications((prev) =>
          prev.map((notification) =>
            notification.id === notificationId ? updatedNotification : notification
          )
        );
        setUnreadCount((prev) => Math.max(0, prev - 1));
        return updatedNotification;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to mark as read';
        setError(errorMessage);
        throw err;
      }
    },
    []
  );

  /**
   * Mark all notifications as read
   */
  const markAllAsRead = useCallback(async () => {
    setError(null);

    try {
      const result = await markAllAsReadApi();
      setNotifications((prev) =>
        prev.map((notification) => ({ ...notification, read: true }))
      );
      setUnreadCount(0);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to mark all as read';
      setError(errorMessage);
      throw err;
    }
  }, []);

  /**
   * Delete notification
   */
  const deleteNotification = useCallback(
    async (notificationId: number) => {
      setError(null);

      try {
        await deleteNotificationApi(notificationId);
        setNotifications((prev) => {
          const notification = prev.find((n) => n.id === notificationId);
          if (notification && !notification.read) {
            setUnreadCount((count) => Math.max(0, count - 1));
          }
          return prev.filter((n) => n.id !== notificationId);
        });
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to delete notification';
        setError(errorMessage);
        throw err;
      }
    },
    []
  );

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Fetch unread count on mount and set up polling
   */
  useEffect(() => {
    fetchUnreadCount();

    // Poll for unread count every 30 seconds
    const interval = setInterval(fetchUnreadCount, 30000);

    return () => clearInterval(interval);
  }, [fetchUnreadCount]);

  return {
    notifications,
    unreadCount,
    isLoading,
    error,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearError,
  };
}
