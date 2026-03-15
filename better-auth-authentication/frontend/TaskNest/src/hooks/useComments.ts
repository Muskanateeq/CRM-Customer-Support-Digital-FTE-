/**
 * useComments Hook
 *
 * Custom hook for comment management with state management
 */

import { useState, useCallback } from 'react';
import {
  createComment as createCommentApi,
  getTaskComments,
  updateComment as updateCommentApi,
  deleteComment as deleteCommentApi,
} from '@/lib/comments-api';
import { Comment, CommentCreateRequest } from '@/lib/types';

export function useComments(taskId: number) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch comments for a task
   */
  const fetchComments = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await getTaskComments(taskId);
      setComments(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch comments';
      setError(errorMessage);
      console.error('Failed to fetch comments:', err);
    } finally {
      setIsLoading(false);
    }
  }, [taskId]);

  /**
   * Create a new comment
   */
  const createComment = useCallback(
    async (data: CommentCreateRequest) => {
      setError(null);

      try {
        const newComment = await createCommentApi(taskId, data);
        setComments((prev) => [...prev, newComment]);
        return newComment;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to create comment';
        setError(errorMessage);
        throw err;
      }
    },
    [taskId]
  );

  /**
   * Update a comment
   */
  const updateComment = useCallback(
    async (commentId: number, content: string) => {
      setError(null);

      try {
        const updatedComment = await updateCommentApi(commentId, content);
        setComments((prev) =>
          prev.map((comment) => (comment.id === commentId ? updatedComment : comment))
        );
        return updatedComment;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to update comment';
        setError(errorMessage);
        throw err;
      }
    },
    []
  );

  /**
   * Delete a comment
   */
  const deleteComment = useCallback(async (commentId: number) => {
    setError(null);

    try {
      await deleteCommentApi(commentId);
      setComments((prev) => prev.filter((comment) => comment.id !== commentId));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete comment';
      setError(errorMessage);
      throw err;
    }
  }, []);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    comments,
    isLoading,
    error,
    createComment,
    updateComment,
    deleteComment,
    refreshComments: fetchComments,
    clearError,
  };
}
