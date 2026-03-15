/**
 * TemplateSelector Component - Choose Task Template
 * Dark Golden Theme - Modern SaaS Design
 */

'use client';

import React from 'react';
import { TaskTemplate } from '@/lib/types';
import './TemplateSelector.css';

export interface TemplateSelectorProps {
  templates: TaskTemplate[];
  onSelect: (template: TaskTemplate) => void;
  selectedId?: string;
}

export default function TemplateSelector({
  templates,
  onSelect,
  selectedId,
}: TemplateSelectorProps) {
  /**
   * Get recurrence label
   */
  const getRecurrenceLabel = (template: TaskTemplate): string | null => {
    if (!template.recurrence_pattern) return null;

    const { type, interval } = template.recurrence_pattern;

    switch (type) {
      case 'daily':
        return `Every ${interval > 1 ? `${interval} days` : 'day'}`;
      case 'weekly':
        return `Every ${interval > 1 ? `${interval} weeks` : 'week'}`;
      case 'monthly':
        return `Every ${interval > 1 ? `${interval} months` : 'month'}`;
      case 'custom':
        return `Every ${interval} days`;
      default:
        return null;
    }
  };

  if (templates.length === 0) {
    return (
      <div className="template-empty">
        <div className="template-empty-icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p className="template-empty-title">No templates available</p>
        <p className="template-empty-text">Create your first template to get started</p>
      </div>
    );
  }

  return (
    <div className="template-selector">
      <div className="template-selector-header">
        <h3 className="template-selector-title">Choose a Template</h3>
        <span className="template-selector-count">{templates.length} templates</span>
      </div>

      <div className="template-selector-grid">
        {templates.map((template) => {
          const isSelected = selectedId === template.id;
          const recurrenceLabel = getRecurrenceLabel(template);

          return (
            <button
              key={template.id}
              onClick={() => onSelect(template)}
              className={`template-card ${isSelected ? 'selected' : ''}`}
            >
              {/* Selected Indicator */}
              {isSelected && (
                <div className="template-selected-indicator">
                  <svg fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              )}

              {/* Template Header */}
              <div className="template-card-header">
                <div className="template-icon">
                  {template.icon || '📋'}
                </div>

                <div className="template-info">
                  <h4 className="template-name">{template.name}</h4>
                  {template.description && (
                    <p className="template-description">{template.description}</p>
                  )}
                </div>
              </div>

              {/* Template Meta */}
              <div className="template-meta">
                <span className={`template-badge priority-${template.priority}`}>
                  {template.priority.charAt(0).toUpperCase() + template.priority.slice(1)}
                </span>

                {recurrenceLabel && (
                  <span className="template-badge recurrence">
                    🔄 {recurrenceLabel}
                  </span>
                )}

                <span className="template-badge usage">
                  Used {template.use_count} {template.use_count === 1 ? 'time' : 'times'}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
