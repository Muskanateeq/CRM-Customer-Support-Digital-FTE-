/**
 * TagSelector Component
 * Dark Golden Theme - Modern SaaS Design
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useTags } from '@/hooks/useTags';
import TagBadge from './TagBadge';
import './TagSelector.css';

export interface TagSelectorProps {
  selectedTagIds: number[];
  onChange: (tagIds: number[]) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function TagSelector({
  selectedTagIds,
  onChange,
  disabled = false,
  placeholder = 'Add tags...',
}: TagSelectorProps) {
  const { tags, createTag, isLoading } = useTags();
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const selectedTags = tags.filter((tag) => selectedTagIds.includes(tag.id));
  const filteredTags = tags.filter((tag) =>
    tag.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
  const exactMatch = tags.find(
    (tag) => tag.name.toLowerCase() === searchQuery.toLowerCase()
  );

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setSearchQuery('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleTag = (tagId: number) => {
    if (selectedTagIds.includes(tagId)) {
      onChange(selectedTagIds.filter((id) => id !== tagId));
    } else {
      onChange([...selectedTagIds, tagId]);
    }
  };

  const removeTag = (tagId: number) => {
    onChange(selectedTagIds.filter((id) => id !== tagId));
  };

  const handleCreateTag = async () => {
    if (!searchQuery.trim() || exactMatch || isCreating) return;

    try {
      setIsCreating(true);
      const newTag = await createTag(searchQuery.trim());
      onChange([...selectedTagIds, newTag.id]);
      setSearchQuery('');
      inputRef.current?.focus();
    } catch (error) {
      console.error('Failed to create tag:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && searchQuery.trim() && !exactMatch) {
      e.preventDefault();
      handleCreateTag();
    } else if (e.key === 'Escape') {
      setIsOpen(false);
      setSearchQuery('');
    }
  };

  return (
    <div ref={dropdownRef} className="tag-selector">
      {selectedTags.length > 0 && (
        <div className="tag-selector-selected">
          {selectedTags.map((tag) => (
            <TagBadge
              key={tag.id}
              name={tag.name}
              variant="primary"
              size="md"
              onRemove={() => removeTag(tag.id)}
            />
          ))}
        </div>
      )}

      <div className="tag-selector-input-wrapper">
        <input
          ref={inputRef}
          type="text"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          disabled={disabled || isLoading}
          placeholder={placeholder}
          className="tag-selector-input"
        />

        <div className={`tag-selector-icon ${isOpen ? 'open' : ''}`}>
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {isOpen && !disabled && (
        <div className="tag-selector-dropdown">
          {isLoading && (
            <div className="tag-selector-loading">Loading tags...</div>
          )}

          {!isLoading && searchQuery.trim() && !exactMatch && (
            <button
              type="button"
              onClick={handleCreateTag}
              disabled={isCreating}
              className="tag-selector-create-btn"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span className="tag-selector-create-text">
                Create tag <span className="tag-selector-create-highlight">&quot;{searchQuery}&quot;</span>
              </span>
            </button>
          )}

          {!isLoading && filteredTags.length === 0 && !searchQuery.trim() && (
            <div className="tag-selector-empty">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              <p>No tags yet. Start typing to create one!</p>
            </div>
          )}

          {!isLoading && filteredTags.length === 0 && searchQuery.trim() && exactMatch && (
            <div className="tag-selector-empty">
              <p>Tag already exists</p>
            </div>
          )}

          {!isLoading && filteredTags.map((tag) => (
            <button
              key={tag.id}
              type="button"
              onClick={() => toggleTag(tag.id)}
              className={`tag-selector-option ${selectedTagIds.includes(tag.id) ? 'selected' : ''}`}
            >
              <span className="tag-selector-option-name">{tag.name}</span>
              <div className="tag-selector-option-check">
                {selectedTagIds.includes(tag.id) && (
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
