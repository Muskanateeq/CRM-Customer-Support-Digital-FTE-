/**
 * History Page - TaskNest
 * Track all user activities and changes
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useRefresh } from '@/contexts/RefreshContext';
import { getActivities, deleteActivity, clearAllActivities, type Activity, type ActivityType } from '@/lib/activities-api';
import './history.css';

/**
 * Date Filter Type
 */
type DateFilter = 'today' | 'week' | 'month' | 'all';

export default function HistoryPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { registerRefresh, unregisterRefresh } = useRefresh();
  const [activities, setActivities] = useState<Activity[]>([]);
  const [filteredActivities, setFilteredActivities] = useState<Activity[]>([]);
  const [dateFilter, setDateFilter] = useState<DateFilter>('all');
  const [typeFilter, setTypeFilter] = useState<ActivityType | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState(false);

  /**
   * Redirect if not authenticated
   */
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  /**
   * Load activities from API
   */
  const loadActivities = useCallback(async () => {
    if (!isAuthenticated) return;

    try {
      setIsLoading(true);
      const data = await getActivities({ limit: 500 });
      setActivities(data);
    } catch (error) {
      console.error('Failed to load activities:', error);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    loadActivities();
  }, [loadActivities]);

  /**
   * Register refresh callback for auto-refresh
   */
  useEffect(() => {
    registerRefresh('history', loadActivities);
    return () => unregisterRefresh('history');
  }, [registerRefresh, unregisterRefresh, loadActivities]);

  /**
   * Apply filters
   */
  useEffect(() => {
    let filtered = [...activities];

    // Date filter
    const now = new Date();
    if (dateFilter === 'today') {
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      filtered = filtered.filter(a => new Date(a.created_at) >= today);
    } else if (dateFilter === 'week') {
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      filtered = filtered.filter(a => new Date(a.created_at) >= weekAgo);
    } else if (dateFilter === 'month') {
      const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      filtered = filtered.filter(a => new Date(a.created_at) >= monthAgo);
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(a => a.type === typeFilter);
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(a =>
        a.title.toLowerCase().includes(query) ||
        a.description.toLowerCase().includes(query) ||
        a.meta?.task_name?.toLowerCase().includes(query)
      );
    }

    // Sort by created_at (newest first)
    filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

    setFilteredActivities(filtered);
  }, [activities, dateFilter, typeFilter, searchQuery]);

  /**
   * Handle delete activity
   */
  const handleDeleteActivity = async (id: number) => {
    if (!confirm('Delete this activity?')) return;

    try {
      setIsDeleting(true);
      await deleteActivity(id);
      setActivities(prev => prev.filter(a => a.id !== id));
    } catch (error) {
      console.error('Failed to delete activity:', error);
      alert('Failed to delete activity. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  };

  /**
   * Handle clear all activities
   */
  const handleClearAll = async () => {
    if (!confirm('Are you sure you want to clear all activity history? This cannot be undone.')) return;

    try {
      setIsDeleting(true);
      await clearAllActivities();
      setActivities([]);
    } catch (error) {
      console.error('Failed to clear activities:', error);
      alert('Failed to clear activities. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  };

  /**
   * Get activity icon
   */
  const getActivityIcon = (type: ActivityType) => {
    switch (type) {
      case 'created':
        return '✅';
      case 'updated':
        return '✏️';
      case 'deleted':
        return '❌';
      case 'completed':
        return '✔️';
      case 'uncompleted':
        return '🔄';
      case 'restored':
        return '♻️';
      default:
        return '📝';
    }
  };

  /**
   * Get activity color
   */
  const getActivityColor = (type: ActivityType) => {
    switch (type) {
      case 'created':
        return 'green';
      case 'updated':
        return 'blue';
      case 'deleted':
        return 'red';
      case 'completed':
        return 'green';
      case 'uncompleted':
        return 'yellow';
      case 'restored':
        return 'purple';
      default:
        return 'gray';
    }
  };

  /**
   * Format timestamp
   */
  const formatTimestamp = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  };

  /**
   * Group activities by date
   */
  const groupedActivities = filteredActivities.reduce((groups, activity) => {
    const date = new Date(activity.created_at).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(activity);
    return groups;
  }, {} as Record<string, Activity[]>);

  if (authLoading || !isAuthenticated) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="history-page">
        <div className="history-loading">Loading activities...</div>
      </div>
    );
  }

  return (
    <div className="history-page">
      {/* Header */}
      <div className="history-header">
        <div>
          <h1 className="history-title">Activity History</h1>
          <p className="history-subtitle">Track all your task activities and changes</p>
        </div>
        {activities.length > 0 && (
          <button
            onClick={handleClearAll}
            disabled={isDeleting}
            className="btn-danger"
            style={{ padding: '8px 16px', fontSize: '14px' }}
          >
            {isDeleting ? 'Clearing...' : 'Clear All'}
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="history-filters">
        {/* Search */}
        <div className="history-search">
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search activities..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="history-search-input"
          />
        </div>

        {/* Date Filter */}
        <div className="history-filter-group">
          <label>Time Period</label>
          <div className="history-filter-buttons">
            {(['today', 'week', 'month', 'all'] as DateFilter[]).map((filter) => (
              <button
                key={filter}
                onClick={() => setDateFilter(filter)}
                className={`filter-btn ${dateFilter === filter ? 'active' : ''}`}
              >
                {filter === 'today' && 'Today'}
                {filter === 'week' && 'This Week'}
                {filter === 'month' && 'This Month'}
                {filter === 'all' && 'All Time'}
              </button>
            ))}
          </div>
        </div>

        {/* Type Filter */}
        <div className="history-filter-group">
          <label>Activity Type</label>
          <div className="history-filter-buttons">
            <button
              onClick={() => setTypeFilter('all')}
              className={`filter-btn ${typeFilter === 'all' ? 'active' : ''}`}
            >
              All
            </button>
            {(['created', 'updated', 'deleted', 'completed', 'restored'] as ActivityType[]).map((type) => (
              <button
                key={type}
                onClick={() => setTypeFilter(type)}
                className={`filter-btn ${typeFilter === type ? 'active' : ''}`}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Activities Timeline */}
      <div className="history-timeline">
        {Object.keys(groupedActivities).length === 0 ? (
          <div className="history-empty">
            <svg width="80" height="80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3>No activities found</h3>
            <p>Start creating and managing tasks to see your activity history</p>
          </div>
        ) : (
          Object.entries(groupedActivities).map(([date, dateActivities]) => (
            <div key={date} className="history-date-group">
              <div className="history-date-header">{date}</div>
              <div className="history-activities">
                {dateActivities.map((activity) => (
                  <div key={activity.id} className={`history-activity ${getActivityColor(activity.type)}`}>
                    <div className="activity-icon">
                      {getActivityIcon(activity.type)}
                    </div>
                    <div className="activity-content">
                      <div className="activity-header">
                        <h4 className="activity-title">{activity.title}</h4>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <span className="activity-time">{formatTimestamp(activity.created_at)}</span>
                          <button
                            onClick={() => handleDeleteActivity(activity.id)}
                            disabled={isDeleting}
                            className="activity-delete-btn"
                            title="Delete activity"
                            style={{
                              background: 'transparent',
                              border: 'none',
                              color: '#ef4444',
                              cursor: 'pointer',
                              fontSize: '18px',
                              padding: '4px',
                              opacity: 0.7,
                              transition: 'opacity 0.2s'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.opacity = '1'}
                            onMouseLeave={(e) => e.currentTarget.style.opacity = '0.7'}
                          >
                            🗑️
                          </button>
                        </div>
                      </div>
                      <p className="activity-description">{activity.description}</p>
                      {activity.meta?.changes && activity.meta.changes.length > 0 && (
                        <ul className="activity-changes">
                          {activity.meta.changes.map((change, idx) => (
                            <li key={idx}>{change}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
