/**
 * CommentThread Component
 *
 * Displays a thread of comments with edit/delete functionality
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useComments } from '@/hooks/useComments';
import CommentInput from './CommentInput';
import { Comment } from '@/lib/types';

interface CommentThreadProps {
  taskId: number;
}

export default function CommentThread({ taskId }: CommentThreadProps) {
  const { user } = useAuth();
  const {
    comments,
    isLoading,
    error,
    createComment,
    updateComment,
    deleteComment,
    refreshComments,
    clearError,
  } = useComments(taskId);

  const [editingCommentId, setEditingCommentId] = useState<number | null>(null);
  const [editContent, setEditContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  /**
   * Load comments on mount
   */
  useEffect(() => {
    refreshComments();
  }, [refreshComments]);

  /**
   * Handle create comment
   */
  const handleCreateComment = async (data: { content: string; mentions?: string[] }) => {
    setIsSubmitting(true);
    try {
      await createComment(data);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Start editing a comment
   */
  const startEditing = (comment: Comment) => {
    setEditingCommentId(comment.id);
    setEditContent(comment.content);
  };

  /**
   * Cancel editing
   */
  const cancelEditing = () => {
    setEditingCommentId(null);
    setEditContent('');
  };

  /**
   * Handle update comment
   */
  const handleUpdateComment = async (commentId: number) => {
    if (!editContent.trim()) return;

    setIsSubmitting(true);
    try {
      await updateComment(commentId, editContent.trim());
      setEditingCommentId(null);
      setEditContent('');
    } catch (error) {
      console.error('Failed to update comment:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Handle delete comment
   */
  const handleDeleteComment = async (commentId: number) => {
    if (!confirm('Are you sure you want to delete this comment?')) return;

    try {
      await deleteComment(commentId);
    } catch (error) {
      console.error('Failed to delete comment:', error);
    }
  };

  /**
   * Format date
   */
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (isLoading) {
    return (
      <div className="comment-thread-loading">
        <div className="comment-spinner"></div>
      </div>
    );
  }

  return (
    <div className="comment-thread">
      {/* Error Message */}
      {error && (
        <div className="comment-error">
          <p>{error}</p>
          <button onClick={clearError}>Dismiss</button>
        </div>
      )}

      {/* Comment Input */}
      <div className="comment-input-section">
        <CommentInput onSubmit={handleCreateComment} isSubmitting={isSubmitting} />
      </div>

      {/* Comments List */}
      <div className="comment-list">
        {comments.length === 0 ? (
          <div className="comment-empty">
            <p>No comments yet. Be the first to comment!</p>
          </div>
        ) : (
          comments.map((comment) => (
            <div key={comment.id} className="comment-item">
              <div className="comment-header">
                <div className="comment-author">
                  <div className="comment-avatar">
                    {comment.author_id.charAt(0).toUpperCase()}
                  </div>
                  <div className="comment-meta">
                    <span className="comment-author-name">{comment.author_id}</span>
                    <span className="comment-date">{formatDate(comment.created_at)}</span>
                  </div>
                </div>

                {/* Actions (only for comment author) */}
                {user?.id === comment.author_id && (
                  <div className="comment-actions">
                    <button
                      onClick={() => startEditing(comment)}
                      className="comment-btn-edit"
                      title="Edit comment"
                    >
                      <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      onClick={() => handleDeleteComment(comment.id)}
                      className="comment-btn-delete"
                      title="Delete comment"
                    >
                      <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                )}
              </div>

              {/* Comment Content */}
              {editingCommentId === comment.id ? (
                <div className="comment-edit-form">
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    className="comment-edit-textarea"
                    rows={3}
                  />
                  <div className="comment-edit-actions">
                    <button
                      onClick={cancelEditing}
                      className="comment-btn-cancel"
                      disabled={isSubmitting}
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleUpdateComment(comment.id)}
                      className="comment-btn-save"
                      disabled={isSubmitting || !editContent.trim()}
                    >
                      {isSubmitting ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="comment-content">
                  <p>{comment.content}</p>
                  {comment.mentions && comment.mentions.length > 0 && (
                    <div className="comment-mentions">
                      {comment.mentions.map((mention, idx) => (
                        <span key={idx} className="comment-mention">
                          @{mention}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
