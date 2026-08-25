"use client";

import { motion } from "framer-motion";
import { HiUser, HiChip } from "react-icons/hi";
import type { ReactNode } from "react";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: Date;
}

const INLINE_MARKDOWN = /(\*\*.+?\*\*|\*[^*\n]+?\*|\[[^\]\n]+\]\([^)\n]+\))/g;

function renderInlineMarkdown(text: string): ReactNode[] {
  return text.split(INLINE_MARKDOWN).filter(Boolean).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index} className="font-semibold text-white">{part.slice(2, -2)}</strong>;
    }

    if (part.startsWith("*") && part.endsWith("*")) {
      return <em key={index}>{part.slice(1, -1)}</em>;
    }

    const link = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
    if (link) {
      const [, label, url] = link;
      if (url.startsWith("https://") || url.startsWith("http://")) {
        return (
          <a
            key={index}
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-300 underline underline-offset-2 hover:text-blue-200"
          >
            {label}
          </a>
        );
      }
      return <span key={index}>{label}</span>;
    }

    // Do not expose unmatched Markdown control characters in chat bubbles.
    return <span key={index}>{part.replaceAll("**", "").replaceAll("*", "")}</span>;
  });
}

function FormattedAssistantMessage({ content }: { content: string }) {
  return (
    <div className="space-y-2 text-sm leading-relaxed break-words">
      {content.split(/\r?\n/).map((rawLine, index) => {
        const line = rawLine.trim();
        if (!line) return <div key={index} className="h-1" />;

        const heading = line.match(/^#{1,6}\s+(.+)$/);
        if (heading) {
          return <p key={index} className="font-semibold text-white">{renderInlineMarkdown(heading[1])}</p>;
        }

        const bullet = line.match(/^[-*]\s+(.+)$/);
        if (bullet) {
          return (
            <div key={index} className="flex items-start gap-2 pl-1">
              <span aria-hidden="true" className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-300" />
              <p>{renderInlineMarkdown(bullet[1])}</p>
            </div>
          );
        }

        const numbered = line.match(/^(\d+)[.)]\s+(.+)$/);
        if (numbered) {
          return (
            <div key={index} className="flex items-start gap-2">
              <span className="min-w-5 font-semibold text-blue-300">{numbered[1]}.</span>
              <p>{renderInlineMarkdown(numbered[2])}</p>
            </div>
          );
        }

        return <p key={index}>{renderInlineMarkdown(line)}</p>;
      })}
    </div>
  );
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
            {isUser ? (
              <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">{content}</p>
            ) : (
              <FormattedAssistantMessage content={content} />
            )}
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
