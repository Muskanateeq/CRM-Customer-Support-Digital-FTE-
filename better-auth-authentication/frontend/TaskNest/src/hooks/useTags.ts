/**
 * useTags Hook
 *
 * Custom hook for managing tags with CRUD operations.
 * Handles tag fetching, creation, updating, and deletion.
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { Tag } from '@/lib/types';
import { api } from '@/lib/api';

interface UseTagsReturn {
  tags: Tag[];
  isLoading: boolean;
  error: string | null;
  fetchTags: () => Promise<void>;
  createTag: (name: string) => Promise<Tag>;
  updateTag: (id: number, name: string) => Promise<void>;
  deleteTag: (id: number) => Promise<void>;
  clearError: () => void;
}

export function useTags(): UseTagsReturn {
  const [tags, setTags] = useState<Tag[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch all tags for the current user
   */
  const fetchTags = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await api.get<Tag[]>('/tags');
      setTags(response);
    } catch (err: unknown) {
      const error = err as Error;
      setError(error.message || 'Failed to fetch tags');
      console.error('Failed to fetch tags:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Create a new tag
   */
  const createTag = useCallback(async (name: string): Promise<Tag> => {
    try {
      setError(null);
      const newTag = await api.post<Tag>('/tags', { name });
      setTags((prev) => [...prev, newTag]);
      return newTag;
    } catch (err: unknown) {
      const error = err as Error;
      setError(error.message || 'Failed to create tag');
      console.error('Failed to create tag:', err);
      throw err;
    }
  }, []);

  /**
   * Update a tag
   */
  const updateTag = useCallback(async (id: number, name: string) => {
    try {
      setError(null);
      const updatedTag = await api.put<Tag>(`/tags/${id}`, { name });
      setTags((prev) =>
        prev.map((tag) => (tag.id === id ? updatedTag : tag))
      );
    } catch (err: unknown) {
      const error = err as Error;
      setError(error.message || 'Failed to update tag');
      console.error('Failed to update tag:', err);
      throw err;
    }
  }, []);

  /**
   * Delete a tag
   */
  const deleteTag = useCallback(async (id: number) => {
    try {
      setError(null);
      await api.delete(`/tags/${id}`);
      setTags((prev) => prev.filter((tag) => tag.id !== id));
    } catch (err: unknown) {
      const error = err as Error;
      setError(error.message || 'Failed to delete tag');
      console.error('Failed to delete tag:', err);
      throw err;
    }
  }, []);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Fetch tags on mount
   */
  useEffect(() => {
    fetchTags();
  }, [fetchTags]);

  return {
    tags,
    isLoading,
    error,
    fetchTags,
    createTag,
    updateTag,
    deleteTag,
    clearError,
  };
}
