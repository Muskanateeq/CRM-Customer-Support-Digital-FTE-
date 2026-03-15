/**
 * useTasks Hook
 *
 * Custom React hook for managing tasks with the backend API.
 * Provides CRUD operations, search, filter, sort, and state management.
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { api, APIError } from '@/lib/api';
import {
  Task,
  TaskCreateRequest,
  TaskUpdateRequest,
  TaskPriority,
} from '@/lib/types';
import { logActivity } from '@/lib/activityTracker';

/**
 * Task Filter Options
 */
export interface TaskFilters {
  search?: string;
  status?: 'all' | 'pending' | 'completed';
  priority?: TaskPriority;
  tag_ids?: number[];
  due_date_filter?: 'overdue' | 'today' | 'week' | 'month' | 'none';
}

/**
 * Task Sort Options
 */
export interface TaskSort {
  sort_by: 'created_at' | 'due_date' | 'priority' | 'title';
  sort_order: 'asc' | 'desc';
}

/**
 * useTasks Hook Return Type
 */
export interface UseTasksReturn {
  // State
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  filters: TaskFilters;
  sort: TaskSort;

  // Actions
  fetchTasks: () => Promise<void>;
  createTask: (data: TaskCreateRequest) => Promise<Task>;
  updateTask: (id: number, data: TaskUpdateRequest) => Promise<Task>;
  deleteTask: (id: number) => Promise<void>;
  toggleComplete: (id: number, completed: boolean) => Promise<Task>;

  // Filter & Sort
  setFilters: (filters: TaskFilters) => void;
  setSort: (sort: TaskSort) => void;
  clearFilters: () => void;

  // Utilities
  refreshTasks: () => Promise<void>;
  clearError: () => void;
}

/**
 * Default sort options
 */
const DEFAULT_SORT: TaskSort = {
  sort_by: 'created_at',
  sort_order: 'desc',
};

/**
 * Default filter options
 */
const DEFAULT_FILTERS: TaskFilters = {
  status: 'all',
};

/**
 * useTasks Hook
 *
 * Manages task state and provides methods for task operations.
 *
 * @example
 * function TaskList() {
 *   const { tasks, isLoading, createTask, deleteTask } = useTasks();
 *
 *   if (isLoading) return <Spinner />;
 *
 *   return (
 *     <div>
 *       {tasks.map(task => (
 *         <TaskItem key={task.id} task={task} onDelete={deleteTask} />
 *       ))}
 *     </div>
 *   );
 * }
 */
export function useTasks(): UseTasksReturn {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFiltersState] = useState<TaskFilters>(DEFAULT_FILTERS);
  const [sort, setSortState] = useState<TaskSort>(DEFAULT_SORT);

  /**
   * Build query parameters from filters and sort
   */
  const buildQueryParams = useCallback(() => {
    const params = new URLSearchParams();

    // Add search
    if (filters.search) {
      params.append('search', filters.search);
    }

    // Add status filter
    if (filters.status && filters.status !== 'all') {
      params.append('status', filters.status);
    }

    // Add priority filter
    if (filters.priority) {
      params.append('priority', filters.priority);
    }

    // Add tag filter
    if (filters.tag_ids && filters.tag_ids.length > 0) {
      params.append('tag_ids', filters.tag_ids.join(','));
    }

    // Add due date filter
    if (filters.due_date_filter) {
      params.append('due_date_filter', filters.due_date_filter);
    }

    // Add sort
    params.append('sort_by', sort.sort_by);
    params.append('sort_order', sort.sort_order);

    // Add pagination (get all for now)
    params.append('limit', '1000');
    params.append('offset', '0');

    return params.toString();
  }, [filters, sort]);

  /**
   * Fetch tasks from API
   */
  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const queryParams = buildQueryParams();
      const endpoint = `/tasks?${queryParams}`;
      const data = await api.get<Task[]>(endpoint);
      setTasks(data);
    } catch (err) {
      const errorMessage =
        err instanceof APIError
          ? err.message
          : 'Failed to fetch tasks. Please try again.';
      setError(errorMessage);
      console.error('Failed to fetch tasks:', err);
    } finally {
      setIsLoading(false);
    }
  }, [buildQueryParams]);

  /**
   * Create a new task
   */
  const createTask = useCallback(
    async (data: TaskCreateRequest): Promise<Task> => {
      setError(null);

      try {
        const newTask = await api.post<Task>('/tasks', data);

        // Optimistically add to list
        setTasks((prev) => [newTask, ...prev]);

        // Log activity
        logActivity(
          'created',
          'Task Created',
          `Created task: ${newTask.title}`,
          { taskName: newTask.title }
        );

        return newTask;
      } catch (err) {
        const errorMessage =
          err instanceof APIError
            ? err.message
            : 'Failed to create task. Please try again.';
        setError(errorMessage);
        throw err;
      }
    },
    []
  );

  /**
   * Update an existing task
   */
  const updateTask = useCallback(
    async (id: number, data: TaskUpdateRequest): Promise<Task> => {
      setError(null);

      try {
        // Get old task for comparison
        const oldTask = tasks.find(t => t.id === id);

        const updatedTask = await api.put<Task>(`/tasks/${id}`, data);

        // Update in list
        setTasks((prev) =>
          prev.map((task) => (task.id === id ? updatedTask : task))
        );

        // Log activity with changes
        if (oldTask) {
          const changes: string[] = [];
          if (data.title && data.title !== oldTask.title) {
            changes.push(`Title changed to "${data.title}"`);
          }
          if (data.priority && data.priority !== oldTask.priority) {
            changes.push(`Priority changed to ${data.priority}`);
          }
          if (data.due_date !== undefined && data.due_date !== oldTask.due_date) {
            changes.push(`Due date updated`);
          }

          logActivity(
            'updated',
            'Task Updated',
            `Updated task: ${updatedTask.title}`,
            { taskName: updatedTask.title, changes }
          );
        }

        return updatedTask;
      } catch (err) {
        const errorMessage =
          err instanceof APIError
            ? err.message
            : 'Failed to update task. Please try again.';
        setError(errorMessage);
        throw err;
      }
    },
    [tasks]
  );

  /**
   * Delete a task
   */
  const deleteTask = useCallback(async (id: number): Promise<void> => {
    setError(null);

    try {
      // Get task name before deleting
      const task = tasks.find(t => t.id === id);
      const taskName = task?.title || 'Unknown task';

      await api.delete(`/tasks/${id}`);

      // Remove from list
      setTasks((prev) => prev.filter((task) => task.id !== id));

      // Log activity
      logActivity(
        'deleted',
        'Task Deleted',
        `Deleted task: ${taskName}`,
        { taskName }
      );
    } catch (err) {
      const errorMessage =
        err instanceof APIError
          ? err.message
          : 'Failed to delete task. Please try again.';
      setError(errorMessage);
      throw err;
    }
  }, [tasks]);

  /**
   * Toggle task completion status
   */
  const toggleComplete = useCallback(
    async (id: number, completed: boolean): Promise<Task> => {
      setError(null);

      // Get task name before toggling
      const task = tasks.find(t => t.id === id);
      const taskName = task?.title || 'Unknown task';

      // Optimistic update
      setTasks((prev) =>
        prev.map((task) =>
          task.id === id ? { ...task, completed } : task
        )
      );

      try {
        const updatedTask = await api.patch<Task>(`/tasks/${id}/complete`, {
          completed,
        });

        // Update with server response
        setTasks((prev) =>
          prev.map((task) => (task.id === id ? updatedTask : task))
        );

        // Log activity
        logActivity(
          completed ? 'completed' : 'uncompleted',
          completed ? 'Task Completed' : 'Task Uncompleted',
          `${completed ? 'Completed' : 'Uncompleted'} task: ${taskName}`,
          { taskName }
        );

        return updatedTask;
      } catch (err) {
        // Revert optimistic update on error
        setTasks((prev) =>
          prev.map((task) =>
            task.id === id ? { ...task, completed: !completed } : task
          )
        );

        const errorMessage =
          err instanceof APIError
            ? err.message
            : 'Failed to update task. Please try again.';
        setError(errorMessage);
        throw err;
      }
    },
    [tasks]
  );

  /**
   * Set filters and refetch tasks
   */
  const setFilters = useCallback((newFilters: TaskFilters) => {
    setFiltersState(newFilters);
  }, []);

  /**
   * Set sort options and refetch tasks
   */
  const setSort = useCallback((newSort: TaskSort) => {
    setSortState(newSort);
  }, []);

  /**
   * Clear all filters
   */
  const clearFilters = useCallback(() => {
    setFiltersState(DEFAULT_FILTERS);
  }, []);

  /**
   * Refresh tasks (alias for fetchTasks)
   */
  const refreshTasks = useCallback(async () => {
    await fetchTasks();
  }, [fetchTasks]);

  /**
   * Clear error message
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Fetch tasks on mount and when filters/sort change
   */
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  return {
    // State
    tasks,
    isLoading,
    error,
    filters,
    sort,

    // Actions
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,

    // Filter & Sort
    setFilters,
    setSort,
    clearFilters,

    // Utilities
    refreshTasks,
    clearError,
  };
}
