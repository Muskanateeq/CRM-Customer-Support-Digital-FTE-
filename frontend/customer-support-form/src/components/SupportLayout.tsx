"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import ChatInterface from "./ChatInterface";
import SupportForm from "./SupportForm";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function SupportLayout() {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [customerName, setCustomerName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [thinkingStatus, setThinkingStatus] = useState<string | undefined>();
  const [agentMode, setAgentMode] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [streamingMessage, setStreamingMessage] = useState<string>("");

  const handleFormSubmit = async (
    email: string,
    name: string,
    subject: string,
    category: string,
    priority: string,
    message: string
  ) => {
    console.log("=== FORM SUBMIT STARTED ===");
    console.log("Email:", email, "Name:", name, "Subject:", subject, "Category:", category, "Priority:", priority);

    setCustomerName(name);
    setIsLoading(true);
    setThinkingStatus(undefined);
    setStreamingMessage("");

    // Add user message to chat
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: message,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      console.log("=== FETCHING STREAM ===");
      console.log("Backend URL:", process.env.NEXT_PUBLIC_BACKEND_URL);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/channels/webform/message/stream`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
            name,
            subject,
            category,
            priority,
            message,
            conversation_id: conversationId,
          }),
        }
      );

      console.log("=== FETCH COMPLETE ===");
      console.log("Response status:", response.status);
      console.log("Response ok:", response.ok);

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      console.log("=== GETTING READER ===");
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No response body");
      }

      console.log("=== READER OBTAINED, STARTING STREAM ===");
      let buffer = "";
      let accumulatedMessage = "";
      let currentEvent = "";

      while (true) {
        const { done, value } = await reader.read();
        console.log("=== READ CHUNK ===", "done:", done, "value length:", value?.length);
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          console.log("Processing line:", JSON.stringify(line));

          if (line.startsWith("event:")) {
            currentEvent = line.substring(6).trim();
            console.log("Found event:", currentEvent);
          } else if (line.startsWith("data:")) {
            const dataStr = line.substring(5).trim();
            if (!dataStr) continue;

            console.log("Processing data for event:", currentEvent, "data:", dataStr.substring(0, 50));

            try {
              const data = JSON.parse(dataStr);

              if (currentEvent === "start") {
                setConversationId(data.conversation_id);
              } else if (currentEvent === "mode") {
                setAgentMode(data.display || data.mode);
              } else if (currentEvent === "thinking") {
                setThinkingStatus(data.status);
              } else if (currentEvent === "text") {
                accumulatedMessage += data.content;
                setStreamingMessage(accumulatedMessage);
                console.log("TEXT EVENT:", data.content, "Accumulated:", accumulatedMessage);
              } else if (currentEvent === "done") {
                console.log("DONE EVENT - Accumulated message:", accumulatedMessage);
                if (accumulatedMessage) {
                  const assistantMessage: Message = {
                    id: Date.now().toString(),
                    role: "assistant",
                    content: accumulatedMessage,
                    timestamp: new Date(),
                  };
                  setMessages((prev) => [...prev, assistantMessage]);
                }
                setStreamingMessage("");
                setThinkingStatus(undefined);
                accumulatedMessage = "";
              } else if (currentEvent === "error") {
                throw new Error(data.error);
              }
            } catch (parseError) {
              console.error("Failed to parse SSE data:", parseError);
            }

            currentEvent = "";
          }
        }
      }
    } catch (error) {
      console.error("Streaming error:", error);
      alert("Failed to send message. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0E27] relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-[800px] h-[800px] bg-[#2563EB]/10 rounded-full blur-3xl -top-96 -right-96 animate-pulse-glow" />
        <div className="absolute w-[600px] h-[600px] bg-[#3B82F6]/10 rounded-full blur-3xl -bottom-96 -left-96 animate-pulse-glow" />
      </div>

      <div className="container mx-auto px-4 pt-24 pb-8 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
          id="support-portal"
        >
          <h1 className="text-3xl md:text-4xl font-bold mb-2">
            <span className="gradient-text">Support Portal</span>
          </h1>
          <p className="text-[#94A3B8] text-base">
            Get instant help from our AI-powered support assistant
          </p>
        </motion.div>

        {/* Split Screen Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-6xl mx-auto">
          {/* Left: Support Form (50%) */}
          <div>
            <SupportForm onSubmit={handleFormSubmit} isLoading={isLoading} />
          </div>

          {/* Right: Chat Interface (50%) */}
          <div className="h-[600px]">
            <ChatInterface
              conversationId={conversationId}
              customerName={customerName}
              isLoading={isLoading}
              thinkingStatus={thinkingStatus}
              agentMode={agentMode}
              messages={messages}
              streamingMessage={streamingMessage}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
