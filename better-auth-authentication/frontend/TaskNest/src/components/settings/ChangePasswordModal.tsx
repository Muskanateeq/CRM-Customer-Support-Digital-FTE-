/**
 * ChangePasswordModal Component
 * Modal for changing user password with backend integration
 * Dark Golden Theme - Modern SaaS Design
 */

'use client';

import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Modal from '@/components/ui/Modal';
import { changePassword } from '@/lib/settingsApi';
import './ChangePasswordModal.css';

export interface ChangePasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ChangePasswordModal({ isOpen, onClose }: ChangePasswordModalProps) {
  const { getToken } = useAuth();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  /**
   * Handle form submit
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!currentPassword || !newPassword || !confirmPassword) {
      setError('All fields are required');
      return;
    }

    if (newPassword.length < 8) {
      setError('New password must be at least 8 characters');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    setIsSubmitting(true);

    try {
      const token = await getToken();
      if (!token) {
        setError('Authentication required. Please log in again.');
        return;
      }

      await changePassword(token, {
        current_password: currentPassword,
        new_password: newPassword,
      });

      alert('Password changed successfully!');
      handleClose();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to change password. Please try again.';
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Handle close
   */
  const handleClose = () => {
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
    setError('');
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Change Password">
      <form onSubmit={handleSubmit} className="change-password-form">
        {error && (
          <div className="password-error">
            {error}
          </div>
        )}

        <div className="form-group">
          <label htmlFor="current-password">Current Password</label>
          <input
            id="current-password"
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            placeholder="Enter current password"
            className="password-input"
            disabled={isSubmitting}
          />
        </div>

        <div className="form-group">
          <label htmlFor="new-password">New Password</label>
          <input
            id="new-password"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="Enter new password (min 8 characters)"
            className="password-input"
            disabled={isSubmitting}
          />
        </div>

        <div className="form-group">
          <label htmlFor="confirm-password">Confirm New Password</label>
          <input
            id="confirm-password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm new password"
            className="password-input"
            disabled={isSubmitting}
          />
        </div>

        <div className="password-requirements">
          <p className="requirements-title">Password Requirements:</p>
          <ul>
            <li className={newPassword.length >= 8 ? 'valid' : ''}>
              At least 8 characters
            </li>
            <li className={/[A-Z]/.test(newPassword) ? 'valid' : ''}>
              One uppercase letter
            </li>
            <li className={/[a-z]/.test(newPassword) ? 'valid' : ''}>
              One lowercase letter
            </li>
            <li className={/[0-9]/.test(newPassword) ? 'valid' : ''}>
              One number
            </li>
          </ul>
        </div>

        <div className="form-actions">
          <button
            type="button"
            onClick={handleClose}
            className="btn-cancel"
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Changing...' : 'Change Password'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
