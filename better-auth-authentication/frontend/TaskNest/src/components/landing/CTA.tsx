/**
 * Call to Action Section Component
 * Final CTA to encourage sign-ups
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowRight, Sparkles } from 'lucide-react';

export default function CTA() {
  return (
    <section className="cta-section">
      <div className="cta-container">
        <div className="cta-content">
          <div className="cta-badge">
            <Sparkles style={{ width: '1rem', height: '1rem', display: 'inline', marginRight: '0.5rem' }} />
            Start Your Journey Today
          </div>
          <h2 className="cta-title">Ready to Transform Your Productivity?</h2>
          <p className="cta-description">
            Join thousands of teams already using TaskNest to streamline their workflow and achieve more together.
          </p>
          <div className="cta-buttons">
            <Link href="/signup" className="btn btn-primary btn-large">
              Start Free Trial
              <ArrowRight style={{ width: '1.25rem', height: '1.25rem', marginLeft: '0.5rem', display: 'inline' }} />
            </Link>
            <Link href="/login" className="btn btn-outline btn-large">
              Sign In
            </Link>
          </div>
          <p className="cta-note">No credit card required • 14-day free trial • Cancel anytime</p>
        </div>
      </div>
    </section>
  );
}
