/**
 * Projects Page - TaskNest
 * Project management and organization
 */

'use client';

import React, { useState } from 'react';
import { useProjects } from '@/hooks/useProjects';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { ProjectCreateRequest, ProjectUpdateRequest } from '@/lib/types';
import Modal from '@/components/ui/Modal';
import '../../projects.css';

export default function ProjectsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const {
    projects,
    isLoading,
    error,
    createProject,
    updateProject,
    deleteProject,
    clearError,
  } = useProjects();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form states
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [projectStatus, setProjectStatus] = useState('active');

  /**
   * Redirect to login if not authenticated
   */
  React.useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  /**
   * Handle create project
   */
  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const data: ProjectCreateRequest = {
        name: projectName,
        description: projectDescription || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      };

      await createProject(data);
      setIsCreateModalOpen(false);
      resetForm();
    } catch (error) {
      console.error('Failed to create project:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Open edit modal
   */
  const openEditModal = (projectId: number) => {
    const project = projects.find((p) => p.id === projectId);
    if (!project) return;

    setSelectedProjectId(projectId);
    setProjectName(project.name);
    setProjectDescription(project.description || '');
    setStartDate(project.start_date || '');
    setEndDate(project.end_date || '');
    setProjectStatus(project.status);
    setIsEditModalOpen(true);
  };

  /**
   * Handle update project
   */
  const handleUpdateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProjectId) return;

    setIsSubmitting(true);

    try {
      const data: ProjectUpdateRequest = {
        name: projectName,
        description: projectDescription || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        status: projectStatus as "completed" | "active" | "archived" | undefined,
      };

      await updateProject(selectedProjectId, data);
      setIsEditModalOpen(false);
      resetForm();
    } catch (error) {
      console.error('Failed to update project:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Handle delete project
   */
  const handleDeleteProject = async (projectId: number) => {
    if (!confirm('Are you sure you want to delete this project?')) return;

    try {
      await deleteProject(projectId);
    } catch (error) {
      console.error('Failed to delete project:', error);
    }
  };

  /**
   * Reset form
   */
  const resetForm = () => {
    setProjectName('');
    setProjectDescription('');
    setStartDate('');
    setEndDate('');
    setProjectStatus('active');
    setSelectedProjectId(null);
  };

  /**
   * Format date
   */
  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString();
  };

  /**
   * Get status badge class
   */
  const getStatusClass = (status: string) => {
    switch (status) {
      case 'active':
        return 'project-status-active';
      case 'completed':
        return 'project-status-completed';
      case 'archived':
        return 'project-status-archived';
      default:
        return '';
    }
  };

  /**
   * Show loading state
   */
  if (authLoading) {
    return (
      <div className="project-loading">
        <div className="project-spinner"></div>
      </div>
    );
  }

  /**
   * Don't render if not authenticated
   */
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="project-container">
      {/* Header */}
      <div className="project-header">
        <div>
          <h1 className="project-page-title">Projects</h1>
          <p className="project-page-subtitle">
            Organize your tasks into projects and track progress
          </p>
        </div>

        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="project-btn-create"
        >
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>Create Project</span>
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="project-error">
          <p>{error}</p>
          <button onClick={clearError}>Dismiss</button>
        </div>
      )}

      {/* Projects Grid */}
      {isLoading ? (
        <div className="project-loading">
          <div className="project-spinner"></div>
        </div>
      ) : projects.length === 0 ? (
        <div className="project-empty-state">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3>No projects yet</h3>
          <p>Create your first project to organize your tasks</p>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="project-btn-create-empty"
          >
            Create Project
          </button>
        </div>
      ) : (
        <div className="project-grid">
          {projects.map((project) => (
            <div key={project.id} className="project-card">
              <div className="project-card-header">
                <div>
                  <h3 className="project-card-title">{project.name}</h3>
                  <span className={`project-status-badge ${getStatusClass(project.status)}`}>
                    {project.status}
                  </span>
                </div>
                <div className="project-card-actions">
                  <button
                    onClick={() => openEditModal(project.id)}
                    className="project-btn-icon"
                    title="Edit project"
                  >
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleDeleteProject(project.id)}
                    className="project-btn-icon project-btn-delete"
                    title="Delete project"
                  >
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>

              {project.description && (
                <p className="project-card-description">{project.description}</p>
              )}

              <div className="project-card-dates">
                {project.start_date && (
                  <div className="project-date">
                    <span className="project-date-label">Start:</span>
                    <span>{formatDate(project.start_date)}</span>
                  </div>
                )}
                {project.end_date && (
                  <div className="project-date">
                    <span className="project-date-label">End:</span>
                    <span>{formatDate(project.end_date)}</span>
                  </div>
                )}
              </div>

              <div className="project-card-footer">
                <span className="project-card-meta">
                  Created {formatDate(project.created_at)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Project Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          resetForm();
        }}
        title="Create New Project"
      >
        <form onSubmit={handleCreateProject} className="project-form">
          <div className="project-form-group">
            <label htmlFor="projectName">Project Name *</label>
            <input
              id="projectName"
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              required
              maxLength={255}
              placeholder="Enter project name"
              className="project-input"
            />
          </div>

          <div className="project-form-group">
            <label htmlFor="projectDescription">Description</label>
            <textarea
              id="projectDescription"
              value={projectDescription}
              onChange={(e) => setProjectDescription(e.target.value)}
              maxLength={2000}
              placeholder="Enter project description (optional)"
              className="project-textarea"
              rows={4}
            />
          </div>

          <div className="project-form-row">
            <div className="project-form-group">
              <label htmlFor="startDate">Start Date</label>
              <input
                id="startDate"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="project-input"
              />
            </div>

            <div className="project-form-group">
              <label htmlFor="endDate">End Date</label>
              <input
                id="endDate"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="project-input"
              />
            </div>
          </div>

          <div className="project-form-actions">
            <button
              type="button"
              onClick={() => {
                setIsCreateModalOpen(false);
                resetForm();
              }}
              className="project-btn-cancel"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="project-btn-submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit Project Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          resetForm();
        }}
        title="Edit Project"
      >
        <form onSubmit={handleUpdateProject} className="project-form">
          <div className="project-form-group">
            <label htmlFor="editProjectName">Project Name *</label>
            <input
              id="editProjectName"
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              required
              maxLength={255}
              placeholder="Enter project name"
              className="project-input"
            />
          </div>

          <div className="project-form-group">
            <label htmlFor="editProjectDescription">Description</label>
            <textarea
              id="editProjectDescription"
              value={projectDescription}
              onChange={(e) => setProjectDescription(e.target.value)}
              maxLength={2000}
              placeholder="Enter project description (optional)"
              className="project-textarea"
              rows={4}
            />
          </div>

          <div className="project-form-row">
            <div className="project-form-group">
              <label htmlFor="editStartDate">Start Date</label>
              <input
                id="editStartDate"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="project-input"
              />
            </div>

            <div className="project-form-group">
              <label htmlFor="editEndDate">End Date</label>
              <input
                id="editEndDate"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="project-input"
              />
            </div>
          </div>

          <div className="project-form-group">
            <label htmlFor="projectStatus">Status</label>
            <select
              id="projectStatus"
              value={projectStatus}
              onChange={(e) => setProjectStatus(e.target.value)}
              className="project-select"
            >
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="archived">Archived</option>
            </select>
          </div>

          <div className="project-form-actions">
            <button
              type="button"
              onClick={() => {
                setIsEditModalOpen(false);
                resetForm();
              }}
              className="project-btn-cancel"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="project-btn-submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
