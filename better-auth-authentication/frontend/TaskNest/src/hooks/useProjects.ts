/**
 * useProjects Hook
 *
 * Custom hook for project management with state management
 */

import { useState, useEffect, useCallback } from 'react';
import {
  createProject as createProjectApi,
  getUserProjects,
  updateProject as updateProjectApi,
  deleteProject as deleteProjectApi,
} from '@/lib/projects-api';
import { Project, ProjectCreateRequest, ProjectUpdateRequest } from '@/lib/types';

export function useProjects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch all projects
   */
  const fetchProjects = useCallback(async (status?: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await getUserProjects(status);
      setProjects(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch projects';
      setError(errorMessage);
      console.error('Failed to fetch projects:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Create a new project
   */
  const createProject = useCallback(
    async (data: ProjectCreateRequest) => {
      setError(null);

      try {
        const newProject = await createProjectApi(data);
        setProjects((prev) => [newProject, ...prev]);
        return newProject;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to create project';
        setError(errorMessage);
        throw err;
      }
    },
    []
  );

  /**
   * Update a project
   */
  const updateProject = useCallback(
    async (projectId: number, data: ProjectUpdateRequest) => {
      setError(null);

      try {
        const updatedProject = await updateProjectApi(projectId, data);
        setProjects((prev) =>
          prev.map((project) => (project.id === projectId ? updatedProject : project))
        );
        return updatedProject;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to update project';
        setError(errorMessage);
        throw err;
      }
    },
    []
  );

  /**
   * Delete a project
   */
  const deleteProject = useCallback(async (projectId: number) => {
    setError(null);

    try {
      await deleteProjectApi(projectId);
      setProjects((prev) => prev.filter((project) => project.id !== projectId));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete project';
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

  /**
   * Fetch projects on mount
   */
  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return {
    projects,
    isLoading,
    error,
    createProject,
    updateProject,
    deleteProject,
    refreshProjects: fetchProjects,
    clearError,
  };
}
