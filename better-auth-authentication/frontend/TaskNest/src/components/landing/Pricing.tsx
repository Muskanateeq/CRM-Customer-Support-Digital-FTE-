/**
 * Pricing Section Component
 * Displays pricing plans with features
 */

'use client';

import React, { useState } from 'react';
import Link from 'next/link';

const pricingPlans = [
  {
    name: 'Starter',
    price: '$0',
    period: '/month',
    description: 'Perfect for individuals',
    features: [
      'Up to 10 tasks',
      'Basic features',
      '1 workspace',
      'Email support',
    ],
    buttonText: 'Get Started',
    featured: false,
  },
  {
    name: 'Professional',
    price: '$12',
    period: '/month',
    description: 'For growing teams',
    features: [
      'Unlimited tasks',
      'Advanced features',
      'Unlimited workspaces',
      'Priority support',
      'AI-powered insights',
      'Advanced analytics',
    ],
    buttonText: 'Start Free Trial',
    featured: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    description: 'For large organizations',
    features: [
      'Everything in Pro',
      'Custom integrations',
      'Dedicated support',
      'SLA guarantee',
      'Advanced security',
      'Custom training',
    ],
    buttonText: 'Contact Sales',
    featured: false,
  },
];

export default function Pricing() {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  return (
    <section id="pricing" className="pricing">
      <div className="section-header">
        <span className="section-badge">Pricing</span>
        <h2>Choose Your Plan</h2>
        <p>Flexible pricing for teams of all sizes.</p>
      </div>

      <div className="pricing-grid">
        {pricingPlans.map((plan, index) => {
          const isFeatured = plan.featured && hoveredIndex === null;
          const isHovered = hoveredIndex === index;

          return (
            <div
              key={index}
              className={`pricing-card ${isFeatured || isHovered ? 'featured' : ''}`}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              <h3>{plan.name}</h3>
              <div className="price">
                {plan.price}
                {plan.period && <span>{plan.period}</span>}
              </div>
              <p>{plan.description}</p>
              <ul className="features-list">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex}>{feature}</li>
                ))}
              </ul>
              <Link href="/signup" className="btn btn-primary">
                {plan.buttonText}
              </Link>
            </div>
          );
        })}
      </div>
    </section>
  );
}
