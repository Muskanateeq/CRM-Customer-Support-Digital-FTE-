/**
 * Footer Component
 * Detailed footer with links and social media
 */

'use client';

import React from 'react';

const footerLinks = {
  product: [
    { name: 'Features', href: '#features' },
    { name: 'Pricing', href: '#pricing' },
    { name: 'Integrations', href: '#' },
    { name: 'Changelog', href: '#' },
  ],
  company: [
    { name: 'About', href: '#' },
    { name: 'Blog', href: '#' },
    { name: 'Careers', href: '#' },
    { name: 'Contact', href: '#' },
  ],
  resources: [
    { name: 'Documentation', href: '#' },
    { name: 'Help Center', href: '#' },
    { name: 'API', href: '#' },
    { name: 'Status', href: '#' },
  ],
  legal: [
    { name: 'Privacy', href: '#' },
    { name: 'Terms', href: '#' },
    { name: 'Security', href: '#' },
    { name: 'Cookies', href: '#' },
  ],
};

export default function Footer() {
  return (
    <footer className="landing-footer">
      <div className="footer-container">
        <div className="footer-grid">
          {/* Brand Column */}
          <div className="footer-brand">
            <h3>TaskNest</h3>
            <p>The modern task management platform for teams that want to achieve more.</p>
            <div className="social-links">
              <a href="#">𝕏</a>
              <a href="#">in</a>
              <a href="#">f</a>
              <a href="#">📷</a>
            </div>
          </div>

          {/* Product Links */}
          <div className="footer-column">
            <h4>Product</h4>
            <ul>
              {footerLinks.product.map((link, index) => (
                <li key={index}>
                  <a href={link.href}>{link.name}</a>
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div className="footer-column">
            <h4>Company</h4>
            <ul>
              {footerLinks.company.map((link, index) => (
                <li key={index}>
                  <a href={link.href}>{link.name}</a>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources Links */}
          <div className="footer-column">
            <h4>Resources</h4>
            <ul>
              {footerLinks.resources.map((link, index) => (
                <li key={index}>
                  <a href={link.href}>{link.name}</a>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal Links */}
          <div className="footer-column">
            <h4>Legal</h4>
            <ul>
              {footerLinks.legal.map((link, index) => (
                <li key={index}>
                  <a href={link.href}>{link.name}</a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <p>&copy; 2024 TaskNest. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
