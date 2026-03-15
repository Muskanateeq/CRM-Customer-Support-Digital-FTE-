/**
 * Dashboard Page - TaskNest
 * Modern dashboard with sidebar navigation
 */

'use client';

import React, { useState, useEffect, useRef, Suspense } from 'react';
import { useTasks } from '@/hooks/useTasks';
import { useAuth } from '@/contexts/AuthContext';
import { useRefresh } from '@/contexts/RefreshContext';
import { useNotifications } from '@/hooks/useNotifications';
import { useTemplates } from '@/hooks/useTemplates';
import { useStats } from '@/hooks/useStats';
import { useTags } from '@/hooks/useTags';
import { Task, TaskCreateRequest, TaskUpdateRequest } from '@/lib/types';
import TaskForm from '@/components/tasks/TaskForm';
import TaskDetailModal from '@/components/tasks/TaskDetailModal';
import FilterPanel from '@/components/dashboard/FilterPanel';
import SortDropdown from '@/components/dashboard/SortDropdown';
import ProgressBar from '@/components/dashboard/ProgressBar';
import StatsSkeleton from '@/components/dashboard/StatsSkeleton';
import TaskListSkeleton from '@/components/dashboard/TaskListSkeleton';
import BulkActionsToolbar from '@/components/dashboard/BulkActionsToolbar';
import GroupByDropdown, { GroupByOption } from '@/components/dashboard/GroupByDropdown';
import ExportDropdown from '@/components/dashboard/ExportDropdown';
import KeyboardShortcutsModal from '@/components/dashboard/KeyboardShortcutsModal';
import NotificationSettings from '@/components/notifications/NotificationSettings';
import NotificationBell from '@/components/notifications/NotificationBell';
import TemplateManager from '@/components/templates/TemplateManager';
import FloatingChatButton from '@/components/chat/FloatingChatButton';
import Modal from '@/components/ui/Modal';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import { useRouter, useSearchParams } from 'next/navigation';
import { groupTasks } from '@/lib/taskGrouping';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';
import '../../dashboard.css';

function DashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { registerRefresh, unregisterRefresh } = useRefresh();
  const {
    tasks,
    isLoading,
    filters,
    sort,
    setFilters,
    setSort,
    clearFilters,
    createTask,
    updateTask,
    toggleComplete,
    refreshTasks,
  } = useTasks();

  // Notification system
  const {
    permission,
    isEnabled: notificationsEnabled,
    toggleNotifications,
    requestPermission,
  } = useNotifications(tasks);

  // Templates
  const {
    templates,
    createTemplate,
    updateTemplate,
    deleteTemplate,
  } = useTemplates();

  // Statistics
  const { stats, refetch: refetchStats } = useStats();

  // Tags
  const { tags } = useTags();

  // State
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isNotificationSettingsOpen, setIsNotificationSettingsOpen] = useState(false);
  const [isTemplateManagerOpen, setIsTemplateManagerOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [viewingTask, setViewingTask] = useState<Task | null>(null);
  const [deletingTaskId, setDeletingTaskId] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [showFilterPanel, setShowFilterPanel] = useState(false);
  const [bulkSelectionMode, setBulkSelectionMode] = useState(false);
  const [selectedTaskIds, setSelectedTaskIds] = useState<Set<number>>(new Set());
  const [groupBy, setGroupBy] = useState<GroupByOption>('none');
  const [isShortcutsModalOpen, setIsShortcutsModalOpen] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  /**
   * Initialize state from URL parameters
   */
  useEffect(() => {
    const search = searchParams.get('search');
    if (search) setSearchQuery(search);
  }, [searchParams]);

  /**
   * Update URL parameters when state changes
   */
  useEffect(() => {
    const params = new URLSearchParams();

    if (debouncedSearch) params.set('search', debouncedSearch);
    if (filters.status && filters.status !== 'all') params.set('status', filters.status);
    if (filters.priority) params.set('priority', filters.priority);
    if (filters.due_date_filter) params.set('due_date_filter', filters.due_date_filter);
    if (sort.sort_by) params.set('sort_by', sort.sort_by);
    if (sort.sort_order) params.set('sort_order', sort.sort_order);

    const newUrl = params.toString() ? `?${params.toString()}` : '/dashboard';
    router.replace(newUrl, { scroll: false });
  }, [debouncedSearch, filters, sort, router]);

  /**
   * Debounce search input (300ms delay)
   */
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      // Update filters with search query
      setFilters({ ...filters, search: searchQuery || undefined });
    }, 300);

    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery]);

  /**
   * Register refresh callbacks for chatbot auto-refresh
   */
  useEffect(() => {
    registerRefresh('dashboard-tasks', refreshTasks);
    registerRefresh('dashboard-stats', refetchStats);

    return () => {
      unregisterRefresh('dashboard-tasks');
      unregisterRefresh('dashboard-stats');
    };
  }, [registerRefresh, unregisterRefresh, refreshTasks, refetchStats]);

  /**
   * Redirect to login if not authenticated
   */
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  /**
   * Handle create task
   */
  const handleCreateTask = async (data: TaskCreateRequest | TaskUpdateRequest) => {
    setIsSubmitting(true);
    try {
      await createTask(data as TaskCreateRequest);
      setIsCreateModalOpen(false);
      // Refetch statistics after creating a task
      refetchStats();
    } catch (error) {
      console.error('Failed to create task:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Handle edit task
   */
  const handleEditTask = async (data: TaskCreateRequest | TaskUpdateRequest) => {
    if (!editingTask) return;

    setIsSubmitting(true);
    try {
      await updateTask(editingTask.id, data as TaskUpdateRequest);
      setIsEditModalOpen(false);
      setEditingTask(null);
      // Refetch statistics after updating a task
      refetchStats();
    } catch (error) {
      console.error('Failed to update task:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Close edit modal
   */
  const handleCloseEdit = () => {
    setIsEditModalOpen(false);
    setEditingTask(null);
  };

  /**
   * Handle task checkbox toggle
   */
  const handleToggleComplete = async (taskId: number) => {
    try {
      const task = tasks.find(t => t.id === taskId);
      if (task) {
        await toggleComplete(task.id, !task.completed);
        // Refetch statistics after toggling completion
        refetchStats();
      }
    } catch (error) {
      console.error('Failed to toggle task:', error);
    }
  };

  /**
   * Handle view task details
   */
  const handleViewTask = (task: Task) => {
    setViewingTask(task);
    setIsDetailModalOpen(true);
  };

  /**
   * Handle edit from detail modal
   */
  const handleEditFromDetail = (task: Task) => {
    setEditingTask(task);
    setIsEditModalOpen(true);
    setIsDetailModalOpen(false);
  };

  /**
   * Handle delete task
   */
  const handleDeleteTask = (taskId: number) => {
    setDeletingTaskId(taskId);
  };

  /**
   * Confirm delete task
   */
  const confirmDeleteTask = async () => {
    if (!deletingTaskId) return;

    try {
      const { deleteTask } = await import('@/lib/tasks-api');
      await deleteTask(deletingTaskId);
      setDeletingTaskId(null);
      setIsDetailModalOpen(false);
      // Refetch statistics after deleting a task
      refetchStats();
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };

  /**
   * Toggle bulk selection mode
   */
  const toggleBulkSelectionMode = () => {
    setBulkSelectionMode(!bulkSelectionMode);
    setSelectedTaskIds(new Set());
  };

  /**
   * Toggle task selection
   */
  const toggleTaskSelection = (taskId: number) => {
    const newSelected = new Set(selectedTaskIds);
    if (newSelected.has(taskId)) {
      newSelected.delete(taskId);
    } else {
      newSelected.add(taskId);
    }
    setSelectedTaskIds(newSelected);
  };

  /**
   * Handle bulk mark complete
   */
  const handleBulkMarkComplete = async () => {
    try {
      const promises = Array.from(selectedTaskIds).map(taskId =>
        toggleComplete(taskId, true)
      );
      await Promise.all(promises);
      setSelectedTaskIds(new Set());
      setBulkSelectionMode(false);
      refetchStats();
    } catch (error) {
      console.error('Failed to mark tasks as complete:', error);
    }
  };

  /**
   * Handle bulk mark incomplete
   */
  const handleBulkMarkIncomplete = async () => {
    try {
      const promises = Array.from(selectedTaskIds).map(taskId =>
        toggleComplete(taskId, false)
      );
      await Promise.all(promises);
      setSelectedTaskIds(new Set());
      setBulkSelectionMode(false);
      refetchStats();
    } catch (error) {
      console.error('Failed to mark tasks as incomplete:', error);
    }
  };

  /**
   * Handle bulk delete
   */
  const handleBulkDelete = async () => {
    if (selectedTaskIds.size === 0) return;

    const confirmed = window.confirm(
      `Are you sure you want to delete ${selectedTaskIds.size} task${selectedTaskIds.size > 1 ? 's' : ''}?`
    );

    if (!confirmed) return;

    try {
      const { deleteTask } = await import('@/lib/tasks-api');
      const promises = Array.from(selectedTaskIds).map(taskId =>
        deleteTask(taskId)
      );
      await Promise.all(promises);
      setSelectedTaskIds(new Set());
      setBulkSelectionMode(false);
      refetchStats();
    } catch (error) {
      console.error('Failed to delete tasks:', error);
    }
  };

  /**
   * Cancel bulk selection
   */
  const handleCancelBulkSelection = () => {
    setSelectedTaskIds(new Set());
    setBulkSelectionMode(false);
  };

  /**
   * Setup keyboard shortcuts
   */
  useKeyboardShortcuts({
    shortcuts: [
      {
        key: 'n',
        description: 'Create new task',
        action: () => setIsCreateModalOpen(true),
      },
      {
        key: 's',
        description: 'Focus search bar',
        action: () => searchInputRef.current?.focus(),
      },
      {
        key: 'f',
        description: 'Toggle filter panel',
        action: () => setShowFilterPanel(!showFilterPanel),
      },
      {
        key: 'Escape',
        description: 'Close modal or panel',
        action: () => {
          if (isCreateModalOpen) setIsCreateModalOpen(false);
          if (isEditModalOpen) handleCloseEdit();
          if (isDetailModalOpen) setIsDetailModalOpen(false);
          if (showFilterPanel) setShowFilterPanel(false);
          if (bulkSelectionMode) handleCancelBulkSelection();
        },
      },
      {
        key: '?',
        description: 'Show keyboard shortcuts',
        action: () => setIsShortcutsModalOpen(true),
      },
    ],
    enabled: !isSubmitting,
  });

  /**
   * Show loading state while checking authentication
   */
  if (authLoading) {
    return (
      <div className="dashboard-loading" style={{ minHeight: '100vh', background: '#000000' }}>
        <div className="dashboard-spinner"></div>
      </div>
    );
  }

  /**
   * Don't render if not authenticated (will redirect)
   */
  if (!isAuthenticated) {
    return null;
  }

  // Calculate statistics from API or fallback to local calculation
  const totalTasks = stats?.total_tasks ?? tasks.length;
  const completedTasks = stats?.completed_tasks ?? tasks.filter((t) => t.completed).length;
  const inProgressTasks = stats?.in_progress_tasks ?? tasks.filter((t) => !t.completed).length;
  const pendingTasks = inProgressTasks;

  // Calculate percentages
  const completedPercentage = stats?.completion_rate ?? (totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0);
  const inProgressPercentage = totalTasks > 0 ? Math.round((inProgressTasks / totalTasks) * 100) : 0;

  // Tasks are already filtered by the backend via useTasks hook
  // No need for local filtering
  const filteredTasks = tasks;

  // Group tasks based on selected grouping option
  const groupedTasks = groupTasks(filteredTasks, groupBy);

  return (
    <div className="dashboard-page">
      <div className="dashboard-content-wrapper">
        {/* Header */}
        <header className="dashboard-header">
          <div className="dashboard-search-bar">
            <svg className="dashboard-search-icon" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd"/>
            </svg>
            <input
              type="text"
              className="dashboard-search-input"
              placeholder="Search tasks by title or description..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              ref={searchInputRef}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="dashboard-search-clear"
                aria-label="Clear search"
              >
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          <div className="dashboard-header-actions">
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="dashboard-btn-new-task"
            >
              <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span>New Task</span>
            </button>

            {/* Notification Bell with full functionality */}
            <NotificationBell />

            {/* Templates Icon */}
            <button
              onClick={() => setIsTemplateManagerOpen(true)}
              className="dashboard-icon-btn"
              title="Templates"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </button>

            {/* Settings Icon */}
            <button
              onClick={() => setIsNotificationSettingsOpen(true)}
              className="dashboard-icon-btn"
              title="Settings"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="dashboard-content">
          <h1 className="dashboard-page-title">Dashboard</h1>
          <p className="dashboard-page-subtitle">
            Welcome back! Here&apos;s what&apos;s happening with your tasks today.
          </p>

          {/* Stats Grid */}
          {isLoading ? (
            <StatsSkeleton />
          ) : (
            <div className="dashboard-stats-grid">
              <div className="dashboard-stat-card stat-card-animated">
                <div className="dashboard-stat-header">
                  <div className="dashboard-stat-label">Total Tasks</div>
                  <div className="dashboard-stat-icon total">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                </div>
                <div className="dashboard-stat-value">{totalTasks}</div>
                <div className="dashboard-stat-change">All your tasks</div>
              </div>

              <div className="dashboard-stat-card stat-card-animated" style={{ animationDelay: '0.1s' }}>
                <div className="dashboard-stat-header">
                  <div className="dashboard-stat-label">In Progress</div>
                  <div className="dashboard-stat-icon progress">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                </div>
                <div className="dashboard-stat-value">{inProgressTasks}</div>
                <div className="dashboard-stat-progress">
                  <ProgressBar
                    value={inProgressPercentage}
                    color="primary"
                    showLabel={false}
                    height="sm"
                  />
                  <span className="dashboard-progress-text">{inProgressPercentage}% of total</span>
                </div>
              </div>

              <div className="dashboard-stat-card stat-card-animated" style={{ animationDelay: '0.2s' }}>
                <div className="dashboard-stat-header">
                  <div className="dashboard-stat-label">Completed</div>
                  <div className="dashboard-stat-icon completed">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div className="dashboard-stat-value">{completedTasks}</div>
                <div className="dashboard-stat-progress">
                  <ProgressBar
                    value={completedPercentage}
                    color="success"
                    showLabel={false}
                    height="sm"
                  />
                  <span className="dashboard-progress-text">{completedPercentage}% completion rate</span>
                </div>
              </div>

              <div className="dashboard-stat-card stat-card-animated" style={{ animationDelay: '0.3s' }}>
                <div className="dashboard-stat-header">
                  <div className="dashboard-stat-label">Pending</div>
                  <div className="dashboard-stat-icon pending">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div className="dashboard-stat-value">{pendingTasks}</div>
                <div className="dashboard-stat-change">Awaiting action</div>
              </div>
            </div>
          )}

          {/* Tasks Section */}
          <div className="dashboard-tasks-section">
            <div className="dashboard-section-header">
              <h2 className="dashboard-section-title">Recent Tasks</h2>

              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
                {/* Bulk Selection Toggle */}
                <button
                  onClick={toggleBulkSelectionMode}
                  className={`dashboard-filter-toggle ${bulkSelectionMode ? 'active' : ''}`}
                  title="Bulk selection mode"
                >
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  <span>Bulk Select</span>
                </button>

                {/* Filter Tabs */}
                <div className="dashboard-filter-tabs">
                  <button
                    className={`dashboard-filter-tab ${(!filters.status || filters.status === 'all') ? 'active' : ''}`}
                    onClick={() => setFilters({ ...filters, status: 'all' })}
                  >
                    All
                  </button>
                  <button
                    className={`dashboard-filter-tab ${filters.status === 'pending' ? 'active' : ''}`}
                    onClick={() => setFilters({ ...filters, status: 'pending' })}
                  >
                    Active
                  </button>
                  <button
                    className={`dashboard-filter-tab ${filters.status === 'completed' ? 'active' : ''}`}
                    onClick={() => setFilters({ ...filters, status: 'completed' })}
                  >
                    Completed
                  </button>
                </div>

                {/* Advanced Filters Toggle */}
                <button
                  onClick={() => setShowFilterPanel(!showFilterPanel)}
                  className="dashboard-filter-toggle"
                  title="Advanced filters"
                >
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                  </svg>
                  <span>Filters</span>
                </button>

                {/* Sort Dropdown */}
                <SortDropdown
                  sort={sort}
                  onSortChange={setSort}
                />

                {/* Group By Dropdown */}
                <GroupByDropdown
                  value={groupBy}
                  onChange={setGroupBy}
                />

                {/* Export Dropdown */}
                <ExportDropdown tasks={filteredTasks} />
              </div>
            </div>

            {/* Advanced Filter Panel */}
            {showFilterPanel && (
              <div style={{ marginBottom: '1.5rem' }}>
                <FilterPanel
                  filters={filters}
                  onFiltersChange={setFilters}
                  onClearFilters={clearFilters}
                  availableTags={tags}
                />
              </div>
            )}

            {/* Task List */}
            {isLoading ? (
              <TaskListSkeleton />
            ) : filteredTasks.length === 0 ? (
              <div className="dashboard-empty-state">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3>No tasks found</h3>
                <p>Create your first task to get started</p>
              </div>
            ) : (
              <div>
                {groupedTasks.map((group) => (
                  <div key={group.key} className="task-group">
                    {groupBy !== 'none' && (
                      <div className="task-group-header">
                        <h3 className="task-group-title">
                          {group.label}
                          <span className="task-group-count">{group.count}</span>
                        </h3>
                      </div>
                    )}
                    <div className="task-group-tasks">
                      {group.tasks.map((task) => (
                        <div
                          key={task.id}
                          className={`dashboard-task-item ${selectedTaskIds.has(task.id) ? 'selected' : ''}`}
                          onClick={() => bulkSelectionMode ? toggleTaskSelection(task.id) : handleViewTask(task)}
                        >
                          {bulkSelectionMode ? (
                            <div
                              className={`dashboard-task-bulk-checkbox ${selectedTaskIds.has(task.id) ? 'checked' : ''}`}
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleTaskSelection(task.id);
                              }}
                            >
                              {selectedTaskIds.has(task.id) && (
                                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                </svg>
                              )}
                            </div>
                          ) : (
                            <div
                              className={`dashboard-task-checkbox ${task.completed ? 'checked' : ''}`}
                              onClick={(e) => {
                                e.stopPropagation();
                                handleToggleComplete(task.id);
                              }}
                            ></div>
                          )}
                          <div className="dashboard-task-content">
                            <div className={`dashboard-task-title ${task.completed ? 'completed' : ''}`}>
                              {task.title}
                            </div>
                            <div className="dashboard-task-meta">
                              {task.due_date && (
                                <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
                              )}
                              {task.due_date && <span>•</span>}
                              <span>Status: {task.completed ? 'Completed' : 'In Progress'}</span>
                            </div>
                          </div>
                          {!bulkSelectionMode && (
                            <>
                              <div className="dashboard-task-actions">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setEditingTask(task);
                                    setIsEditModalOpen(true);
                                  }}
                                  className="dashboard-task-action-btn edit"
                                  title="Edit task"
                                >
                                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                  </svg>
                                </button>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDeleteTask(task.id);
                                  }}
                                  className="dashboard-task-action-btn delete"
                                  title="Delete task"
                                >
                                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                  </svg>
                                </button>
                              </div>
                              <div className={`dashboard-task-priority dashboard-priority-${task.priority || 'medium'}`}>
                                {(task.priority || 'medium').charAt(0).toUpperCase() + (task.priority || 'medium').slice(1)}
                              </div>
                            </>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create Task Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Task"
      >
        <TaskForm
          onSubmit={handleCreateTask}
          onCancel={() => setIsCreateModalOpen(false)}
          isLoading={isSubmitting}
        />
      </Modal>

      {/* Edit Task Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={handleCloseEdit}
        title="Edit Task"
      >
        {editingTask && (
          <TaskForm
            task={editingTask}
            onSubmit={handleEditTask}
            onCancel={handleCloseEdit}
            isLoading={isSubmitting}
          />
        )}
      </Modal>

      {/* Notification Settings Modal */}
      <Modal
        isOpen={isNotificationSettingsOpen}
        onClose={() => setIsNotificationSettingsOpen(false)}
        title="Notification Settings"
      >
        <NotificationSettings
          isEnabled={notificationsEnabled}
          permission={permission}
          onToggle={toggleNotifications}
          onRequestPermission={requestPermission}
        />
      </Modal>

      {/* Template Manager Modal */}
      <Modal
        isOpen={isTemplateManagerOpen}
        onClose={() => setIsTemplateManagerOpen(false)}
        title="Template Manager"
      >
        <TemplateManager
          templates={templates}
          onCreateTemplate={createTemplate}
          onUpdateTemplate={updateTemplate}
          onDeleteTemplate={deleteTemplate}
        />
      </Modal>

      {/* Task Detail Modal */}
      <TaskDetailModal
        task={viewingTask}
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setViewingTask(null);
        }}
        onEdit={handleEditFromDetail}
        onDelete={handleDeleteTask}
      />

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deletingTaskId !== null}
        title="Delete Task"
        message={`Are you sure you want to delete this task? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        variant="danger"
        onConfirm={confirmDeleteTask}
        onCancel={() => setDeletingTaskId(null)}
      />

      {/* Floating Chat Button */}
      <FloatingChatButton />

      {/* Bulk Actions Toolbar */}
      <BulkActionsToolbar
        selectedCount={selectedTaskIds.size}
        onMarkComplete={handleBulkMarkComplete}
        onMarkIncomplete={handleBulkMarkIncomplete}
        onDelete={handleBulkDelete}
        onCancel={handleCancelBulkSelection}
      />

      {/* Keyboard Shortcuts Modal */}
      <KeyboardShortcutsModal
        isOpen={isShortcutsModalOpen}
        onClose={() => setIsShortcutsModalOpen(false)}
      />
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <DashboardContent />
    </Suspense>
  );
}
