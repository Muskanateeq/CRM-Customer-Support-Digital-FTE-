/**
 * useTasks Hook Tests
 *
 * Tests for task management custom hook.
 */

import { renderHook } from '@testing-library/react';
import { useTasks } from '../useTasks';

// Mock the tasks-api module
jest.mock('@/lib/tasks-api', () => ({
  getTasks: jest.fn(() => Promise.resolve([])),
  createTask: jest.fn((data) => Promise.resolve({ id: 1, ...data, completed: false })),
  updateTask: jest.fn((id, data) => Promise.resolve({ id, ...data })),
  deleteTask: jest.fn(() => Promise.resolve()),
  toggleTaskCompletion: jest.fn((id) => Promise.resolve({ id, completed: true })),
}));

describe('useTasks', () => {
  describe('Hook Structure', () => {
    it('returns an object with expected properties', () => {
      const { result } = renderHook(() => useTasks());

      expect(result.current).toHaveProperty('tasks');
      expect(result.current).toHaveProperty('isLoading');
      expect(result.current).toHaveProperty('error');
      expect(result.current).toHaveProperty('createTask');
      expect(result.current).toHaveProperty('updateTask');
      expect(result.current).toHaveProperty('deleteTask');
      expect(result.current).toHaveProperty('toggleComplete');
      expect(result.current).toHaveProperty('refreshTasks');
    });

    it('tasks is an array', () => {
      const { result } = renderHook(() => useTasks());

      expect(Array.isArray(result.current.tasks)).toBe(true);
    });

    it('isLoading is a boolean', () => {
      const { result } = renderHook(() => useTasks());

      expect(typeof result.current.isLoading).toBe('boolean');
    });

    it('createTask is a function', () => {
      const { result } = renderHook(() => useTasks());

      expect(typeof result.current.createTask).toBe('function');
    });

    it('updateTask is a function', () => {
      const { result } = renderHook(() => useTasks());

      expect(typeof result.current.updateTask).toBe('function');
    });

    it('deleteTask is a function', () => {
      const { result } = renderHook(() => useTasks());

      expect(typeof result.current.deleteTask).toBe('function');
    });

    it('toggleComplete is a function', () => {
      const { result } = renderHook(() => useTasks());

      expect(typeof result.current.toggleComplete).toBe('function');
    });

    it('refreshTasks is a function', () => {
      const { result } = renderHook(() => useTasks());

      expect(typeof result.current.refreshTasks).toBe('function');
    });
  });

  describe('Initial State', () => {
    it('starts with empty tasks array', () => {
      const { result } = renderHook(() => useTasks());

      expect(result.current.tasks).toEqual([]);
    });

    it('error is initially null or undefined', () => {
      const { result } = renderHook(() => useTasks());

      expect(result.current.error == null).toBe(true);
    });
  });
});
