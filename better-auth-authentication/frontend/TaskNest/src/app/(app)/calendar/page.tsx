/**
 * Calendar Page - TaskNest
 * Task scheduling and calendar view
 */

'use client';

import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';

export default function CalendarPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  /**
   * Redirect to login if not authenticated
   */
  React.useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  if (authLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '3rem' }}>
        <div style={{ width: '40px', height: '40px', border: '3px solid rgba(228, 155, 15, 0.2)', borderTopColor: '#E49B0F', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }}></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '2rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: '700', background: 'linear-gradient(135deg, #E49B0F, #F5B942)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', margin: '0 0 0.5rem 0' }}>
          Calendar
        </h1>
        <p style={{ fontSize: '1rem', color: '#A0A0A0', margin: '0' }}>
          View and manage your tasks in calendar format
        </p>
      </div>

      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '4rem 2rem',
        background: 'rgba(10, 10, 10, 0.5)',
        border: '1px solid rgba(228, 155, 15, 0.2)',
        borderRadius: '16px',
        textAlign: 'center'
      }}>
        <svg width="80" height="80" fill="none" stroke="#A0A0A0" viewBox="0 0 24 24" style={{ marginBottom: '1.5rem', opacity: 0.5 }}>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <h3 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#FFFFFF', margin: '0 0 0.5rem 0' }}>
          Calendar View Coming Soon
        </h3>
        <p style={{ fontSize: '1rem', color: '#A0A0A0', margin: '0' }}>
          Task calendar with drag-and-drop scheduling will be available soon
        </p>
      </div>
    </div>
  );
}
