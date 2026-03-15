/**
 * KeyboardShortcutsModal Component
 * Displays available keyboard shortcuts
 */

'use client';

import React from 'react';
import Modal from '@/components/ui/Modal';
import './KeyboardShortcutsModal.css';

interface KeyboardShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const shortcuts = [
  { key: 'N', description: 'Create new task' },
  { key: 'S', description: 'Focus search bar' },
  { key: 'F', description: 'Toggle filter panel' },
  { key: 'E', description: 'Edit selected task' },
  { key: 'Delete', description: 'Delete selected task' },
  { key: 'Escape', description: 'Close modal or panel' },
  { key: '?', description: 'Show keyboard shortcuts' },
];

export default function KeyboardShortcutsModal({
  isOpen,
  onClose,
}: KeyboardShortcutsModalProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Keyboard Shortcuts">
      <div className="keyboard-shortcuts-modal">
        <p className="keyboard-shortcuts-description">
          Use these keyboard shortcuts to navigate and manage tasks quickly.
        </p>

        <div className="keyboard-shortcuts-list">
          {shortcuts.map((shortcut) => (
            <div key={shortcut.key} className="keyboard-shortcut-item">
              <kbd className="keyboard-shortcut-key">{shortcut.key}</kbd>
              <span className="keyboard-shortcut-description">
                {shortcut.description}
              </span>
            </div>
          ))}
        </div>

        <div className="keyboard-shortcuts-note">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>
            Keyboard shortcuts are disabled when typing in input fields.
          </span>
        </div>
      </div>
    </Modal>
  );
}
