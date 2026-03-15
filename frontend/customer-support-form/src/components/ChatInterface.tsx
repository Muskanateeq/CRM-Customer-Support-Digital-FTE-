"use client";

import { useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import { HiChip } from "react-icons/hi";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  conversationId: string | null;
  customerName: string;
  isLoading: boolean;
  thinkingStatus?: string;
  agentMode?: string | null;
  messages: Message[];
  streamingMessage?: string;
}

export default function ChatInterface({
  conversationId,
  customerName,
  isLoading,
  thinkingStatus,
  agentMode,
  messages,
  streamingMessage,
}: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, streamingMessage]);

  return (
    <motion.div
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6 }}
      className="flex flex-col h-full glass-card overflow-hidden"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-[#2563EB] to-[#3B82F6] px-6 py-4 border-b border-white/10">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <HiChip className="w-5 h-5" />
              AI Assistant
            </h2>
            {conversationId && (
              <p className="text-sm text-blue-100 mt-1">
                Chatting with {customerName}
              </p>
            )}
          </div>
          <div className="flex items-center gap-2">
            {/* Online Status */}
            <div className="flex items-center gap-2 px-3 py-1.5 bg-white/10 rounded-full">
              <span className="w-2 h-2 bg-[#10B981] rounded-full animate-pulse-glow"></span>
              <span className="text-xs text-white font-medium">Online</span>
            </div>
            {/* Agent Mode Badge */}
            {agentMode && (
              <div className="text-xs bg-white/10 px-3 py-1.5 rounded-full text-white font-medium">
                {agentMode}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-[#0F172A]/50">
        {messages.length === 0 && !isLoading && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center mt-12"
          >
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-[#2563EB] to-[#3B82F6] flex items-center justify-center">
              <HiChip className="w-10 h-10 text-white" />
            </div>
            <p className="text-lg text-[#CBD5E1] mb-2">👋 Welcome to Custora Support!</p>
            <p className="text-sm text-[#94A3B8]">
              Submit the form to start chatting with our AI assistant.
            </p>
          </motion.div>
        )}

        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              <MessageBubble
                role={message.role}
                content={message.content}
                timestamp={message.timestamp}
              />
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Streaming Message - Show in real-time */}
        {streamingMessage && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <MessageBubble
              key="streaming"
              role="assistant"
              content={streamingMessage}
              timestamp={new Date()}
            />
          </motion.div>
        )}

        {/* Typing Indicator - Show only when loading but no streaming text yet */}
        {isLoading && !streamingMessage && <TypingIndicator status={thinkingStatus} />}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area - Replaced with View Tickets Button */}
      <div className="border-t border-white/10 p-4 bg-[#1E293B]/50">
        {conversationId ? (
          <div className="space-y-3">
            <p className="text-center text-[#94A3B8] text-sm">
              Need to submit another query? Use the form on the left.
            </p>
            <a
              href="/tickets"
              className="block w-full px-6 py-3 bg-gradient-to-r from-[#2563EB] to-[#3B82F6] text-white rounded-lg font-semibold hover:shadow-lg hover:shadow-[#2563EB]/50 transition-all text-center"
            >
              View All Tickets
            </a>
          </div>
        ) : (
          <p className="text-center text-[#94A3B8] text-sm">
            Submit the form to start chatting
          </p>
        )}

        {/* Response Time Indicator */}
        {conversationId && (
          <div className="mt-3 flex items-center justify-center gap-2 text-xs text-[#64748B]">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
            </svg>
            <span>Average response time: &lt;2 seconds</span>
          </div>
        )}
      </div>
    </motion.div>
  );
}
