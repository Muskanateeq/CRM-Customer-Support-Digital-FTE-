/**
 * How It Works Section Component
 * Shows 3 simple steps to get started
 */

'use client';

import React from 'react';

const steps = [
  {
    number: '1',
    title: 'Create Your Workspace',
    description: 'Sign up and set up your workspace in seconds. Invite your team members to collaborate.',
  },
  {
    number: '2',
    title: 'Add Your Tasks',
    description: 'Create tasks, set priorities, assign team members, and organize everything in one place.',
  },
  {
    number: '3',
    title: 'Track Progress',
    description: 'Monitor progress, get insights, and achieve your goals faster with real-time updates.',
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="how-it-works">
      <div className="section-header">
        <span className="section-badge">How It Works</span>
        <h2>Get Started in 3 Simple Steps</h2>
        <p>Start managing your tasks efficiently in minutes.</p>
      </div>

      <div className="steps-container">
        {steps.map((step, index) => (
          <div key={index} className="step">
            <div className="step-number">{step.number}</div>
            <h3>{step.title}</h3>
            <p>{step.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
