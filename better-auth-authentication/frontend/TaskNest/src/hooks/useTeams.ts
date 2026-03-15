/**
 * useTeams Hook
 *
 * Custom hook for team management with state management
 */

import { useState, useEffect, useCallback } from 'react';
import {
  createTeam as createTeamApi,
  getUserTeams,
  updateTeam as updateTeamApi,
  deleteTeam as deleteTeamApi,
  getTeamMembers as getTeamMembersApi,
  inviteMember as inviteMemberApi,
} from '@/lib/teams-api';
import { Team, TeamCreateRequest, TeamUpdateRequest } from '@/lib/types';

export function useTeams() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch all teams
   */
  const fetchTeams = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await getUserTeams();
      setTeams(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch teams';
      setError(errorMessage);
      console.error('Failed to fetch teams:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Create a new team
   */
  const createTeam = useCallback(
    async (data: TeamCreateRequest) => {
      setError(null);

      try {
        const newTeam = await createTeamApi(data);
        setTeams((prev) => [...prev, newTeam]);
        return newTeam;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to create team';
        setError(errorMessage);
        throw err;
      }
    },
    []
  );

  /**
   * Update a team
   */
  const updateTeam = useCallback(
    async (teamId: number, data: TeamUpdateRequest) => {
      setError(null);

      try {
        const updatedTeam = await updateTeamApi(teamId, data);
        setTeams((prev) =>
          prev.map((team) => (team.id === teamId ? updatedTeam : team))
        );
        return updatedTeam;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to update team';
        setError(errorMessage);
        throw err;
      }
    },
    []
  );

  /**
   * Delete a team
   */
  const deleteTeam = useCallback(async (teamId: number) => {
    setError(null);

    try {
      await deleteTeamApi(teamId);
      setTeams((prev) => prev.filter((team) => team.id !== teamId));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete team';
      setError(errorMessage);
      throw err;
    }
  }, []);

  /**
   * Get team members
   */
  const getMembers = useCallback(async (teamId: number) => {
    setError(null);

    try {
      const members = await getTeamMembersApi(teamId);
      return members;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch members';
      setError(errorMessage);
      throw err;
    }
  }, []);

  /**
   * Invite member to team
   */
  const inviteMember = useCallback(async (teamId: number, email: string) => {
    setError(null);

    try {
      const invitation = await inviteMemberApi(teamId, email);
      return invitation;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to invite member';
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
   * Fetch teams on mount
   */
  useEffect(() => {
    fetchTeams();
  }, [fetchTeams]);

  return {
    teams,
    isLoading,
    error,
    createTeam,
    updateTeam,
    deleteTeam,
    getMembers,
    inviteMember,
    refreshTeams: fetchTeams,
    clearError,
  };
}
