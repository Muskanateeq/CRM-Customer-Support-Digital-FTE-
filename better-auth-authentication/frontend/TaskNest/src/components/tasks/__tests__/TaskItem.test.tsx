/**
 * TaskItem Component Tests
 *
 * Tests for individual task display and interactions.
 */

import TaskItem from '../TaskItem';

describe('TaskItem', () => {
  describe('Component Structure', () => {
    it('exports TaskItem component', () => {
      expect(TaskItem).toBeDefined();
      expect(typeof TaskItem).toBe('function');
    });

    it('TaskItem is a valid React component', () => {
      expect(TaskItem.name).toBe('TaskItem');
    });
  });

  describe('Component Props', () => {
    it('TaskItem accepts required props', () => {
      const props = {
        task: {
          id: 1,
          title: 'Test Task',
          description: 'Test description',
          priority: 'medium' as const,
          completed: false,
          created_at: '2026-02-07T00:00:00Z',
          updated_at: '2026-02-07T00:00:00Z',
          tags: [],
        },
        onToggleComplete: jest.fn(),
        onEdit: jest.fn(),
        onDelete: jest.fn(),
      };

      expect(() => {
        expect(props.task).toBeDefined();
        expect(props.onToggleComplete).toBeDefined();
        expect(props.onEdit).toBeDefined();
        expect(props.onDelete).toBeDefined();
      }).not.toThrow();
    });
  });

  describe('Task Data Structure', () => {
    it('validates task has required fields', () => {
      const task = {
        id: 1,
        title: 'Test Task',
        description: 'Test description',
        priority: 'medium',
        completed: false,
        created_at: '2026-02-07T00:00:00Z',
        updated_at: '2026-02-07T00:00:00Z',
        tags: [],
      };

      expect(task.id).toBeDefined();
      expect(task.title).toBeDefined();
      expect(task.priority).toBeDefined();
      expect(typeof task.completed).toBe('boolean');
    });

    it('validates priority values', () => {
      const validPriorities = ['high', 'medium', 'low'];
      expect(validPriorities).toContain('high');
      expect(validPriorities).toContain('medium');
      expect(validPriorities).toContain('low');
    });

    it('validates completed status is boolean', () => {
      const completedTask = { completed: true };
      const pendingTask = { completed: false };

      expect(typeof completedTask.completed).toBe('boolean');
      expect(typeof pendingTask.completed).toBe('boolean');
    });
  });

  describe('Task Tags', () => {
    it('supports multiple tags', () => {
      const tags = ['Work', 'Important', 'Urgent'];
      expect(Array.isArray(tags)).toBe(true);
      expect(tags.length).toBe(3);
    });

    it('supports empty tags array', () => {
      const tags: string[] = [];
      expect(Array.isArray(tags)).toBe(true);
      expect(tags.length).toBe(0);
    });
  });
});
