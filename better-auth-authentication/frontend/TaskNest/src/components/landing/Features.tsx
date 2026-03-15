/**
 * Features Section Component
 * Displays 6 key features with icons
 */

'use client';

import React, { useState } from 'react';
import { Target, Users, Bot, BarChart3, Bell, Lock } from 'lucide-react';

const features = [
  {
    icon: Target,
    title: 'Smart Task Management',
    description: 'Create, organize, and prioritize tasks with our intuitive interface. Set deadlines, add tags, and track progress effortlessly.',
    featured: false,
  },
  {
    icon: Bot,
    title: 'AI-Powered Insights',
    description: 'Get intelligent suggestions for task prioritization, time estimates, and productivity improvements.',
    featured: true,
  },
  {
    icon: Users,
    title: 'Team Collaboration',
    description: 'Work together seamlessly with real-time updates, comments, and file sharing. Keep everyone on the same page.',
    featured: false,
  },
  {
    icon: BarChart3,
    title: 'Advanced Analytics',
    description: 'Track team performance, identify bottlenecks, and make data-driven decisions with comprehensive reports.',
    featured: false,
  },
  {
    icon: Bell,
    title: 'Smart Notifications',
    description: 'Stay updated with customizable notifications. Never miss a deadline or important update.',
    featured: false,
  },
  {
    icon: Lock,
    title: 'Enterprise Security',
    description: 'Bank-level encryption, SSO, and compliance with industry standards to keep your data safe.',
    featured: false,
  },
];

export default function Features() {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  return (
    <section id="features" className="features">
      <div className="section-header">
        <span className="section-badge">Features</span>
        <h2>Everything You Need to Stay Organized</h2>
        <p>Powerful features designed to help you manage tasks efficiently and collaborate with your team.</p>
      </div>

      <div className="features-grid">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          const isFeatured = feature.featured && hoveredIndex === null;
          const isHovered = hoveredIndex === index;

          return (
            <div
              key={index}
              className={`feature-card ${isFeatured || isHovered ? 'featured' : ''}`}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              <div className="feature-icon">
                <Icon style={{ width: '1.5rem', height: '1.5rem' }} />
              </div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
