"use client";

import { motion } from "framer-motion";
import { HiChip } from "react-icons/hi";

interface TypingIndicatorProps {
  status?: string;
}

export default function TypingIndicator({ status }: TypingIndicatorProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-start gap-3 mb-4"
    >
      {/* Avatar */}
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-[#10B981] to-[#34D399] flex items-center justify-center shadow-lg">
        <HiChip className="w-5 h-5 text-white" />
      </div>

      {/* Typing Animation */}
      <div className="glass px-4 py-3 rounded-2xl rounded-bl-sm">
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              <motion.div
                className="w-2 h-2 bg-[#3B82F6] rounded-full"
                animate={{ y: [0, -8, 0] }}
                transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
              />
              <motion.div
                className="w-2 h-2 bg-[#3B82F6] rounded-full"
                animate={{ y: [0, -8, 0] }}
                transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
              />
              <motion.div
                className="w-2 h-2 bg-[#3B82F6] rounded-full"
                animate={{ y: [0, -8, 0] }}
                transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
              />
            </div>
            <span className="text-xs text-[#94A3B8] font-medium">AI is thinking...</span>
          </div>
          {status && (
            <span className="text-xs text-[#64748B] italic">{status}</span>
          )}
        </div>
      </div>
    </motion.div>
  );
}
