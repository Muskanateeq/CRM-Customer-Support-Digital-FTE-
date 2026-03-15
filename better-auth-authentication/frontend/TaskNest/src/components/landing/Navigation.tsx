/**
 * Navigation Component
 * Fixed navigation bar with logo and auth buttons
 */

'use client';

import React from 'react';
import Link from 'next/link';

export default function Navigation() {
  return (
    <nav className="landing-nav">
      <div className="nav-container">
        <div className="logo">TaskNest</div>

        <ul className="nav-links">
          <li><a href="#features">Features</a></li>
          <li><a href="#how-it-works">How It Works</a></li>
          <li><a href="#pricing">Pricing</a></li>
          <li><a href="#testimonials">Testimonials</a></li>
          <li><a href="#faq">FAQ</a></li>
        </ul>

        <div className="nav-cta">
          <Link href="/login" className="btn btn-outline">Sign In</Link>
          <Link href="/signup" className="btn btn-primary">Get Started</Link>
        </div>
      </div>
    </nav>
  );
}
