"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { HiArrowLeft, HiUser, HiMail, HiTag, HiExclamation, HiChatAlt2 } from "react-icons/hi";

interface Message {
  id: string;
  role: string;
  content: string;
  created_at: string;
  channel: string;
}

interface TicketDetail {
  id: string;
  ticket_number: string;
  customer_id: string;
  customer_name: string;
  customer_email: string;
  category: string;
  priority: string;
  status: string;
  source_channel: string;
  created_at: string;
  resolved_at: string | null;
  subject?: string;
}

interface TicketResponse {
  ticket: TicketDetail;
  messages: Message[];
  message_count: number;
}

export default function TicketDetailPage() {
  const params = useParams();
  const router = useRouter();
  const ticketId = params.id as string;

  const [data, setData] = useState<TicketResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTicketDetails = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/tickets/${ticketId}`);

        if (!response.ok) {
          if (response.status === 404) {
            setError("Ticket not found");
          } else {
            setError("Failed to load ticket details");
          }
          return;
        }

        const responseData = await response.json();
        setData(responseData);
      } catch (err) {
        console.error("Error fetching ticket:", err);
        setError("Failed to load ticket details");
      } finally {
        setLoading(false);
      }
    };

    if (ticketId) {
      fetchTicketDetails();
    }
  }, [ticketId]);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "open":
        return "bg-[#3B82F6]/20 text-[#3B82F6]";
      case "processing":
        return "bg-[#F59E0B]/20 text-[#F59E0B]";
      case "resolved":
        return "bg-[#10B981]/20 text-[#10B981]";
      case "escalated":
        return "bg-[#EF4444]/20 text-[#EF4444]";
      default:
        return "bg-[#64748B]/20 text-[#64748B]";
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case "high":
        return "text-[#EF4444]";
      case "medium":
        return "text-[#F59E0B]";
      case "low":
        return "text-[#10B981]";
      default:
        return "text-[#64748B]";
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0E27] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[#3B82F6] mb-4"></div>
          <p className="text-[#94A3B8]">Loading ticket details...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-[#0A0E27] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-[#EF4444]/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <HiExclamation className="w-8 h-8 text-[#EF4444]" />
          </div>
          <h2 className="text-xl font-bold text-[#F8FAFC] mb-2">{error || "Ticket not found"}</h2>
          <button
            onClick={() => router.push("/tickets")}
            className="text-[#3B82F6] hover:text-[#60A5FA] transition-colors"
          >
            ← Back to Tickets
          </button>
        </div>
      </div>
    );
  }

  const { ticket, messages } = data;

  return (
    <div className="min-h-screen bg-[#0A0E27] relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-[800px] h-[800px] bg-[#2563EB]/10 rounded-full blur-3xl -top-96 -right-96 animate-pulse-glow" />
        <div className="absolute w-[600px] h-[600px] bg-[#3B82F6]/10 rounded-full blur-3xl -bottom-96 -left-96 animate-pulse-glow" />
      </div>

      <div className="container mx-auto px-4 py-8 relative z-10">
        {/* Back Button - Positioned lower to avoid logo overlap */}
        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          onClick={() => router.push("/dashboard")}
          className="flex items-center gap-2 text-[#94A3B8] hover:text-[#F8FAFC] transition-colors mb-6 mt-16"
        >
          <HiArrowLeft className="w-5 h-5" />
          Back to Tickets
        </motion.button>

        {/* Ticket Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 rounded-2xl mb-6"
        >
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
            <div>
              <h1 className="text-2xl font-bold text-[#F8FAFC] mb-2">
                Ticket {ticket.ticket_number}
              </h1>
              <div className="flex items-center gap-3 flex-wrap">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(ticket.status)}`}>
                  {ticket.status.toUpperCase()}
                </span>
                <span className={`flex items-center gap-1 text-sm font-semibold ${getPriorityColor(ticket.priority)}`}>
                  <HiExclamation className="w-4 h-4" />
                  {ticket.priority.toUpperCase()} Priority
                </span>
              </div>
            </div>
            <div className="text-right">
              <p className="text-[#64748B] text-sm mb-1">Created</p>
              <p className="text-[#F8FAFC] text-sm font-medium">{formatDate(ticket.created_at)}</p>
              {ticket.resolved_at && (
                <>
                  <p className="text-[#64748B] text-sm mt-2 mb-1">Resolved</p>
                  <p className="text-[#10B981] text-sm font-medium">{formatDate(ticket.resolved_at)}</p>
                </>
              )}
            </div>
          </div>

          {/* Subject Section */}
          {ticket.subject && ticket.subject !== "No subject" && (
            <div className="mt-4 pt-4 border-t border-white/10">
              <p className="text-[#64748B] text-sm mb-2">Subject</p>
              <p className="text-[#F8FAFC] text-base">{ticket.subject}</p>
            </div>
          )}
        </motion.div>

        {/* Ticket Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Customer Information */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card p-6 rounded-2xl"
          >
            <h2 className="text-lg font-bold text-[#F8FAFC] mb-4 flex items-center gap-2">
              <HiUser className="w-5 h-5 text-[#3B82F6]" />
              Customer Information
            </h2>
            <div className="space-y-3">
              <div>
                <p className="text-[#64748B] text-sm mb-1">Name</p>
                <p className="text-[#F8FAFC] font-medium">{ticket.customer_name}</p>
              </div>
              <div>
                <p className="text-[#64748B] text-sm mb-1 flex items-center gap-1">
                  <HiMail className="w-4 h-4" />
                  Email
                </p>
                <p className="text-[#F8FAFC] font-medium">{ticket.customer_email}</p>
              </div>
              <div>
                <p className="text-[#64748B] text-sm mb-1">Customer ID</p>
                <p className="text-[#94A3B8] text-sm font-mono">{ticket.customer_id}</p>
              </div>
            </div>
          </motion.div>

          {/* Ticket Information */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-card p-6 rounded-2xl"
          >
            <h2 className="text-lg font-bold text-[#F8FAFC] mb-4 flex items-center gap-2">
              <HiTag className="w-5 h-5 text-[#3B82F6]" />
              Ticket Information
            </h2>
            <div className="space-y-3">
              <div>
                <p className="text-[#64748B] text-sm mb-1">Category</p>
                <p className="text-[#F8FAFC] font-medium capitalize">{ticket.category}</p>
              </div>
              <div>
                <p className="text-[#64748B] text-sm mb-1">Source Channel</p>
                <p className="text-[#F8FAFC] font-medium capitalize">{ticket.source_channel.replace("_", " ")}</p>
              </div>
              <div>
                <p className="text-[#64748B] text-sm mb-1">Ticket ID</p>
                <p className="text-[#94A3B8] text-sm font-mono">{ticket.id}</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Conversation Messages */}
        {messages.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass-card p-6 rounded-2xl mb-6"
          >
            <h2 className="text-lg font-bold text-[#F8FAFC] mb-4 flex items-center gap-2">
              <HiChatAlt2 className="w-5 h-5 text-[#3B82F6]" />
              Conversation History ({messages.length} messages)
            </h2>
            <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
              {messages.map((message, index) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, x: message.role === "customer" ? -20 : 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + index * 0.05 }}
                  className={`flex ${message.role === "customer" ? "justify-start" : "justify-end"}`}
                >
                  <div
                    className={`max-w-[80%] p-4 rounded-lg ${
                      message.role === "customer"
                        ? "bg-[#1E293B] border border-white/10"
                        : message.role === "agent"
                        ? "bg-gradient-to-r from-[#2563EB] to-[#3B82F6]"
                        : "bg-[#F59E0B]/20 border border-[#F59E0B]/30"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span
                        className={`text-xs font-semibold ${
                          message.role === "customer"
                            ? "text-[#94A3B8]"
                            : message.role === "agent"
                            ? "text-white"
                            : "text-[#F59E0B]"
                        }`}
                      >
                        {message.role === "customer"
                          ? "Customer"
                          : message.role === "agent"
                          ? "AI Agent"
                          : "Human Support"}
                      </span>
                      <span
                        className={`text-xs ${
                          message.role === "customer"
                            ? "text-[#64748B]"
                            : message.role === "agent"
                            ? "text-blue-200"
                            : "text-[#F59E0B]/70"
                        }`}
                      >
                        {new Date(message.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p
                      className={`text-sm ${
                        message.role === "customer"
                          ? "text-[#CBD5E1]"
                          : message.role === "agent"
                          ? "text-white"
                          : "text-[#F8FAFC]"
                      }`}
                    >
                      {message.content}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Escalation Notice */}
            {ticket.status === "escalated" && (
              <div className="mt-4 p-4 bg-[#F59E0B]/10 border border-[#F59E0B]/30 rounded-lg">
                <p className="text-sm text-[#F59E0B] flex items-center gap-2">
                  <HiExclamation className="w-5 h-5" />
                  <span>
                    <strong>Escalated to Human Support</strong> - A specialist will respond soon
                  </span>
                </p>
              </div>
            )}
          </motion.div>
        )}

        {/* No Messages */}
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass-card p-8 rounded-2xl mb-6 text-center"
          >
            <HiChatAlt2 className="w-12 h-12 text-[#64748B] mx-auto mb-3" />
            <p className="text-[#94A3B8]">No conversation messages found for this ticket</p>
          </motion.div>
        )}

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="flex gap-4"
        >
          <button
            onClick={() => router.push(`/tickets?q=${ticket.customer_email}`)}
            className="px-6 py-3 bg-gradient-to-r from-[#2563EB] to-[#3B82F6] text-white font-semibold rounded-lg hover:shadow-lg hover:shadow-[#3B82F6]/30 transition-all"
          >
            View Customer History
          </button>
          <button
            onClick={() => router.push("/support")}
            className="px-6 py-3 bg-[#1E293B] text-[#F8FAFC] font-semibold rounded-lg border border-white/10 hover:bg-[#334155] transition-all"
          >
            Create New Ticket
          </button>
        </motion.div>
      </div>
    </div>
  );
}
