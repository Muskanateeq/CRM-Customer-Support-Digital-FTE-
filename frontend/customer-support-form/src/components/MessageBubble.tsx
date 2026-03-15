"use client";

import { motion } from "framer-motion";
import { HiUser, HiChip } from "react-icons/hi";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: Date;
}

export default function MessageBubble({ role, content, timestamp }: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
    >
      <div className={`flex items-start gap-3 max-w-[85%] ${isUser ? "flex-row-reverse" : ""}`}>
        {/* Avatar */}
        <div
          className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
            isUser
              ? "bg-gradient-to-br from-[#2563EB] to-[#3B82F6]"
              : "bg-gradient-to-br from-[#10B981] to-[#34D399]"
          } shadow-lg`}
        >
          {isUser ? (
            <HiUser className="w-5 h-5 text-white" />
          ) : (
            <HiChip className="w-5 h-5 text-white" />
          )}
        </div>

        {/* Message Content */}
        <div className="flex flex-col">
          <div
            className={`px-4 py-3 rounded-2xl ${
              isUser
                ? "bg-gradient-to-br from-[#2563EB] to-[#3B82F6] text-white rounded-br-sm shadow-lg shadow-[#2563EB]/30"
                : "glass text-[#F8FAFC] rounded-bl-sm"
            }`}
          >
            <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">{content}</p>
          </div>

          {/* Timestamp */}
          {timestamp && (
            <span
              className={`text-xs text-[#64748B] mt-1.5 flex items-center gap-1 ${
                isUser ? "justify-end" : "justify-start"
              }`}
            >
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                  clipRule="evenodd"
                />
              </svg>
              {timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
}
