/**
 * NotificationPermissionBanner Component
 *
 * Displays a banner prompting users to enable browser notifications.
 * Shows only when permission is 'default' (not yet requested).
 * Can be dismissed and won't show again for 7 days.
 */

'use client';

import { useState, useEffect } from 'react';
import { X, Bell } from 'lucide-react';

interface NotificationPermissionBannerProps {
  onRequestPermission: () => Promise<void>;
  permission: NotificationPermission;
}

const DISMISS_KEY = 'notification_banner_dismissed';
const DISMISS_DURATION = 7 * 24 * 60 * 60 * 1000; // 7 days in milliseconds

export function NotificationPermissionBanner({
  onRequestPermission,
  permission,
}: NotificationPermissionBannerProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isRequesting, setIsRequesting] = useState(false);

  useEffect(() => {
    // Only show if permission is 'default' (not yet asked)
    if (permission !== 'default') {
      setIsVisible(false);
      return;
    }

    // Check if user dismissed the banner recently
    const dismissedAt = localStorage.getItem(DISMISS_KEY);
    if (dismissedAt) {
      const dismissedTime = parseInt(dismissedAt, 10);
      const now = Date.now();

      // If dismissed less than 7 days ago, don't show
      if (now - dismissedTime < DISMISS_DURATION) {
        setIsVisible(false);
        return;
      }
    }

    // Show banner
    setIsVisible(true);
  }, [permission]);

  const handleEnable = async () => {
    setIsRequesting(true);
    try {
      await onRequestPermission();
      setIsVisible(false);
    } catch (error) {
      console.error('Failed to request permission:', error);
    } finally {
      setIsRequesting(false);
    }
  };

  const handleDismiss = () => {
    // Store dismissal timestamp
    localStorage.setItem(DISMISS_KEY, String(Date.now()));
    setIsVisible(false);
  };

  if (!isVisible) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-primary to-primary-dark text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex items-center justify-between gap-4">
          {/* Icon and Message */}
          <div className="flex items-center gap-3 flex-1">
            <div className="flex-shrink-0">
              <Bell className="w-6 h-6" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium">
                Stay on top of your tasks with notifications
              </p>
              <p className="text-xs text-white/80 mt-0.5">
                Get reminders before your tasks are due
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <button
              onClick={handleEnable}
              disabled={isRequesting}
              className="px-4 py-2 bg-white text-primary rounded-lg font-medium text-sm hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isRequesting ? 'Enabling...' : 'Enable Notifications'}
            </button>
            <button
              onClick={handleDismiss}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              aria-label="Dismiss notification banner"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
