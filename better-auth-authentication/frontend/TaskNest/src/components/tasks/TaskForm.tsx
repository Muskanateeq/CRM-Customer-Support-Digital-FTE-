/**
 * TaskForm Component
 * Dark Golden Theme - Modern SaaS Design
 */

'use client';

import React, { useState } from 'react';
import { Task, TaskCreateRequest, TaskUpdateRequest, TaskPriority, RecurrencePattern, TaskTemplate } from '@/lib/types';
import TagSelector from '@/components/tags/TagSelector';
import RecurrenceSelector from './RecurrenceSelector';
import TemplateSelector from '@/components/templates/TemplateSelector';
import { useTemplates } from '@/hooks/useTemplates';
import './TaskForm.css';

/**
 * TaskForm Props
 */
interface TaskFormProps {
  task?: Task; // If provided, form is in edit mode
  onSubmit: (data: TaskCreateRequest | TaskUpdateRequest) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

/**
 * TaskForm Component
 */
export default function TaskForm({
  task,
  onSubmit,
  onCancel,
  isLoading = false,
}: TaskFormProps) {
  // Templates
  const { templates, incrementUseCount } = useTemplates();
  const [showTemplates, setShowTemplates] = useState(!task); // Show templates only for new tasks
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | undefined>();

  // Form state
  const [title, setTitle] = useState(task?.title || '');
  const [description, setDescription] = useState(task?.description || '');
  const [priority, setPriority] = useState<TaskPriority>(
    task?.priority || TaskPriority.MEDIUM
  );
  const [dueDate, setDueDate] = useState(task?.due_date || '');
  const [dueTime, setDueTime] = useState(task?.due_time || '');
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>(
    task?.tags?.map((tag) => tag.id) || []
  );
  const [recurrencePattern, setRecurrencePattern] = useState<RecurrencePattern | undefined>(
    task?.recurrence_pattern
  );
  const [errors, setErrors] = useState<Record<string, string>>({});

  const isEditMode = !!task;

  /**
   * Apply template to form
   */
  const handleTemplateSelect = (template: TaskTemplate) => {
    setSelectedTemplateId(template.id);

    // Apply template values
    if (template.template_title) {
      setTitle(template.template_title);
    }
    if (template.template_description) {
      setDescription(template.template_description);
    }
    setPriority(template.priority);
    if (template.tag_ids) {
      setSelectedTagIds(template.tag_ids);
    }
    if (template.recurrence_pattern) {
      setRecurrencePattern(template.recurrence_pattern);
    }

    // Increment use count
    incrementUseCount(template.id);

    // Hide template selector after selection
    setShowTemplates(false);
  };

  /**
   * Toggle template selector
   */
  const handleToggleTemplates = () => {
    setShowTemplates(!showTemplates);
  };

  /**
   * Validate form
   */
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Title is required
    if (!title.trim()) {
      newErrors.title = 'Title is required';
    } else if (title.length > 200) {
      newErrors.title = 'Title must be 200 characters or less';
    }

    // Description max length
    if (description && description.length > 1000) {
      newErrors.description = 'Description must be 1000 characters or less';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    const formData: TaskCreateRequest | TaskUpdateRequest = {
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
      due_date: dueDate || undefined,
      due_time: dueTime || undefined,
      tag_ids: selectedTagIds.length > 0 ? selectedTagIds : undefined,
      recurrence_pattern: recurrencePattern,
    };

    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  /**
   * Handle cancel
   */
  const handleCancel = () => {
    onCancel();
  };

  return (
    <form onSubmit={handleSubmit} className="task-form">
      {/* Template Selector - Only for new tasks */}
      {!isEditMode && (
        <div className="task-form-template-section">
          <button
            type="button"
            onClick={handleToggleTemplates}
            className="task-form-template-toggle"
          >
            <div className="task-form-template-toggle-content">
              <div className="task-form-template-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="task-form-template-text">
                <div className="task-form-template-title">
                  {showTemplates ? 'Hide Templates' : 'Use a Template'}
                </div>
                <div className="task-form-template-subtitle">
                  {showTemplates ? 'Start from scratch' : 'Quick start with pre-configured settings'}
                </div>
              </div>
            </div>
            <svg className={`task-form-template-arrow ${showTemplates ? 'rotated' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showTemplates && (
            <div className="task-form-template-selector">
              <TemplateSelector
                templates={templates}
                onSelect={handleTemplateSelect}
                selectedId={selectedTemplateId}
              />
            </div>
          )}
        </div>
      )}

      {/* Title */}
      <div className="task-form-field">
        <label htmlFor="title" className="task-form-label">
          Title <span className="task-form-required">*</span>
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter task title"
          disabled={isLoading}
          className={`task-form-input ${errors.title ? 'error' : ''}`}
        />
        {errors.title && (
          <div className="task-form-error">
            <svg fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {errors.title}
          </div>
        )}
      </div>

      {/* Description */}
      <div className="task-form-field">
        <label htmlFor="description" className="task-form-label">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter task description (optional)"
          disabled={isLoading}
          className={`task-form-textarea ${errors.description ? 'error' : ''}`}
        />
        {errors.description && (
          <div className="task-form-error">
            <svg fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {errors.description}
          </div>
        )}
      </div>

      {/* Priority */}
      <div className="task-form-field">
        <label className="task-form-label">Priority</label>
        <div className="task-form-priority-grid">
          <button
            type="button"
            onClick={() => setPriority(TaskPriority.HIGH)}
            disabled={isLoading}
            className={`task-form-priority-btn high ${priority === TaskPriority.HIGH ? 'active' : ''}`}
          >
            🔥 High
          </button>
          <button
            type="button"
            onClick={() => setPriority(TaskPriority.MEDIUM)}
            disabled={isLoading}
            className={`task-form-priority-btn medium ${priority === TaskPriority.MEDIUM ? 'active' : ''}`}
          >
            ⚡ Medium
          </button>
          <button
            type="button"
            onClick={() => setPriority(TaskPriority.LOW)}
            disabled={isLoading}
            className={`task-form-priority-btn low ${priority === TaskPriority.LOW ? 'active' : ''}`}
          >
            📌 Low
          </button>
        </div>
      </div>

      {/* Tags */}
      <div className="task-form-field">
        <label className="task-form-label">Tags</label>
        <TagSelector
          selectedTagIds={selectedTagIds}
          onChange={setSelectedTagIds}
          disabled={isLoading}
          placeholder="Add tags to organize your task..."
        />
      </div>

      {/* Recurrence */}
      <div className="task-form-field">
        <RecurrenceSelector
          value={recurrencePattern}
          onChange={setRecurrencePattern}
          disabled={isLoading}
        />
      </div>

      {/* Due Date and Time */}
      <div className="task-form-datetime-grid">
        <div className="task-form-field">
          <label htmlFor="dueDate" className="task-form-label">
            Due Date
          </label>
          <input
            id="dueDate"
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            disabled={isLoading}
            className="task-form-input"
          />
        </div>

        <div className="task-form-field">
          <label htmlFor="dueTime" className="task-form-label">
            Due Time
          </label>
          <input
            id="dueTime"
            type="time"
            value={dueTime}
            onChange={(e) => setDueTime(e.target.value)}
            disabled={isLoading}
            className="task-form-input"
          />
        </div>
      </div>

      {/* Form Actions */}
      <div className="task-form-actions">
        <button
          type="button"
          onClick={handleCancel}
          className="task-form-btn task-form-btn-secondary"
          disabled={isLoading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="task-form-btn task-form-btn-primary"
          disabled={isLoading}
        >
          {isLoading ? (
            <div className="task-form-loading">
              <div className="task-form-spinner"></div>
              <span>{isEditMode ? 'Updating...' : 'Creating...'}</span>
            </div>
          ) : (
            <span>{isEditMode ? 'Update Task' : 'Create Task'}</span>
          )}
        </button>
      </div>
    </form>
  );
}
