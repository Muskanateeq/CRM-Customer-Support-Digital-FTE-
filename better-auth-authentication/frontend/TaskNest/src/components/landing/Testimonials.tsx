/**
 * Testimonials Section Component
 * Customer reviews and feedback
 */

'use client';

import React from 'react';

const testimonials = [
  {
    name: 'Sarah Johnson',
    role: 'Product Manager at TechCorp',
    content: 'TaskNest transformed how our team works. The AI features are game-changing, and the interface is incredibly intuitive.',
  },
  {
    name: 'Michael Chen',
    role: 'CEO at StartupXYZ',
    content: "We've tried many task management tools, but TaskNest is by far the best. It's powerful yet simple to use.",
  },
  {
    name: 'Emily Rodriguez',
    role: 'Design Lead at Creative Co',
    content: 'The collaboration features are outstanding. Our remote team stays connected and productive thanks to TaskNest.',
  },
];

export default function Testimonials() {
  return (
    <section id="testimonials" className="testimonials">
      <div className="section-header">
        <span className="section-badge">Testimonials</span>
        <h2>Loved by Teams Worldwide</h2>
        <p>See what our customers have to say about TaskNest.</p>
      </div>

      <div className="testimonials-grid">
        {testimonials.map((testimonial, index) => (
          <div key={index} className="testimonial-card">
            <div className="testimonial-header">
              <div className="avatar"></div>
              <div className="testimonial-info">
                <h4>{testimonial.name}</h4>
                <p>{testimonial.role}</p>
              </div>
            </div>
            <div className="stars">★★★★★</div>
            <p>&quot;{testimonial.content}&quot;</p>
          </div>
        ))}
      </div>
    </section>
  );
}
