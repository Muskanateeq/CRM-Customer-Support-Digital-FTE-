/**
 * Team Page - TaskNest
 * Team collaboration and management
 */

'use client';

import React, { useState } from 'react';
import { useTeams } from '@/hooks/useTeams';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { TeamCreateRequest } from '@/lib/types';
import Modal from '@/components/ui/Modal';
import '../../teams.css';

export default function TeamPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const {
    teams,
    isLoading,
    error,
    createTeam,
    deleteTeam,
    inviteMember,
    clearError,
  } = useTeams();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
  const [selectedTeamId, setSelectedTeamId] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form states
  const [teamName, setTeamName] = useState('');
  const [teamDescription, setTeamDescription] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');

  /**
   * Redirect to login if not authenticated
   */
  React.useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  /**
   * Handle create team
   */
  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const data: TeamCreateRequest = {
        name: teamName,
        description: teamDescription || undefined,
      };

      await createTeam(data);
      setIsCreateModalOpen(false);
      setTeamName('');
      setTeamDescription('');
    } catch (error) {
      console.error('Failed to create team:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Handle invite member
   */
  const handleInviteMember = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTeamId) return;

    setIsSubmitting(true);

    try {
      await inviteMember(selectedTeamId, inviteEmail);
      setIsInviteModalOpen(false);
      setInviteEmail('');
      setSelectedTeamId(null);
      alert('Invitation sent successfully!');
    } catch (error) {
      console.error('Failed to invite member:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Handle delete team
   */
  const handleDeleteTeam = async (teamId: number) => {
    if (!confirm('Are you sure you want to delete this team?')) return;

    try {
      await deleteTeam(teamId);
    } catch (error) {
      console.error('Failed to delete team:', error);
    }
  };

  /**
   * Open invite modal
   */
  const openInviteModal = (teamId: number) => {
    setSelectedTeamId(teamId);
    setIsInviteModalOpen(true);
  };

  /**
   * Show loading state
   */
  if (authLoading) {
    return (
      <div className="team-loading">
        <div className="team-spinner"></div>
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
    <div className="team-container">
      {/* Header */}
      <div className="team-header">
        <div>
          <h1 className="team-page-title">Teams</h1>
          <p className="team-page-subtitle">
            Collaborate with your team members on tasks and projects
          </p>
        </div>

        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="team-btn-create"
        >
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>Create Team</span>
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="team-error">
          <p>{error}</p>
          <button onClick={clearError}>Dismiss</button>
        </div>
      )}

      {/* Teams Grid */}
      {isLoading ? (
        <div className="team-loading">
          <div className="team-spinner"></div>
        </div>
      ) : teams.length === 0 ? (
        <div className="team-empty-state">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <h3>No teams yet</h3>
          <p>Create your first team to start collaborating</p>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="team-btn-create-empty"
          >
            Create Team
          </button>
        </div>
      ) : (
        <div className="team-grid">
          {teams.map((team) => (
            <div key={team.id} className="team-card">
              <div className="team-card-header">
                <h3 className="team-card-title">{team.name}</h3>
                <div className="team-card-actions">
                  <button
                    onClick={() => openInviteModal(team.id)}
                    className="team-btn-icon"
                    title="Invite member"
                  >
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleDeleteTeam(team.id)}
                    className="team-btn-icon team-btn-delete"
                    title="Delete team"
                  >
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>

              {team.description && (
                <p className="team-card-description">{team.description}</p>
              )}

              <div className="team-card-footer">
                <span className="team-card-meta">
                  Created {new Date(team.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Team Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Team"
      >
        <form onSubmit={handleCreateTeam} className="team-form">
          <div className="team-form-group">
            <label htmlFor="teamName">Team Name *</label>
            <input
              id="teamName"
              type="text"
              value={teamName}
              onChange={(e) => setTeamName(e.target.value)}
              required
              maxLength={255}
              placeholder="Enter team name"
              className="team-input"
            />
          </div>

          <div className="team-form-group">
            <label htmlFor="teamDescription">Description</label>
            <textarea
              id="teamDescription"
              value={teamDescription}
              onChange={(e) => setTeamDescription(e.target.value)}
              maxLength={1000}
              placeholder="Enter team description (optional)"
              className="team-textarea"
              rows={4}
            />
          </div>

          <div className="team-form-actions">
            <button
              type="button"
              onClick={() => setIsCreateModalOpen(false)}
              className="team-btn-cancel"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="team-btn-submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Creating...' : 'Create Team'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Invite Member Modal */}
      <Modal
        isOpen={isInviteModalOpen}
        onClose={() => setIsInviteModalOpen(false)}
        title="Invite Team Member"
      >
        <form onSubmit={handleInviteMember} className="team-form">
          <div className="team-form-group">
            <label htmlFor="inviteEmail">Email Address *</label>
            <input
              id="inviteEmail"
              type="email"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              required
              placeholder="Enter email address"
              className="team-input"
            />
          </div>

          <div className="team-form-actions">
            <button
              type="button"
              onClick={() => setIsInviteModalOpen(false)}
              className="team-btn-cancel"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="team-btn-submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Sending...' : 'Send Invitation'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
