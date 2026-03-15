/**
 * Custom Chat Modal Component - TaskNest Theme
 *
 * Dark golden theme matching TaskNest design system
 * Colors: Black (#000000), Gamboge (#E49B0F), White (#FFFFFF)
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRefresh } from '@/contexts/RefreshContext';
import { getConversations, getConversationHistory, deleteConversation, type Conversation, type Message as ApiMessage } from '@/lib/chatApi';

/**
 * Chat Modal Props
 */
interface ChatKitModalProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * Message Interface
 */
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

/**
 * Custom Chat Modal Component
 */
export default function ChatKitModal({ isOpen, onClose }: ChatKitModalProps) {
  const { getToken } = useAuth();
  const { refreshAll } = useRefresh();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [conversationToDelete, setConversationToDelete] = useState<number | null>(null);
  const [_successMessage, setSuccessMessage] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'chat' | 'history'>('chat'); // Track current view
  const messagesEndRef = useRef<HTMLDivElement>(null);

  /**
   * Scroll to bottom of messages - INSTANT (no smooth animation)
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'auto' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  /**
   * Handle escape key
   */
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  /**
   * Send message to backend with INSTANT streaming (0ms delay)
   */
  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    // INSTANT: Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setError(null);

    // INSTANT: Create assistant placeholder immediately (visible instantly)
    const assistantMessageId = (Date.now() + 1).toString();
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '', // Empty but visible - will stream content
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, assistantMessage]);

    // Set loading AFTER messages are visible (non-blocking)
    setIsLoading(true);

    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Authentication required');
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
      const response = await fetch(`${apiUrl}/api/v1/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // INSTANT streaming - process chunks immediately
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode and display immediately (0ms delay)
        buffer += decoder.decode(value, { stream: true });

        // Process complete SSE messages instantly
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            try {
              const event = JSON.parse(data);

              if (event.type === 'conversation_id') {
                setConversationId(event.conversation_id);
              } else if (event.type === 'content') {
                // INSTANT: Append content immediately (no batching, no delays)
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantMessageId
                      ? { ...msg, content: msg.content + event.content }
                      : msg
                  )
                );
              } else if (event.type === 'tool_call') {
                // Handle tool execution status
                if (event.status === 'executing') {
                  setMessages(prev =>
                    prev.map(msg =>
                      msg.id === assistantMessageId
                        ? { ...msg, content: msg.content + `\n\n🔧 ${event.tool}...` }
                        : msg
                    )
                  );
                } else if (event.status === 'completed') {
                  // Tool executed successfully
                  setMessages(prev =>
                    prev.map(msg =>
                      msg.id === assistantMessageId
                        ? { ...msg, content: msg.content + ` ✓` }
                        : msg
                    )
                  );
                } else if (event.status === 'failed') {
                  // Tool execution failed - show user-friendly error
                  const errorMsg = event.error || 'Tool execution failed';
                  setMessages(prev =>
                    prev.map(msg =>
                      msg.id === assistantMessageId
                        ? { ...msg, content: msg.content + `\n\n❌ Failed to execute ${event.tool}: ${errorMsg}` }
                        : msg
                    )
                  );
                }
              } else if (event.type === 'done') {
                setIsLoading(false);
                // Trigger UI refresh after chatbot actions complete
                if (event.tool_calls && event.tool_calls.length > 0) {
                  console.log('[ChatKitModal] Chatbot actions completed, triggering UI refresh');
                  refreshAll();
                }
              } else if (event.type === 'error') {
                // Handle general errors with user-friendly messages
                const errorMsg = event.error || 'An error occurred';
                const userFriendlyMsg = errorMsg.includes('validation failed')
                  ? 'Sorry, I had trouble understanding the task details. Please try rephrasing your request.'
                  : errorMsg.includes('not found')
                  ? 'The requested task was not found. Please check and try again.'
                  : errorMsg.includes('Authentication')
                  ? 'Your session has expired. Please refresh the page and try again.'
                  : errorMsg;

                throw new Error(userFriendlyMsg);
              }
            } catch (parseError) {
              console.error('SSE parse error:', parseError);
            }
          }
        }
      }
    } catch (err) {
      console.error('Send error:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message');

      // Show error instantly
      setMessages(prev =>
        prev.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, content: `Error: ${err instanceof Error ? err.message : 'Failed to send message'}` }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle Enter key
   */
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  /**
   * Load conversation history
   */
  const loadHistory = async () => {
    setIsLoadingHistory(true);
    try {
      const token = await getToken();
      if (!token) return;

      const data = await getConversations(token, 50, 0);
      setConversations(data.conversations);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  /**
   * Toggle history panel
   */
  const toggleHistory = () => {
    if (!isHistoryOpen) {
      loadHistory();
      setViewMode('history'); // Switch to history view
    }
    setIsHistoryOpen(!isHistoryOpen);
  };

  /**
   * Load and resume a conversation - INSTANT UX
   */
  const resumeConversation = async (convId: number) => {
    // INSTANT: Switch to chat view immediately (0 seconds wait)
    setConversationId(convId);
    setViewMode('chat');
    setIsHistoryOpen(false);

    // Show loading placeholder message instantly
    setMessages([{
      id: 'loading',
      role: 'assistant',
      content: 'Loading conversation...',
      timestamp: new Date(),
    }]);

    // Load messages in background
    try {
      const token = await getToken();
      if (!token) return;

      const data = await getConversationHistory(token, convId, 100, 0);

      // Convert API messages to local Message format (filter out system messages)
      const loadedMessages: Message[] = data.messages
        .filter((msg: ApiMessage) => msg.role === 'user' || msg.role === 'assistant')
        .map((msg: ApiMessage) => ({
          id: msg.id.toString(),
          role: msg.role as 'user' | 'assistant',
          content: msg.content,
          timestamp: new Date(msg.created_at),
        }));

      // Replace loading message with actual messages
      setMessages(loadedMessages);
    } catch (error) {
      console.error('Failed to load conversation:', error);
      setMessages([{
        id: 'error',
        role: 'assistant',
        content: 'Failed to load conversation. Please try again.',
        timestamp: new Date(),
      }]);
    }
  };

  /**
   * Delete conversation with optimistic UI
   */
  const handleDeleteConversation = async (convId: number) => {
    // Save current state for rollback
    const previousConversations = conversations;
    const previousConversationId = conversationId;
    const previousMessages = messages;

    // Optimistically update UI immediately
    setConversations(prev => prev.filter(c => c.id !== convId));

    // Show success message immediately
    setSuccessMessage(`Conversation ${convId} deleted successfully`);
    setTimeout(() => setSuccessMessage(null), 3000);

    // Close dialog immediately
    setDeleteDialogOpen(false);
    setConversationToDelete(null);

    // If current conversation is deleted, clear it immediately
    if (conversationId === convId) {
      setConversationId(null);
      setMessages([]);
      setViewMode('history'); // Go back to history view
    }

    // Call API in background
    try {
      const token = await getToken();
      if (!token) throw new Error('Authentication required');

      await deleteConversation(token, convId);
      // Success - UI already updated
    } catch (error) {
      // Rollback on error
      console.error('Failed to delete conversation:', error);
      setConversations(previousConversations);
      setSuccessMessage(null);
      setError('Failed to delete conversation. Please try again.');

      // Restore conversation if it was current
      if (previousConversationId === convId) {
        setConversationId(previousConversationId);
        setMessages(previousMessages);
      }
    }
  };

  /**
   * Open delete dialog
   */
  const openDeleteDialog = (convId: number) => {
    setConversationToDelete(convId);
    setDeleteDialogOpen(true);
  };

  /**
   * Start new conversation
   */
  const startNewChat = () => {
    setConversationId(null);
    setMessages([]);
    setViewMode('chat'); // Switch to chat view
    setIsHistoryOpen(false);
  };

  /**
   * Close conversation and go back to history
   */
  const _closeConversation = () => {
    setViewMode('history');
    loadHistory();
  };

  /**
   * Don't render if not open
   */
  if (!isOpen) {
    return null;
  }

  return (
    <div className="chat-modal-overlay" onClick={onClose}>
      <div className="chat-modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="chat-modal-header">
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
            <div className="header-text">
              <h2>AI Assistant</h2>
              <p>Manage your tasks with natural language</p>
            </div>
          </div>
          <div className="header-actions">
            <button onClick={toggleHistory} className="history-button" aria-label="Conversation history" title="History">
              <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
            <button onClick={onClose} className="close-button" aria-label="Close chat">
              <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Single View Mode - History OR Chat */}
        {viewMode === 'history' ? (
          /* History View - Full Screen Conversations List */
          <div className="history-view-full">
            <div className="history-view-header">
              <h3>Conversations</h3>
              <div className="history-view-actions">
                <button onClick={startNewChat} className="btn-new-chat" title="New chat">
                  <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  New Chat
                </button>
                <button onClick={() => setViewMode('chat')} className="btn-close-history-view" title="Close history">
                  <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <div className="history-view-content">
              {isLoadingHistory ? (
                <div className="history-loading">Loading conversations...</div>
              ) : conversations.length === 0 ? (
                <div className="history-empty">
                  <svg width="48" height="48" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <p>No conversations yet</p>
                  <button onClick={startNewChat} className="btn-start-first-chat">
                    Start your first conversation
                  </button>
                </div>
              ) : (
                <div className="history-conversations-grid">
                  {conversations.map(conversation => (
                    <div
                      key={conversation.id}
                      className="history-conversation-card"
                      onClick={() => resumeConversation(conversation.id)}
                    >
                      <div className="history-conversation-header">
                        <div className="history-conversation-icon">
                          <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z" />
                          </svg>
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
                      <div className="history-conversation-title">Conversation {conversation.id}</div>
                      <div className="history-conversation-date">
                        {new Date(conversation.updated_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : (
          /* Chat View - Full Screen Chat Interface */
          <>
            {/* Messages Area */}
            <div className="chat-messages">
              {messages.length === 0 ? (
                <div className="chat-empty">
                  <svg width="64" height="64" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                  <h3>Start a conversation</h3>
                  <p>Try: &quot;Add a task to buy groceries tomorrow&quot;</p>
                </div>
              ) : (
                <>
                  {messages.map((message) => (
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
                        <div className="message-time">
                          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
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
                <div className="chat-error-banner">
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
                  placeholder="Type a message... (e.g., 'Add a task to buy groceries tomorrow')"
                  className="chat-input"
                  rows={1}
                  disabled={isLoading}
                />
                <button
                  onClick={sendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  className="chat-send-button"
                  aria-label="Send message"
                >
                  {isLoading ? (
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
          </>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      {deleteDialogOpen && (
        <div className="delete-dialog-overlay-modal" onClick={() => setDeleteDialogOpen(false)}>
          <div className="delete-dialog-modal" onClick={(e) => e.stopPropagation()}>
            <div className="delete-dialog-icon-modal">
              <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </div>
            <h3>Delete Conversation?</h3>
            <p>This action cannot be undone.</p>
            <div className="delete-dialog-actions-modal">
              <button onClick={() => setDeleteDialogOpen(false)} className="btn-cancel-modal">
                Cancel
              </button>
              <button
                onClick={() => conversationToDelete && handleDeleteConversation(conversationToDelete)}
                className="btn-delete-modal"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        /* Modal Overlay */
        .chat-modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.85);
          backdrop-filter: blur(8px);
          -webkit-backdrop-filter: blur(8px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 9999;
          padding: 1rem;
          animation: fadeIn 0.2s ease-out;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        /* Modal Container */
        .chat-modal-container {
          background: rgba(10, 10, 10, 0.98);
          border: 1px solid rgba(228, 155, 15, 0.3);
          border-radius: 16px;
          box-shadow: 0 20px 60px rgba(228, 155, 15, 0.3);
          width: 100%;
          max-width: 500px;
          height: 700px;
          max-height: 90vh;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          animation: slideUp 0.3s ease-out;
        }

        @keyframes slideUp {
          from {
            transform: translateY(30px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        /* Modal Header */
        .chat-modal-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1.5rem;
          border-bottom: 1px solid rgba(228, 155, 15, 0.2);
          background: rgba(228, 155, 15, 0.05);
        }

        .header-actions {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .history-button {
          width: 36px;
          height: 36px;
          background: rgba(228, 155, 15, 0.1);
          border: 1px solid rgba(228, 155, 15, 0.2);
          border-radius: 8px;
          color: #E49B0F;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
          flex-shrink: 0;
        }

        .history-button:hover {
          background: rgba(228, 155, 15, 0.2);
          border-color: #E49B0F;
        }

        .header-content {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .header-icon {
          width: 44px;
          height: 44px;
          background: linear-gradient(135deg, #E49B0F 0%, #F5B942 100%);
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #000000;
          flex-shrink: 0;
        }

        .header-text h2 {
          font-size: 1.25rem;
          font-weight: 700;
          margin: 0;
          background: linear-gradient(135deg, #E49B0F, #F5B942);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .header-text p {
          font-size: 0.8rem;
          margin: 0.25rem 0 0;
          color: #A0A0A0;
        }

        .close-button {
          width: 36px;
          height: 36px;
          background: rgba(228, 155, 15, 0.1);
          border: 1px solid rgba(228, 155, 15, 0.2);
          border-radius: 8px;
          color: #E49B0F;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
          flex-shrink: 0;
        }

        .close-button:hover {
          background: rgba(228, 155, 15, 0.2);
          border-color: #E49B0F;
          transform: rotate(90deg);
        }

        /* History Full Layout - Split View */
        .history-full-layout {
          display: flex;
          height: 100%;
          flex: 1;
          overflow: hidden;
        }

        /* Left Sidebar - Conversations List */
        .history-sidebar {
          width: 320px;
          background: rgba(0, 0, 0, 0.5);
          border-right: 1px solid rgba(228, 155, 15, 0.2);
          display: flex;
          flex-direction: column;
        }

        .history-sidebar-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1rem 1.5rem;
          border-bottom: 1px solid rgba(228, 155, 15, 0.2);
          background: rgba(228, 155, 15, 0.05);
        }

        .history-sidebar-header h3 {
          font-size: 0.875rem;
          font-weight: 700;
          color: #E49B0F;
          margin: 0;
        }

        .btn-new-chat-sidebar {
          width: 32px;
          height: 32px;
          background: rgba(212, 175, 55, 0.15);
          border: 1px solid rgba(212, 175, 55, 0.3);
          border-radius: 8px;
          color: #d4af37;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .btn-new-chat-sidebar:hover {
          background: rgba(212, 175, 55, 0.25);
          transform: translateY(-2px);
        }

        .history-sidebar-content {
          flex: 1;
          overflow-y: auto;
          padding: 0.5rem;
        }

        .history-sidebar-content::-webkit-scrollbar {
          width: 4px;
        }

        .history-sidebar-content::-webkit-scrollbar-track {
          background: rgba(228, 155, 15, 0.05);
        }

        .history-sidebar-content::-webkit-scrollbar-thumb {
          background: rgba(228, 155, 15, 0.3);
          border-radius: 2px;
        }

        .history-conversations-list {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .history-conversation-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(228, 155, 15, 0.1);
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .history-conversation-item:hover {
          background: rgba(255, 255, 255, 0.05);
          border-color: rgba(228, 155, 15, 0.3);
        }

        .history-conversation-item.active {
          background: rgba(228, 155, 15, 0.15);
          border-color: rgba(228, 155, 15, 0.4);
        }

        .history-conversation-icon {
          width: 28px;
          height: 28px;
          background: rgba(228, 155, 15, 0.15);
          border: 1px solid rgba(228, 155, 15, 0.3);
          border-radius: 6px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #E49B0F;
          flex-shrink: 0;
        }

        .history-conversation-info {
          flex: 1;
          min-width: 0;
        }

        .history-conversation-title {
          font-size: 0.8125rem;
          font-weight: 600;
          color: #FFFFFF;
          margin-bottom: 0.25rem;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .history-conversation-date {
          font-size: 0.6875rem;
          color: #666666;
        }

        .btn-delete-conversation-history {
          width: 24px;
          height: 24px;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.2);
          border-radius: 6px;
          color: #EF4444;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.3s ease;
          opacity: 0;
          flex-shrink: 0;
        }

        .history-conversation-item:hover .btn-delete-conversation-history {
          opacity: 1;
        }

        .btn-delete-conversation-history:hover {
          background: rgba(239, 68, 68, 0.2);
          border-color: rgba(239, 68, 68, 0.4);
        }

        /* Right Side - Chat Area */
        .history-chat-area {
          flex: 1;
          display: flex;
          flex-direction: column;
          background: #000000;
        }

        .history-chat-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1rem 1.5rem;
          border-bottom: 1px solid rgba(228, 155, 15, 0.2);
          background: rgba(228, 155, 15, 0.05);
        }

        .history-chat-header h3 {
          font-size: 1rem;
          font-weight: 700;
          color: #E49B0F;
          margin: 0;
        }

        .btn-close-history {
          width: 32px;
          height: 32px;
          background: rgba(228, 155, 15, 0.1);
          border: 1px solid rgba(228, 155, 15, 0.2);
          border-radius: 8px;
          color: #E49B0F;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .btn-close-history:hover {
          background: rgba(228, 155, 15, 0.2);
          transform: rotate(90deg);
        }

        .history-loading,
        .history-empty {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 2rem 1rem;
          text-align: center;
          color: #A0A0A0;
        }

        .history-empty svg {
          color: #E49B0F;
          opacity: 0.5;
          margin-bottom: 0.5rem;
        }

        .history-empty p {
          font-size: 0.8125rem;
          margin: 0;
        }

        /* Delete Dialog in Modal */
        .delete-dialog-overlay-modal {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.85);
          backdrop-filter: blur(8px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 10001;
          animation: fadeIn 0.2s ease-out;
        }

        .delete-dialog-modal {
          background: rgba(10, 10, 10, 0.98);
          border: 1px solid rgba(239, 68, 68, 0.3);
          border-radius: 16px;
          box-shadow: 0 20px 60px rgba(239, 68, 68, 0.3);
          padding: 1.5rem;
          max-width: 360px;
          width: 90%;
          animation: slideUp 0.3s ease-out;
        }

        .delete-dialog-icon-modal {
          width: 48px;
          height: 48px;
          background: rgba(239, 68, 68, 0.1);
          border: 2px solid rgba(239, 68, 68, 0.3);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #EF4444;
          margin: 0 auto 1rem;
        }

        .delete-dialog-modal h3 {
          font-size: 1.25rem;
          font-weight: 700;
          color: #FFFFFF;
          margin: 0 0 0.5rem;
          text-align: center;
        }

        .delete-dialog-modal p {
          font-size: 0.875rem;
          color: #A0A0A0;
          margin: 0 0 1.5rem;
          text-align: center;
        }

        .delete-dialog-actions-modal {
          display: flex;
          gap: 0.75rem;
        }

        .btn-cancel-modal,
        .btn-delete-modal {
          flex: 1;
          padding: 0.75rem 1rem;
          border-radius: 8px;
          font-size: 0.875rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          border: none;
        }

        .btn-cancel-modal {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          color: #FFFFFF;
        }

        .btn-cancel-modal:hover {
          background: rgba(255, 255, 255, 0.1);
        }

        .btn-delete-modal {
          background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
          color: #FFFFFF;
        }

        .btn-delete-modal:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px 0 rgba(239, 68, 68, 0.6);
        }

        /* Single View Mode - History View */
        .history-view-full {
          display: flex;
          flex-direction: column;
          height: 100%;
          flex: 1;
          overflow: hidden;
          background: #000000;
        }

        .history-view-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1.5rem;
          border-bottom: 1px solid rgba(228, 155, 15, 0.2);
          background: rgba(228, 155, 15, 0.05);
        }

        .history-view-header h3 {
          font-size: 1.125rem;
          font-weight: 700;
          color: #E49B0F;
          margin: 0;
        }

        .history-view-actions {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .btn-new-chat {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.875rem 1.75rem;
          background: linear-gradient(135deg, #d4af37 0%, #e6c34f 100%);
          border: none;
          border-radius: 8px;
          color: #000000;
          font-size: 0.9375rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          min-width: 140px;
          justify-content: center;
        }

        .btn-new-chat:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px 0 rgba(212, 175, 55, 0.6);
        }

        .btn-close-history-view {
          width: 36px;
          height: 36px;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.2);
          border-radius: 8px;
          color: #EF4444;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .btn-close-history-view:hover {
          background: rgba(239, 68, 68, 0.2);
          border-color: #EF4444;
          transform: rotate(90deg);
        }

        .history-view-content {
          flex: 1;
          overflow-y: auto;
          padding: 1.5rem;
        }

        .history-view-content::-webkit-scrollbar {
          width: 6px;
        }

        .history-view-content::-webkit-scrollbar-track {
          background: rgba(228, 155, 15, 0.05);
        }

        .history-view-content::-webkit-scrollbar-thumb {
          background: rgba(228, 155, 15, 0.3);
          border-radius: 3px;
        }

        .history-loading {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: #E49B0F;
          font-size: 0.875rem;
        }

        .history-empty {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          text-align: center;
          color: #A0A0A0;
          gap: 1rem;
        }

        .history-empty svg {
          color: #E49B0F;
          opacity: 0.5;
        }

        .history-empty p {
          font-size: 0.875rem;
          margin: 0;
        }

        .btn-start-first-chat {
          padding: 0.75rem 1.5rem;
          background: linear-gradient(135deg, #E49B0F 0%, #F5B942 100%);
          border: none;
          border-radius: 8px;
          color: #000000;
          font-size: 0.875rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-start-first-chat:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px 0 rgba(228, 155, 15, 0.6);
        }

        .history-conversations-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 1rem;
        }

        .history-conversation-card {
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(228, 155, 15, 0.2);
          border-radius: 12px;
          padding: 1.25rem;
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .history-conversation-card:hover {
          background: rgba(255, 255, 255, 0.05);
          border-color: rgba(228, 155, 15, 0.4);
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(228, 155, 15, 0.2);
        }

        .history-conversation-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .history-conversation-icon {
          width: 36px;
          height: 36px;
          background: rgba(228, 155, 15, 0.15);
          border: 1px solid rgba(228, 155, 15, 0.3);
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #E49B0F;
        }

        .btn-delete-conversation {
          width: 32px;
          height: 32px;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.2);
          border-radius: 6px;
          color: #EF4444;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .btn-delete-conversation:hover {
          background: rgba(239, 68, 68, 0.2);
          border-color: #EF4444;
        }

        .history-conversation-title {
          font-size: 0.9375rem;
          font-weight: 600;
          color: #FFFFFF;
        }

        .history-conversation-date {
          font-size: 0.8125rem;
          color: #A0A0A0;
        }

        /* Single View Mode - Chat View Header */
        .chat-view-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1rem 1.5rem;
          border-bottom: 1px solid rgba(228, 155, 15, 0.2);
          background: rgba(228, 155, 15, 0.05);
        }

        .chat-view-header h3 {
          font-size: 0.9375rem;
          font-weight: 600;
          color: #E49B0F;
          margin: 0;
        }

        .chat-view-actions {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .btn-new-chat-header {
          width: 36px;
          height: 36px;
          background: rgba(212, 175, 55, 0.15);
          border: 1px solid rgba(212, 175, 55, 0.3);
          border-radius: 8px;
          color: #d4af37;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .btn-new-chat-header:hover {
          background: rgba(212, 175, 55, 0.25);
          transform: translateY(-2px);
        }

        .btn-close-conversation {
          width: 36px;
          height: 36px;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.2);
          border-radius: 8px;
          color: #EF4444;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .btn-close-conversation:hover {
          background: rgba(239, 68, 68, 0.2);
          border-color: #EF4444;
          transform: rotate(90deg);
        }

        /* Messages Area */
        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 1.5rem;
          background: #000000;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .chat-messages::-webkit-scrollbar {
          width: 6px;
        }

        .chat-messages::-webkit-scrollbar-track {
          background: rgba(228, 155, 15, 0.05);
        }

        .chat-messages::-webkit-scrollbar-thumb {
          background: rgba(228, 155, 15, 0.3);
          border-radius: 3px;
        }

        .chat-messages::-webkit-scrollbar-thumb:hover {
          background: rgba(228, 155, 15, 0.5);
        }

        /* Empty State */
        .chat-empty {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          text-align: center;
          color: #A0A0A0;
        }

        .chat-empty svg {
          color: #E49B0F;
          margin-bottom: 1rem;
          opacity: 0.5;
        }

        .chat-empty h3 {
          font-size: 1.125rem;
          font-weight: 600;
          color: #FFFFFF;
          margin: 0 0 0.5rem;
        }

        .chat-empty p {
          font-size: 0.875rem;
          margin: 0;
        }

        /* Message */
        .message {
          display: flex;
          gap: 0.75rem;
          animation: messageSlide 0.3s ease-out;
        }

        @keyframes messageSlide {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .message-user {
          flex-direction: row-reverse;
        }

        .message-avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .message-user .message-avatar {
          background: linear-gradient(135deg, #E49B0F 0%, #F5B942 100%);
          color: #000000;
        }

        .message-assistant .message-avatar {
          background: rgba(228, 155, 15, 0.1);
          border: 1px solid rgba(228, 155, 15, 0.3);
          color: #E49B0F;
        }

        .message-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .message-user .message-content {
          align-items: flex-end;
        }

        .message-text {
          padding: 0.75rem 1rem;
          border-radius: 12px;
          font-size: 0.875rem;
          line-height: 1.5;
          max-width: 85%;
          word-wrap: break-word;
        }

        .message-user .message-text {
          background: linear-gradient(135deg, #E49B0F 0%, #F5B942 100%);
          color: #000000;
          border-bottom-right-radius: 4px;
        }

        .message-assistant .message-text {
          background: rgba(228, 155, 15, 0.1);
          border: 1px solid rgba(228, 155, 15, 0.2);
          color: #FFFFFF;
          border-bottom-left-radius: 4px;
        }

        .message-time {
          font-size: 0.75rem;
          color: #666;
          padding: 0 0.5rem;
        }

        /* Input Area */
        .chat-input-container {
          border-top: 1px solid rgba(228, 155, 15, 0.2);
          background: rgba(228, 155, 15, 0.05);
          padding: 1rem;
        }

        .chat-error-banner {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.3);
          border-radius: 8px;
          color: #EF4444;
          font-size: 0.875rem;
          margin-bottom: 0.75rem;
        }

        .chat-input-wrapper {
          display: flex;
          gap: 0.75rem;
          align-items: flex-end;
        }

        .chat-input {
          flex: 1;
          background: rgba(228, 155, 15, 0.1);
          border: 1px solid rgba(228, 155, 15, 0.3);
          border-radius: 12px;
          padding: 0.75rem 1rem;
          color: #FFFFFF;
          font-size: 0.875rem;
          font-family: inherit;
          resize: none;
          max-height: 120px;
          transition: all 0.2s;
        }

        .chat-input:focus {
          outline: none;
          border-color: #E49B0F;
          background: rgba(228, 155, 15, 0.15);
        }

        .chat-input::placeholder {
          color: rgba(255, 255, 255, 0.4);
        }

        .chat-input:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .chat-send-button {
          width: 44px;
          height: 44px;
          background: linear-gradient(135deg, #E49B0F 0%, #F5B942 100%);
          border: none;
          border-radius: 12px;
          color: #000000;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
          flex-shrink: 0;
        }

        .chat-send-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px 0 rgba(228, 155, 15, 0.6);
        }

        .chat-send-button:active:not(:disabled) {
          transform: translateY(0);
        }

        .chat-send-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .spinner {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }

        /* Mobile adjustments */
        @media (max-width: 768px) {
          .chat-modal-container {
            max-width: 100%;
            height: 100%;
            max-height: 100vh;
            border-radius: 0;
            border: none;
          }

          .chat-modal-header {
            padding: 1rem;
          }

          .header-icon {
            width: 40px;
            height: 40px;
          }

          .header-text h2 {
            font-size: 1.125rem;
          }

          .header-text p {
            font-size: 0.75rem;
          }

          .close-button {
            width: 32px;
            height: 32px;
          }

          .chat-messages {
            padding: 1rem;
          }
        }

        /* Accessibility */
        .close-button:focus-visible,
        .chat-send-button:focus-visible {
          outline: 2px solid #E49B0F;
          outline-offset: 2px;
        }
      `}</style>
    </div>
  );
}
