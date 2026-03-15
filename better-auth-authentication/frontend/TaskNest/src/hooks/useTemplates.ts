/**
 * useTemplates Hook - Task Template Management
 *
 * Features:
 * - CRUD operations for templates
 * - LocalStorage persistence
 * - Template usage tracking
 * - Default templates
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { TaskTemplate, TemplateCreateRequest, TemplateUpdateRequest, TaskPriority } from '@/lib/types';

const STORAGE_KEY = 'tasknest_templates';

interface UseTemplatesReturn {
  templates: TaskTemplate[];
  isLoading: boolean;
  error: string | null;
  createTemplate: (data: TemplateCreateRequest) => Promise<TaskTemplate>;
  updateTemplate: (id: string, data: TemplateUpdateRequest) => Promise<TaskTemplate>;
  deleteTemplate: (id: string) => Promise<void>;
  incrementUseCount: (id: string) => void;
  clearError: () => void;
}

/**
 * Default templates
 */
const DEFAULT_TEMPLATES: TaskTemplate[] = [
  {
    id: 'default-1',
    name: 'Daily Standup',
    description: 'Daily team standup meeting',
    icon: '👥',
    template_title: 'Daily Standup',
    template_description: 'Prepare updates for the team',
    priority: TaskPriority.MEDIUM,
    recurrence_pattern: {
      type: 'daily',
      interval: 1,
    },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    use_count: 0,
  },
  {
    id: 'default-2',
    name: 'Weekly Review',
    description: 'Review weekly progress and plan ahead',
    icon: '📊',
    template_title: 'Weekly Review',
    template_description: 'Review completed tasks and plan next week',
    priority: TaskPriority.HIGH,
    recurrence_pattern: {
      type: 'weekly',
      interval: 1,
      days_of_week: [1], // Monday
    },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    use_count: 0,
  },
  {
    id: 'default-3',
    name: 'Monthly Report',
    description: 'Prepare monthly progress report',
    icon: '📝',
    template_title: 'Monthly Report',
    template_description: 'Compile and submit monthly report',
    priority: TaskPriority.HIGH,
    recurrence_pattern: {
      type: 'monthly',
      interval: 1,
      day_of_month: 1,
    },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    use_count: 0,
  },
  {
    id: 'default-4',
    name: 'Quick Task',
    description: 'Simple one-time task',
    icon: '⚡',
    template_title: '',
    template_description: '',
    priority: TaskPriority.MEDIUM,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    use_count: 0,
  },
];

/**
 * Load templates from localStorage
 */
const loadTemplates = (): TaskTemplate[] => {
  if (typeof window === 'undefined') return DEFAULT_TEMPLATES;

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return DEFAULT_TEMPLATES;

    const parsed = JSON.parse(stored);
    return Array.isArray(parsed) ? parsed : DEFAULT_TEMPLATES;
  } catch (error) {
    console.error('Failed to load templates:', error);
    return DEFAULT_TEMPLATES;
  }
};

/**
 * Save templates to localStorage
 */
const saveTemplates = (templates: TaskTemplate[]): void => {
  if (typeof window === 'undefined') return;

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(templates));
  } catch (error) {
    console.error('Failed to save templates:', error);
  }
};

/**
 * Generate unique ID
 */
const generateId = (): string => {
  return `template-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * useTemplates Hook
 */
export function useTemplates(): UseTemplatesReturn {
  const [templates, setTemplates] = useState<TaskTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load templates on mount
   */
  useEffect(() => {
    try {
      const loaded = loadTemplates();
      setTemplates(loaded);
    } catch (err) {
      setError('Failed to load templates');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Create template
   */
  const createTemplate = useCallback(
    async (data: TemplateCreateRequest): Promise<TaskTemplate> => {
      try {
        const newTemplate: TaskTemplate = {
          id: generateId(),
          ...data,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          use_count: 0,
        };

        const updated = [...templates, newTemplate];
        setTemplates(updated);
        saveTemplates(updated);

        return newTemplate;
      } catch {
        const message = 'Failed to create template';
        setError(message);
        throw new Error(message);
      }
    },
    [templates]
  );

  /**
   * Update template
   */
  const updateTemplate = useCallback(
    async (id: string, data: TemplateUpdateRequest): Promise<TaskTemplate> => {
      try {
        const index = templates.findIndex((t) => t.id === id);
        if (index === -1) {
          throw new Error('Template not found');
        }

        const updatedTemplate: TaskTemplate = {
          ...templates[index],
          ...data,
          updated_at: new Date().toISOString(),
        };

        const updated = [...templates];
        updated[index] = updatedTemplate;

        setTemplates(updated);
        saveTemplates(updated);

        return updatedTemplate;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to update template';
        setError(message);
        throw new Error(message);
      }
    },
    [templates]
  );

  /**
   * Delete template
   */
  const deleteTemplate = useCallback(
    async (id: string): Promise<void> => {
      try {
        // Prevent deleting default templates
        if (id.startsWith('default-')) {
          throw new Error('Cannot delete default templates');
        }

        const updated = templates.filter((t) => t.id !== id);
        setTemplates(updated);
        saveTemplates(updated);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to delete template';
        setError(message);
        throw new Error(message);
      }
    },
    [templates]
  );

  /**
   * Increment use count
   */
  const incrementUseCount = useCallback(
    (id: string): void => {
      const index = templates.findIndex((t) => t.id === id);
      if (index === -1) return;

      const updated = [...templates];
      updated[index] = {
        ...updated[index],
        use_count: updated[index].use_count + 1,
      };

      setTemplates(updated);
      saveTemplates(updated);
    },
    [templates]
  );

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    templates,
    isLoading,
    error,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    incrementUseCount,
    clearError,
  };
}
