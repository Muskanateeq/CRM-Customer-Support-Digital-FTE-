/**
 * FAQ Section Component
 * Frequently Asked Questions with accordion
 */

'use client';

import React, { useState } from 'react';
import { Plus, Minus } from 'lucide-react';

const faqs = [
  {
    question: 'How does the free trial work?',
    answer: 'You get 14 days of full access to all Professional features. No credit card required. Cancel anytime.',
  },
  {
    question: 'Can I change plans later?',
    answer: 'Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately.',
  },
  {
    question: 'Is my data secure?',
    answer: 'Absolutely. We use bank-level encryption and comply with all major security standards including SOC 2 and GDPR.',
  },
  {
    question: 'Do you offer refunds?',
    answer: "Yes, we offer a 30-day money-back guarantee. If you're not satisfied, we'll refund your payment.",
  },
  {
    question: 'Can I integrate with other tools?',
    answer: 'Yes! TaskNest integrates with popular tools like Slack, Google Workspace, Microsoft Teams, and more.',
  },
];

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section id="faq" className="faq">
      <div className="section-header">
        <span className="section-badge">FAQ</span>
        <h2>Frequently Asked Questions</h2>
        <p>Everything you need to know about TaskNest.</p>
      </div>

      <div className="faq-container">
        {faqs.map((faq, index) => (
          <div key={index} className="faq-item">
            <div
              className="faq-question-wrapper"
              onClick={() => toggleFAQ(index)}
            >
              <div className="faq-question">{faq.question}</div>
              <div className="faq-icon">
                {openIndex === index ? (
                  <Minus style={{ width: '1.25rem', height: '1.25rem' }} />
                ) : (
                  <Plus style={{ width: '1.25rem', height: '1.25rem' }} />
                )}
              </div>
            </div>
            <div className={`faq-answer ${openIndex === index ? 'open' : ''}`}>
              {faq.answer}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
