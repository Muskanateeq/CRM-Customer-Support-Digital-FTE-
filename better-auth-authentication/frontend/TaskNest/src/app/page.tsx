/**
 * TaskNest Landing Page - Production Level Design
 *
 * Features:
 * - Comprehensive sections (Hero, Features, How It Works, Testimonials, Pricing, FAQ)
 * - Professional Lucide React icons
 * - Smooth scroll animations
 * - Modern typography
 * - Responsive design for all devices
 * - Brand colors (Black, White, Gold #E49B0F)
 * - Component-based architecture
 */

'use client';

import React, { useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import './landing.css';

// Landing Page Components
import Navigation from '@/components/landing/Navigation';
import Hero from '@/components/landing/Hero';
import Features from '@/components/landing/Features';
import HowItWorks from '@/components/landing/HowItWorks';
import Testimonials from '@/components/landing/Testimonials';
import Pricing from '@/components/landing/Pricing';
import FAQ from '@/components/landing/FAQ';
import CTA from '@/components/landing/CTA';
import Footer from '@/components/landing/Footer';

export default function Home() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  /**
   * Redirect authenticated users to dashboard page
   */
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isLoading, isAuthenticated, router]);

  /**
   * Show loading state
   */
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-gray-900 to-black">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-[#E49B0F] border-t-transparent"></div>
          <p className="mt-6 text-white text-lg">Loading TaskNest...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ backgroundColor: 'var(--bg-darker)', color: 'var(--text-light)' }}>
      {/* Navigation */}
      <Navigation />

      {/* Main Content */}
      <main>
        {/* Hero Section */}
        <Hero />

        {/* Features Section */}
        <Features />

        {/* How It Works Section */}
        <HowItWorks />

        {/* Testimonials Section */}
        <Testimonials />

        {/* Pricing Section */}
        <Pricing />

        {/* FAQ Section */}
        <FAQ />

        {/* Call to Action Section */}
        <CTA />
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}
