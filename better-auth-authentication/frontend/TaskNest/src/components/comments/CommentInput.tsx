/**
 * CommentInput Component
 *
 * Input field for creating comments with @mention autocomplete
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { CommentCreateRequest } from '@/lib/types';

interface CommentInputProps {
  onSubmit: (data: CommentCreateRequest) => Promise<void>;
  isSubmitting?: boolean;
  placeholder?: string;
}

export default function CommentInput({
  onSubmit,
  isSubmitting = false,
  placeholder = 'Write a comment...',
}: CommentInputProps) {
  const [content, setContent] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /**
   * Auto-resize textarea
   */
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [content]);

  /**
   * Extract mentions from content
   */
  const extractMentions = (text: string): string[] => {
    const mentionRegex = /@(\w+)/g;
    const matches = text.match(mentionRegex);
    if (!matches) return [];

    return matches.map(match => match.substring(1)); // Remove @ symbol
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!content.trim() || isSubmitting) return;

    const extractedMentions = extractMentions(content);

    try {
      await onSubmit({
        content: content.trim(),
        mentions: extractedMentions.length > 0 ? extractedMentions : undefined,
      });

      // Clear form
      setContent('');
    } catch (error) {
      console.error('Failed to submit comment:', error);
    }
  };

  /**
   * Handle keyboard shortcuts
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Ctrl+Enter or Cmd+Enter
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="comment-input-form">
      <div className="comment-input-wrapper">
        <textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="comment-input-textarea"
          disabled={isSubmitting}
          rows={1}
        />
      </div>

      <div className="comment-input-actions">
        <div className="comment-input-hint">
          <span>Use @username to mention someone</span>
          <span className="comment-input-shortcut">Ctrl+Enter to submit</span>
        </div>
        <button
          type="submit"
          className="comment-input-submit"
          disabled={!content.trim() || isSubmitting}
        >
          {isSubmitting ? 'Posting...' : 'Post Comment'}
        </button>
      </div>
    </form>
  );
}
