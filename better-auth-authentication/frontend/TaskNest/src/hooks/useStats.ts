/**
 * useStats Hook
 * Fetches and manages task statistics
 */

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

export interface TaskStatistics {
  total_tasks: number;
  completed_tasks: number;
  in_progress_tasks: number;
  overdue_tasks: number;
  completion_rate: number;
  priority_distribution: {
    high?: number;
    medium?: number;
    low?: number;
  };
  tasks_by_status: {
    completed: number;
    in_progress: number;
    overdue: number;
  };
  weekly_stats: {
    tasks_created: number;
    tasks_completed: number;
  };
  trend: {
    direction: 'up' | 'down' | 'neutral';
    percentage: number;
  };
}

export function useStats() {
  const [stats, setStats] = useState<TaskStatistics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await api.get('/tasks/stats/summary') as { data: TaskStatistics };
      setStats(response.data);
    } catch (err) {
      console.error('Failed to fetch statistics:', err);
      setError('Failed to load statistics');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return {
    stats,
    isLoading,
    error,
    refetch: fetchStats,
  };
}
