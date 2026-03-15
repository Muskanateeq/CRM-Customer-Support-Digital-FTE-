/**
 * TemplateManager Component
 * Dark Golden Theme - Modern SaaS Design
 */

'use client';

import React, { useState } from 'react';
import { TaskTemplate, TemplateCreateRequest, TemplateUpdateRequest, TaskPriority } from '@/lib/types';
import './TemplateManager.css';

export interface TemplateManagerProps {
  templates: TaskTemplate[];
  onCreateTemplate: (data: TemplateCreateRequest) => Promise<TaskTemplate>;
  onUpdateTemplate: (id: string, data: TemplateUpdateRequest) => Promise<TaskTemplate>;
  onDeleteTemplate: (id: string) => Promise<void>;
}

export default function TemplateManager({
  templates,
  onCreateTemplate,
  onUpdateTemplate,
  onDeleteTemplate,
}: TemplateManagerProps) {
  const [isCreating, setIsCreating] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [icon, setIcon] = useState('📋');
  const [templateTitle, setTemplateTitle] = useState('');
  const [templateDescription, setTemplateDescription] = useState('');
  const [priority, setPriority] = useState<TaskPriority>(TaskPriority.MEDIUM);

  /**
   * Reset form
   */
  const resetForm = () => {
    setName('');
    setDescription('');
    setIcon('📋');
    setTemplateTitle('');
    setTemplateDescription('');
    setPriority(TaskPriority.MEDIUM);
    setIsCreating(false);
    setEditingId(null);
  };

  /**
   * Load template for editing
   */
  const handleEdit = (template: TaskTemplate) => {
    setName(template.name);
    setDescription(template.description || '');
    setIcon(template.icon || '📋');
    setTemplateTitle(template.template_title || '');
    setTemplateDescription(template.template_description || '');
    setPriority(template.priority);
    setEditingId(template.id);
    setIsCreating(false);
  };

  /**
   * Handle submit
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) return;

    setIsSubmitting(true);

    try {
      const data = {
        name: name.trim(),
        description: description.trim() || undefined,
        icon: icon || '📋',
        template_title: templateTitle.trim() || undefined,
        template_description: templateDescription.trim() || undefined,
        priority,
      };

      if (editingId) {
        await onUpdateTemplate(editingId, data);
      } else {
        await onCreateTemplate(data);
      }

      resetForm();
    } catch (error) {
      console.error('Failed to save template:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Handle delete
   */
  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this template?')) return;

    try {
      await onDeleteTemplate(id);
    } catch (error) {
      console.error('Failed to delete template:', error);
    }
  };

  const showForm = isCreating || editingId !== null;

  return (
    <div className="template-manager">
      {/* Header */}
      <div className="template-manager-header">
        <div className="template-manager-header-content">
          <h2 className="template-manager-title">Template Manager</h2>
          <p className="template-manager-subtitle">Create and manage your task templates</p>
        </div>
        {!showForm && (
          <button
            onClick={() => setIsCreating(true)}
            className="template-manager-create-btn"
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Template
          </button>
        )}
      </div>

      {/* Template Form */}
      {showForm && (
        <div className="template-form-container">
          <h3 className="template-form-title">
            {editingId ? 'Edit Template' : 'Create Template'}
          </h3>

          <form onSubmit={handleSubmit} className="template-form">
            {/* Template Name */}
            <div className="template-form-field">
              <label className="template-form-label">
                Template Name <span className="template-form-label-required">*</span>
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., Daily Standup"
                disabled={isSubmitting}
                required
                className="template-form-input"
              />
            </div>

            {/* Template Description */}
            <div className="template-form-field">
              <label className="template-form-label">
                Template Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe what this template is for..."
                disabled={isSubmitting}
                rows={2}
                className="template-form-textarea"
              />
            </div>

            {/* Icon */}
            <div className="template-form-field">
              <label className="template-form-label">
                Icon (Emoji)
              </label>
              <input
                type="text"
                value={icon}
                onChange={(e) => setIcon(e.target.value)}
                placeholder="📋"
                disabled={isSubmitting}
                maxLength={2}
                className="template-form-input"
              />
            </div>

            {/* Task Title Template */}
            <div className="template-form-field">
              <label className="template-form-label">
                Default Task Title
              </label>
              <input
                type="text"
                value={templateTitle}
                onChange={(e) => setTemplateTitle(e.target.value)}
                placeholder="Leave empty for custom title"
                disabled={isSubmitting}
                className="template-form-input"
              />
            </div>

            {/* Task Description Template */}
            <div className="template-form-field">
              <label className="template-form-label">
                Default Task Description
              </label>
              <textarea
                value={templateDescription}
                onChange={(e) => setTemplateDescription(e.target.value)}
                placeholder="Leave empty for custom description"
                disabled={isSubmitting}
                rows={2}
                className="template-form-textarea"
              />
            </div>

            {/* Priority */}
            <div className="template-form-field">
              <label className="template-form-label">
                Default Priority
              </label>
              <div className="template-priority-grid">
                {[TaskPriority.HIGH, TaskPriority.MEDIUM, TaskPriority.LOW].map((p) => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => setPriority(p)}
                    disabled={isSubmitting}
                    className={`template-priority-btn ${priority === p ? 'active' : ''}`}
                  >
                    {p.charAt(0).toUpperCase() + p.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="template-form-actions">
              <button
                type="submit"
                disabled={isSubmitting || !name.trim()}
                className="template-form-submit"
              >
                {editingId ? 'Update Template' : 'Create Template'}
              </button>
              <button
                type="button"
                onClick={resetForm}
                disabled={isSubmitting}
                className="template-form-cancel"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Template List */}
      {!showForm && (
        <div className="template-list">
          {templates.map((template) => (
            <div key={template.id} className="template-card">
              <div className="template-card-content">
                <div className="template-card-icon">
                  {template.icon || '📋'}
                </div>
                <div className="template-card-info">
                  <h4 className="template-card-name">{template.name}</h4>
                  {template.description && (
                    <p className="template-card-description">{template.description}</p>
                  )}
                  <div className="template-card-meta">
                    <span className="template-card-priority">
                      {template.priority}
                    </span>
                    <span className="template-card-usage">
                      Used {template.use_count}x
                    </span>
                  </div>
                </div>
              </div>

              <div className="template-card-actions">
                <button
                  onClick={() => handleEdit(template)}
                  className="template-card-edit"
                >
                  Edit
                </button>
                {!template.id.startsWith('default-') && (
                  <button
                    onClick={() => handleDelete(template.id)}
                    className="template-card-delete"
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
