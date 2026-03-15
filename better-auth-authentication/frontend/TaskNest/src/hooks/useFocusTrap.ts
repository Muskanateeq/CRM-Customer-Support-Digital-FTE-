/**
 * useFocusTrap Hook - Trap Focus Within Element
 *
 * Features:
 * - Traps focus within a container (useful for modals)
 * - Handles Tab and Shift+Tab navigation
 * - Returns focus to trigger element on close
 * - Prevents focus from leaving the container
 */

'use client';

import { useEffect, useRef } from 'react';

export interface UseFocusTrapOptions {
  isActive: boolean;
  onEscape?: () => void;
  initialFocus?: boolean;
  returnFocus?: boolean;
}

export function useFocusTrap<T extends HTMLElement = HTMLElement>(
  options: UseFocusTrapOptions = { isActive: true }
) {
  const containerRef = useRef<T>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!options.isActive) return;

    const container = containerRef.current;
    if (!container) return;

    // Store the element that had focus before the trap was activated
    previousActiveElement.current = document.activeElement as HTMLElement;

    // Get all focusable elements within the container
    const getFocusableElements = (): HTMLElement[] => {
      if (!container) return [];

      const focusableSelectors = [
        'a[href]',
        'button:not([disabled])',
        'textarea:not([disabled])',
        'input:not([disabled])',
        'select:not([disabled])',
        '[tabindex]:not([tabindex="-1"])',
      ].join(', ');

      return Array.from(container.querySelectorAll(focusableSelectors));
    };

    // Focus the first focusable element
    if (options.initialFocus !== false) {
      const focusableElements = getFocusableElements();
      if (focusableElements.length > 0) {
        focusableElements[0].focus();
      }
    }

    // Handle keyboard events
    const handleKeyDown = (event: KeyboardEvent) => {
      // Handle Escape key
      if (event.key === 'Escape' && options.onEscape) {
        options.onEscape();
        return;
      }

      // Handle Tab key
      if (event.key === 'Tab') {
        const focusableElements = getFocusableElements();
        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        // Shift + Tab (backwards)
        if (event.shiftKey) {
          if (document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
          }
        }
        // Tab (forwards)
        else {
          if (document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    container.addEventListener('keydown', handleKeyDown);

    // Cleanup
    return () => {
      container.removeEventListener('keydown', handleKeyDown);

      // Return focus to the previously focused element
      if (options.returnFocus !== false && previousActiveElement.current) {
        previousActiveElement.current.focus();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [options.isActive, options.onEscape, options.initialFocus, options.returnFocus]);

  return containerRef;
}
