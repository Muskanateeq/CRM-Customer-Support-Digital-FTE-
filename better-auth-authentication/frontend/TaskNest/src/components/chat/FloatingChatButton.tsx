/**
 * Floating Chat Button Component - TaskNest Theme
 *
 * Dark golden theme matching TaskNest design system
 * Colors: Black (#000000), Gamboge (#E49B0F), White (#FFFFFF)
 */

'use client';

import React, { useState, useEffect } from 'react';

/**
 * ChatKit Dynamic Import
 */
const ChatKitModal = React.lazy(() => import('./ChatKitModal'));

/**
 * Floating Chat Button Component
 */
export default function FloatingChatButton() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return null;
  }

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="floating-chat-button"
        aria-label="Open AI Assistant"
        title="AI Assistant"
      >
        <svg
          width="24"
          height="24"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          className="chat-icon"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
        <span className="button-pulse"></span>
      </button>

      {/* Tooltip */}
      <div className="floating-chat-tooltip">AI Assistant</div>

      {/* Chat Modal */}
      {isOpen && (
        <React.Suspense fallback={<div>Loading...</div>}>
          <ChatKitModal isOpen={isOpen} onClose={() => setIsOpen(false)} />
        </React.Suspense>
      )}

      <style jsx>{`
        /* Floating Button */
        .floating-chat-button {
          position: fixed;
          bottom: 2rem;
          right: 2rem;
          width: 60px;
          height: 60px;
          background: linear-gradient(135deg, #d4af37 0%, #e6c34f 100%);
          color: #000000;
          border: none;
          border-radius: 50%;
          box-shadow: 0 4px 14px 0 rgba(212, 175, 55, 0.39);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.3s ease;
          z-index: 9998;
        }

        .floating-chat-button:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 24px 0 rgba(212, 175, 55, 0.6);
        }

        .floating-chat-button:active {
          transform: translateY(-2px);
        }

        .chat-icon {
          position: relative;
          z-index: 2;
          transition: transform 0.3s ease;
        }

        .floating-chat-button:hover .chat-icon {
          transform: scale(1.1);
        }

        /* Pulse Animation */
        .button-pulse {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          border-radius: 50%;
          background: linear-gradient(135deg, #E49B0F 0%, #F5B942 100%);
          opacity: 0.6;
          animation: pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }

        @keyframes pulse-ring {
          0% {
            transform: scale(1);
            opacity: 0.6;
          }
          50% {
            transform: scale(1.15);
            opacity: 0.3;
          }
          100% {
            transform: scale(1);
            opacity: 0.6;
          }
        }

        /* Tooltip */
        .floating-chat-tooltip {
          position: fixed;
          bottom: 2.25rem;
          right: 5.5rem;
          background: rgba(10, 10, 10, 0.95);
          color: #E49B0F;
          padding: 0.5rem 1rem;
          border-radius: 8px;
          font-size: 0.875rem;
          font-weight: 500;
          white-space: nowrap;
          opacity: 0;
          pointer-events: none;
          transition: opacity 0.3s ease;
          z-index: 9997;
          border: 1px solid rgba(228, 155, 15, 0.3);
          box-shadow: 0 4px 14px 0 rgba(228, 155, 15, 0.2);
        }

        .floating-chat-button:hover + .floating-chat-tooltip {
          opacity: 1;
        }

        /* Mobile adjustments */
        @media (max-width: 768px) {
          .floating-chat-button {
            bottom: 1.5rem;
            right: 1.5rem;
            width: 56px;
            height: 56px;
          }

          .floating-chat-tooltip {
            display: none;
          }
        }

        /* Accessibility */
        .floating-chat-button:focus-visible {
          outline: 2px solid #E49B0F;
          outline-offset: 4px;
        }
      `}</style>
    </>
  );
}
