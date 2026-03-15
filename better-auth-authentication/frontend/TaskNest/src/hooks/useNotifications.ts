/**
 * useNotifications Hook - Browser Notification System
 *
 * Features:
 * - Request notification permission
 * - Check for due/upcoming tasks
 * - Trigger browser notifications
 * - Handle notification clicks
 * - Periodic checking
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { Task } from '@/lib/types';

interface NotificationOptions {
  enabled: boolean;
  checkInterval: number; // in milliseconds
  notifyBefore: number; // minutes before due time
}

interface UseNotificationsReturn {
  permission: NotificationPermission;
  isEnabled: boolean;
  requestPermission: () => Promise<void>;
  checkTasks: (tasks: Task[]) => void;
  toggleNotifications: () => void;
}

const DEFAULT_OPTIONS: NotificationOptions = {
  enabled: false,
  checkInterval: 60000, // Check every minute
  notifyBefore: 15, // Notify 15 minutes before (default)
};

/**
 * Get notification timing preference from localStorage
 */
const getNotifyBefore = (): number => {
  if (typeof window === 'undefined') return DEFAULT_OPTIONS.notifyBefore;
  const saved = localStorage.getItem('notification_minutes_before');
  return saved ? parseInt(saved, 10) : DEFAULT_OPTIONS.notifyBefore;
};

export function useNotifications(tasks: Task[]): UseNotificationsReturn {
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [isEnabled, setIsEnabled] = useState(false);
  const [notifiedTasks, setNotifiedTasks] = useState<Set<number>>(new Set());

  /**
   * Check if browser supports notifications
   */
  const isSupported = typeof window !== 'undefined' && 'Notification' in window;

  /**
   * Initialize permission state
   */
  useEffect(() => {
    if (isSupported) {
      setPermission(Notification.permission);

      // Load enabled state from localStorage
      const saved = localStorage.getItem('notifications_enabled');
      setIsEnabled(saved === 'true' && Notification.permission === 'granted');
    }
  }, [isSupported]);

  /**
   * Request notification permission
   */
  const requestPermission = useCallback(async () => {
    if (!isSupported) {
      console.warn('Notifications not supported');
      return;
    }

    try {
      const result = await Notification.requestPermission();
      setPermission(result);

      if (result === 'granted') {
        setIsEnabled(true);
        localStorage.setItem('notifications_enabled', 'true');

        // Show test notification
        new Notification('TaskNest Notifications Enabled', {
          body: 'You will now receive reminders for your tasks',
          icon: '/favicon.ico',
          badge: '/favicon.ico',
        });
      }
    } catch (error) {
      console.error('Failed to request notification permission:', error);
    }
  }, [isSupported]);

  /**
   * Toggle notifications on/off
   */
  const toggleNotifications = useCallback(() => {
    if (permission !== 'granted') {
      requestPermission();
      return;
    }

    const newState = !isEnabled;
    setIsEnabled(newState);
    localStorage.setItem('notifications_enabled', String(newState));
  }, [permission, isEnabled, requestPermission]);

  /**
   * Check if task is due soon
   */
  const isTaskDueSoon = useCallback((task: Task): boolean => {
    if (!task.due_date || task.completed) return false;

    const now = new Date();
    const dueDateTime = new Date(task.due_date);

    // If task has time, use it
    if (task.due_time) {
      const [hours, minutes] = task.due_time.split(':').map(Number);
      dueDateTime.setHours(hours, minutes, 0, 0);
    } else {
      // If no time, set to end of day
      dueDateTime.setHours(23, 59, 59, 999);
    }

    const diffMs = dueDateTime.getTime() - now.getTime();
    const diffMinutes = Math.floor(diffMs / 60000);

    // Get dynamic notification timing preference
    const notifyBefore = getNotifyBefore();

    // Notify if due within the configured time window
    return diffMinutes > 0 && diffMinutes <= notifyBefore;
  }, []);

  /**
   * Send notification for a task
   */
  const sendNotification = useCallback((task: Task) => {
    if (!isSupported || permission !== 'granted' || !isEnabled) return;
    if (notifiedTasks.has(task.id)) return;

    const dueTime = task.due_time || 'soon';
    const title = `⏰ Task Due ${dueTime === 'soon' ? 'Soon' : `at ${dueTime}`}`;
    const body = task.title;

    const notification = new Notification(title, {
      body,
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      tag: `task-${task.id}`,
      requireInteraction: true,
      data: { taskId: task.id },
    });

    // Handle notification click
    notification.onclick = () => {
      window.focus();
      notification.close();
      // Could navigate to specific task here
    };

    // Mark as notified
    setNotifiedTasks((prev) => new Set(prev).add(task.id));

    // Clear from notified list after 1 hour
    setTimeout(() => {
      setNotifiedTasks((prev) => {
        const next = new Set(prev);
        next.delete(task.id);
        return next;
      });
    }, 3600000);
  }, [isSupported, permission, isEnabled, notifiedTasks]);

  /**
   * Check tasks for notifications
   */
  const checkTasks = useCallback(
    (tasksToCheck: Task[]) => {
      if (!isEnabled || permission !== 'granted') return;

      tasksToCheck.forEach((task) => {
        if (isTaskDueSoon(task)) {
          sendNotification(task);
        }
      });
    },
    [isEnabled, permission, isTaskDueSoon, sendNotification]
  );

  /**
   * Periodic task checking
   */
  useEffect(() => {
    if (!isEnabled || permission !== 'granted') return;

    const interval = setInterval(() => {
      checkTasks(tasks);
    }, DEFAULT_OPTIONS.checkInterval);

    // Initial check
    checkTasks(tasks);

    return () => clearInterval(interval);
  }, [isEnabled, permission, tasks, checkTasks]);

  return {
    permission,
    isEnabled,
    requestPermission,
    checkTasks,
    toggleNotifications,
  };
}
