/**
 * My Tasks Page - TaskNest
 * Personal task management with full CRUD operations
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useTasks } from '@/hooks/useTasks';
import { useAuth } from '@/contexts/AuthContext';
import { useRefresh } from '@/contexts/RefreshContext';
import { useRouter } from 'next/navigation';
import { Task, TaskCreateRequest, TaskUpdateRequest } from '@/lib/types';
import TaskForm from '@/components/tasks/TaskForm';
import TaskItem from '@/components/tasks/TaskItem';
import FilterPanel from '@/components/tasks/FilterPanel';
import SortDropdown from '@/components/tasks/SortDropdown';
import Modal from '@/components/ui/Modal';
import '../../dashboard.css';

export default function TasksPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { registerRefresh, unregisterRefresh } = useRefresh();
  const {
    tasks,
    isLoading,
    error,
    filters,
    sort,
    setFilters,
    setSort,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
    clearError,
    refreshTasks,
  } = useTasks();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);

  /**
   * Debounce search
   */
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setFilters({ ...filters, search: searchQuery });
    }, 300);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery]);

  /**
   * Register refresh callbacks for chatbot auto-refresh
   */
  useEffect(() => {
    registerRefresh('tasks-page', refreshTasks);

    return () => {
      unregisterRefresh('tasks-page');
    };
  }, [registerRefresh, unregisterRefresh, refreshTasks]);

  /**
   * Redirect if not authenticated
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
    } catch (error) {
      console.error('Failed to create task:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Handle update task
   */
  const handleUpdateTask = async (data: TaskUpdateRequest) => {
    if (!editingTask) return;
    setIsSubmitting(true);
    try {
      await updateTask(editingTask.id, data);
      setIsEditModalOpen(false);
      setEditingTask(null);
    } catch (error) {
      console.error('Failed to update task:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Handle toggle complete (wrapper for type compatibility)
   */
  const handleToggleComplete = async (id: number, completed: boolean): Promise<void> => {
    await toggleComplete(id, completed);
  };

  /**
   * Handle delete task
   */
  const handleDeleteTask = async (taskId: number) => {
    try {
      await deleteTask(taskId);
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };

  /**
   * Open edit modal
   */
  const openEditModal = (task: Task) => {
    setEditingTask(task);
    setIsEditModalOpen(true);
  };

  /**
   * Handle task selection
   */
  const handleTaskSelect = (task: Task) => {
    setSelectedTaskId(task.id === selectedTaskId ? null : task.id);
  };

  if (authLoading || !isAuthenticated) {
    return null;
  }

  const filteredTasks = tasks.filter(task => {
    if (debouncedSearch) {
      return task.title.toLowerCase().includes(debouncedSearch.toLowerCase());
    }
    return true;
  });

  return (
    <div className="tasks-page">
      {/* Header */}
      <div className="tasks-header">
        <div>
          <h1 className="tasks-title">My Tasks</h1>
          <p className="tasks-subtitle">Manage your personal tasks and to-dos</p>
        </div>
        <button onClick={() => setIsCreateModalOpen(true)} className="btn-create-task">
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>Add Task</span>
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="error-banner">
          <p>{error}</p>
          <button onClick={clearError}>Dismiss</button>
        </div>
      )}

      {/* Search and Filters */}
      <div className="tasks-controls">
        <div className="tasks-controls-top">
          <div className="search-box">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>
          <div className="tasks-controls-actions">
            <FilterPanel filters={filters} onFilterChange={setFilters} taskCount={tasks.length} />
            <SortDropdown currentSort={sort} onChange={setSort} />
          </div>
        </div>
      </div>

      {/* Tasks List */}
      {isLoading ? (
        <div className="loading-state">
          <div className="spinner"></div>
        </div>
      ) : filteredTasks.length === 0 ? (
        <div className="empty-state">
          <svg width="80" height="80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          <h3>No tasks found</h3>
          <p>Create your first task to get started</p>
          <button onClick={() => setIsCreateModalOpen(true)} className="btn-create-empty">
            Create Task
          </button>
        </div>
      ) : (
        <div className="tasks-list">
          {filteredTasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onToggleComplete={handleToggleComplete}
              onEdit={openEditModal}
              onDelete={handleDeleteTask}
              isSelected={task.id === selectedTaskId}
              onSelect={handleTaskSelect}
            />
          ))}
        </div>
      )}

      {/* Create Modal */}
      <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} title="Create New Task">
        <TaskForm
          onSubmit={handleCreateTask}
          onCancel={() => setIsCreateModalOpen(false)}
          isLoading={isSubmitting}
        />
      </Modal>

      {/* Edit Modal */}
      <Modal isOpen={isEditModalOpen} onClose={() => { setIsEditModalOpen(false); setEditingTask(null); }} title="Edit Task">
        {editingTask && (
          <TaskForm
            task={editingTask}
            onSubmit={handleUpdateTask}
            onCancel={() => { setIsEditModalOpen(false); setEditingTask(null); }}
            isLoading={isSubmitting}
          />
        )}
      </Modal>
    </div>
  );
}
