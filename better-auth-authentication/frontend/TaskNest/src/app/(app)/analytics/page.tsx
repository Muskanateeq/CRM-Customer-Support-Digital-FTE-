/**
 * Analytics Page - TaskNest
 * Advanced analytics with Plotly charts
 * Dark Golden Theme - Modern SaaS Design
 */

'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useTasks } from '@/hooks/useTasks';
import dynamic from 'next/dynamic';
import './analytics.css';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

/**
 * Time Range Type
 */
type TimeRange = '7days' | '30days' | '90days' | 'all';

export default function AnalyticsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { tasks, isLoading } = useTasks();
  const [timeRange, setTimeRange] = useState<TimeRange>('30days');

  /**
   * Redirect if not authenticated
   */
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  /**
   * Filter tasks by time range
   */
  const filteredTasks = useMemo(() => {
    if (timeRange === 'all') return tasks;

    const now = new Date();
    const daysMap = { '7days': 7, '30days': 30, '90days': 90 };
    const days = daysMap[timeRange];
    const cutoff = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);

    return tasks.filter(task => new Date(task.created_at) >= cutoff);
  }, [tasks, timeRange]);

  /**
   * Calculate statistics
   */
  const stats = useMemo(() => {
    const total = filteredTasks.length;
    const completed = filteredTasks.filter(t => t.completed).length;
    const pending = total - completed;
    const overdue = filteredTasks.filter(t =>
      !t.completed && t.due_date && new Date(t.due_date) < new Date()
    ).length;

    const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;

    // Most used tag
    const tagCounts: Record<string, number> = {};
    filteredTasks.forEach(task => {
      task.tags?.forEach(tag => {
        tagCounts[tag.name] = (tagCounts[tag.name] || 0) + 1;
      });
    });
    const mostUsedTag = Object.entries(tagCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'None';

    // Most productive day
    const dayCounts: Record<string, number> = {};
    filteredTasks.filter(t => t.completed).forEach(task => {
      const day = new Date(task.updated_at).toLocaleDateString('en-US', { weekday: 'long' });
      dayCounts[day] = (dayCounts[day] || 0) + 1;
    });
    const mostProductiveDay = Object.entries(dayCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A';

    return {
      total,
      completed,
      pending,
      overdue,
      completionRate,
      mostUsedTag,
      mostProductiveDay,
    };
  }, [filteredTasks]);

  /**
   * Tasks by Status (Pie Chart)
   */
  const statusChartData = useMemo(() => {
    return [{
      values: [stats.completed, stats.pending, stats.overdue],
      labels: ['Completed', 'Pending', 'Overdue'],
      type: 'pie' as const,
      marker: {
        colors: ['#10B981', '#E49B0F', '#EF4444'],
      },
      textinfo: 'label+percent',
      textfont: { color: '#FFFFFF', size: 14 },
      hoverinfo: 'label+value+percent',
    }];
  }, [stats]);

  /**
   * Tasks by Priority (Bar Chart)
   */
  const priorityChartData = useMemo(() => {
    const high = filteredTasks.filter(t => t.priority === 'high').length;
    const medium = filteredTasks.filter(t => t.priority === 'medium').length;
    const low = filteredTasks.filter(t => t.priority === 'low').length;

    return [{
      x: ['High', 'Medium', 'Low'],
      y: [high, medium, low],
      type: 'bar' as const,
      marker: {
        color: ['#EF4444', '#F59E0B', '#10B981'],
      },
      text: [high, medium, low],
      textposition: 'outside' as const,
      textfont: { color: '#FFFFFF' },
    }];
  }, [filteredTasks]);

  /**
   * Tasks by Tags (Bar Chart)
   */
  const tagsChartData = useMemo(() => {
    const tagCounts: Record<string, number> = {};
    filteredTasks.forEach(task => {
      task.tags?.forEach(tag => {
        tagCounts[tag.name] = (tagCounts[tag.name] || 0) + 1;
      });
    });

    const sortedTags = Object.entries(tagCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);

    return [{
      x: sortedTags.map(t => t[0]),
      y: sortedTags.map(t => t[1]),
      type: 'bar' as const,
      marker: {
        color: '#E49B0F',
      },
      text: sortedTags.map(t => t[1]),
      textposition: 'outside' as const,
      textfont: { color: '#FFFFFF' },
    }];
  }, [filteredTasks]);

  /**
   * Completion Trend (Line Chart)
   */
  const trendChartData = useMemo(() => {
    const days = timeRange === '7days' ? 7 : timeRange === '30days' ? 30 : 90;
    const dates: string[] = [];
    const counts: number[] = [];

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));

      const count = filteredTasks.filter(task => {
        if (!task.completed) return false;
        const taskDate = new Date(task.updated_at).toISOString().split('T')[0];
        return taskDate === dateStr;
      }).length;

      counts.push(count);
    }

    return [{
      x: dates,
      y: counts,
      type: 'scatter' as const,
      mode: 'lines+markers' as const,
      line: { color: '#E49B0F', width: 3 },
      marker: { color: '#E49B0F', size: 8 },
      fill: 'tozeroy' as const,
      fillcolor: 'rgba(228, 155, 15, 0.1)',
    }];
  }, [filteredTasks, timeRange]);

  /**
   * Common chart layout
   */
  const chartLayout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: '#FFFFFF', family: 'Inter, sans-serif' },
    margin: { t: 40, r: 20, b: 60, l: 60 },
    xaxis: { gridcolor: 'rgba(255,255,255,0.1)' },
    yaxis: { gridcolor: 'rgba(255,255,255,0.1)' },
  };

  if (authLoading || !isAuthenticated) {
    return null;
  }

  return (
    <div className="analytics-page">
      {/* Header */}
      <div className="analytics-header">
        <div>
          <h1 className="analytics-title">Analytics Dashboard</h1>
          <p className="analytics-subtitle">Insights into your productivity and task management</p>
        </div>

        {/* Time Range Filter */}
        <div className="time-range-filter">
          {(['7days', '30days', '90days', 'all'] as TimeRange[]).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`time-btn ${timeRange === range ? 'active' : ''}`}
            >
              {range === '7days' && 'Last 7 Days'}
              {range === '30days' && 'Last 30 Days'}
              {range === '90days' && 'Last 90 Days'}
              {range === 'all' && 'All Time'}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon total">📊</div>
          <div className="stat-content">
            <p className="stat-label">Total Tasks</p>
            <h3 className="stat-value">{stats.total}</h3>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon completion">✅</div>
          <div className="stat-content">
            <p className="stat-label">Completion Rate</p>
            <h3 className="stat-value">{stats.completionRate}%</h3>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon tag">🏷️</div>
          <div className="stat-content">
            <p className="stat-label">Most Used Tag</p>
            <h3 className="stat-value">{stats.mostUsedTag}</h3>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon day">📅</div>
          <div className="stat-content">
            <p className="stat-label">Most Productive Day</p>
            <h3 className="stat-value">{stats.mostProductiveDay}</h3>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      {isLoading ? (
        <div className="loading-state">
          <div className="spinner"></div>
        </div>
      ) : (
        <div className="charts-grid">
          {/* Status Pie Chart */}
          <div className="chart-card">
            <h3 className="chart-title">Tasks by Status</h3>
            <Plot
              data={statusChartData}
              layout={{ ...chartLayout, height: 350 }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%' }}
            />
          </div>

          {/* Priority Bar Chart */}
          <div className="chart-card">
            <h3 className="chart-title">Tasks by Priority</h3>
            <Plot
              data={priorityChartData}
              layout={{ ...chartLayout, height: 350 }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%' }}
            />
          </div>

          {/* Completion Trend Line Chart */}
          <div className="chart-card full-width">
            <h3 className="chart-title">Completion Trend</h3>
            <Plot
              data={trendChartData}
              layout={{ ...chartLayout, height: 350 }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%' }}
            />
          </div>

          {/* Tags Bar Chart */}
          <div className="chart-card full-width">
            <h3 className="chart-title">Top 10 Tags</h3>
            <Plot
              data={tagsChartData}
              layout={{ ...chartLayout, height: 350 }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%' }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
