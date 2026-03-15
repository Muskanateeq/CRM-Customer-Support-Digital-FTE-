/**
 * Hero Section Component
 * Main landing page hero with CTA buttons
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { Rocket } from 'lucide-react';

export default function Hero() {
  return (
    <section className="hero">
      <div className="grid-bg"></div>
      <div className="hero-container">
        <div className="hero-content">
          <span className="hero-badge">
            <Rocket className="w-4 h-4" style={{ display: 'inline', marginRight: '0.5rem' }} />
            New: AI-Powered Task Management
          </span>
          <h1>Organize Your Work, Amplify Your Productivity</h1>
          <p>TaskNest helps teams collaborate seamlessly with intelligent task management, real-time updates, and powerful automation.</p>
          <div className="hero-cta">
            <Link href="/signup" className="btn btn-primary">Start Free Trial</Link>
            <Link href="/login" className="btn btn-outline">Watch Demo</Link>
          </div>
        </div>
      </div>
    </section>
  );
}
