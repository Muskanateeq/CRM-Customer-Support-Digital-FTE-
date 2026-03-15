/**
 * Chat Page - TaskNest
 * AI Assistant with natural language task management
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import {
  getConversations,
  getConversationHistory,
  deleteConversation,
  sendMessageStream,
  type Conversation,
  type Message,
} from '@/lib/chatApi';
import './chat.css';

export default function ChatPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading, getToken } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [conversationToDelete, setConversationToDelete] = useState<number | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  /**
   * Redirect if not authenticated
   */
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  /**
   * Load conversations (no loading state - instant display)
   */
  const loadConversations = React.useCallback(async () => {
    if (!isAuthenticated) return;

    try {
      const token = await getToken();
      if (!token) return;

      const data = await getConversations(token, 50, 0);
      setConversations(data.conversations);

      // Auto-select first conversation if none selected
      if (!selectedConversation && data.conversations.length > 0) {
        setSelectedConversation(data.conversations[0].id);
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
      setError('Failed to load conversations');
    }
  }, [isAuthenticated, getToken, selectedConversation]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  /**
   * Load conversation messages
   */
  const loadMessages = React.useCallback(async (conversationId: number) => {
    try {
      const token = await getToken();
      if (!token) return;

      const data = await getConversationHistory(token, conversationId, 100, 0);
      setMessages(data.messages);
    } catch (error) {
      console.error('Failed to load messages:', error);
      setError('Failed to load messages');
    }
  }, [getToken]);

  useEffect(() => {
    if (selectedConversation) {
      loadMessages(selectedConversation);
    } else {
      setMessages([]);
    }
  }, [selectedConversation, loadMessages]);

  /**
   * Scroll to bottom
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  /**
   * Send message with streaming
   */
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isSending) return;

    const userMessageContent = inputValue.trim();
    setInputValue('');
    setIsSending(true);
    setError(null);

    // Add user message to UI
    const userMessage: Message = {
      id: Date.now(),
      conversation_id: selectedConversation || 0,
      role: 'user',
      content: userMessageContent,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);

    // Create placeholder for assistant message
    const assistantMessageId = Date.now() + 1;
    const assistantMessage: Message = {
      id: assistantMessageId,
      conversation_id: selectedConversation || 0,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, assistantMessage]);

    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Authentication required');
      }

      let newConversationId = selectedConversation;

      // Stream response
      for await (const event of sendMessageStream(
        token,
        userMessageContent,
        selectedConversation || undefined
      )) {
        if (event.type === 'conversation_id') {
          newConversationId = event.conversation_id as number;
          if (!selectedConversation) {
            setSelectedConversation(newConversationId);
            // Reload conversations to show new one
            loadConversations();
          }
        } else if (event.type === 'content') {
          // Append content to assistant message
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, content: msg.content + event.content }
                : msg
            )
          );
        } else if (event.type === 'tool_call') {
          // Show tool execution
          if (event.status === 'executing') {
            setMessages(prev =>
              prev.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, content: msg.content + `\n\n🔧 ${event.tool}...` }
                  : msg
              )
            );
          }
        } else if (event.type === 'done') {
          // Streaming complete
          setIsSending(false);
        } else if (event.type === 'error') {
          throw new Error(String(event.error));
        }
      }
    } catch (err) {
      console.error('Failed to send message:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message');

      // Update assistant message with error
      setMessages(prev =>
        prev.map(msg =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content: `Error: ${err instanceof Error ? err.message : 'Failed to send message'}`,
              }
            : msg
        )
      );
    } finally {
      setIsSending(false);
    }
  };

  /**
   * Handle Enter key
   */
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  /**
   * Start new conversation
   */
  const handleNewConversation = () => {
    setSelectedConversation(null);
    setMessages([]);
    setError(null);
  };

  /**
   * Delete conversation with optimistic UI update
   */
  const handleDeleteConversation = async (conversationId: number) => {
    // Save current state for rollback
    const previousConversations = conversations;
    const previousSelectedConversation = selectedConversation;
    const previousMessages = messages;

    // Optimistically update UI immediately
    setConversations(prev => prev.filter(c => c.id !== conversationId));

    // Show success message immediately
    setSuccessMessage(`Conversation ${conversationId} deleted successfully`);
    setTimeout(() => setSuccessMessage(null), 3000);

    // Close dialog immediately
    setDeleteDialogOpen(false);
    setConversationToDelete(null);

    // Clear selection if deleted
    if (selectedConversation === conversationId) {
      setSelectedConversation(null);
      setMessages([]);
    }

    // Call API in background
    try {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');

      await deleteConversation(token, conversationId);
      // Success - UI already updated
    } catch (error) {
      // Rollback on error
      console.error('Failed to delete conversation:', error);
      setConversations(previousConversations);
      setSuccessMessage(null);
      setError('Failed to delete conversation. Please try again.');

      // Restore selection if it was deleted
      if (previousSelectedConversation === conversationId) {
        setSelectedConversation(previousSelectedConversation);
        setMessages(previousMessages);
      }
    }
  };

  /**
   * Open delete confirmation dialog
   */
  const openDeleteDialog = (conversationId: number) => {
    setConversationToDelete(conversationId);
    setDeleteDialogOpen(true);
  };

  /**
   * Format timestamp
   */
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (authLoading || !isAuthenticated) {
    return null;
  }

  return (
    <div className="chat-page">
      {/* Sidebar - Conversations List */}
      <div className="chat-sidebar">
        <div className="sidebar-header">
          <h2>Conversations</h2>
          <button onClick={handleNewConversation} className="btn-new-chat" title="New conversation">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </div>

        <div className="conversations-list">
          {conversations.length === 0 ? (
            <div className="empty-state">
              <p>No conversations yet</p>
              <p className="empty-hint">Start a new chat to begin</p>
            </div>
          ) : (
            conversations.map(conversation => (
              <div
                key={conversation.id}
                className={`conversation-item ${selectedConversation === conversation.id ? 'active' : ''}`}
                onClick={() => setSelectedConversation(conversation.id)}
              >
                <div className="conversation-icon">
                  <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z" />
                  </svg>
                </div>
                <div className="conversation-info">
                  <div className="conversation-title">
                    Conversation {conversation.id}
                  </div>
                  <div className="conversation-date">
                    {new Date(conversation.updated_at).toLocaleDateString()}
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    openDeleteDialog(conversation.id);
                  }}
                  className="btn-delete-conversation"
                  title="Delete conversation"
                >
                  <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-main">
        {/* Header */}
        <div className="chat-header">
          <div className="header-content">
            <div className="header-icon">
              <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
            <div>
              <h1>AI Assistant</h1>
              <p>Manage your tasks with natural language</p>
            </div>
          </div>
          {successMessage && (
            <div className="success-message">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
              </svg>
              <span>{successMessage}</span>
            </div>
          )}
        </div>

        {/* Messages */}
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="chat-empty">
              <svg width="80" height="80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
              <h3>Start a conversation</h3>
              <p>Try asking:</p>
              <ul>
                <li>&quot;Add a task to buy groceries tomorrow&quot;</li>
                <li>&quot;Show me all my high priority tasks&quot;</li>
                <li>&quot;Mark task 5 as complete&quot;</li>
                <li>&quot;Update task 3 to have medium priority&quot;</li>
              </ul>
            </div>
          ) : (
            <>
              {messages.map(message => (
                <div
                  key={message.id}
                  className={`message ${message.role === 'user' ? 'message-user' : 'message-assistant'}`}
                >
                  <div className="message-avatar">
                    {message.role === 'user' ? (
                      <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                      </svg>
                    ) : (
                      <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z" />
                      </svg>
                    )}
                  </div>
                  <div className="message-content">
                    <div className="message-text">{message.content}</div>
                    <div className="message-time">{formatTime(message.created_at)}</div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="chat-input-container">
          {error && (
            <div className="chat-error">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
              </svg>
              <span>{error}</span>
            </div>
          )}
          <div className="chat-input-wrapper">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type a message... (e.g., Add a task to buy groceries tomorrow)"
              className="chat-input"
              rows={1}
              disabled={isSending}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isSending}
              className="chat-send-button"
              aria-label="Send message"
            >
              {isSending ? (
                <svg className="spinner" width="20" height="20" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" opacity="0.25" />
                  <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" opacity="0.75" />
                </svg>
              ) : (
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      {deleteDialogOpen && (
        <div className="delete-dialog-overlay" onClick={() => setDeleteDialogOpen(false)}>
          <div className="delete-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="delete-dialog-icon">
              <svg width="48" height="48" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </div>
            <h3>Delete Conversation?</h3>
            <p>This action cannot be undone. All messages in this conversation will be permanently deleted.</p>
            <div className="delete-dialog-actions">
              <button
                onClick={() => setDeleteDialogOpen(false)}
                className="btn-cancel"
              >
                Cancel
              </button>
              <button
                onClick={() => conversationToDelete && handleDeleteConversation(conversationToDelete)}
                className="btn-delete"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
