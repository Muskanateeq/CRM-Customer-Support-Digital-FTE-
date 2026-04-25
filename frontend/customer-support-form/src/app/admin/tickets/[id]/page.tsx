"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  HiArrowLeft,
  HiUser,
  HiMail,
  HiPhone,
  HiClock,
  HiCheckCircle,
  HiPaperAirplane,
} from "react-icons/hi";

interface Message {
  id: string;
  role: string;
  content: string;
  channel: string;
  direction: string;
  created_at: string;
}

interface TicketDetail {
  ticket: {
    id: string;
    ticket_number: string;
    customer_name: string;
    customer_email: string;
    customer_phone: string;
    category: string;
    priority: string;
    status: string;
    source_channel: string;
    escalation_reason: string;
    created_at: string;
    escalated_at: string;
  };
  messages: Message[];
  responses: any[];
  notes: any[];
}

export default function AdminTicketDetailPage() {
  const router = useRouter();
  const params = useParams();
  const ticketId = params.id as string;

  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [responseContent, setResponseContent] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [sendSuccess, setSendSuccess] = useState(false);

  useEffect(() => {
    checkAuth();
    fetchTicketDetail();
  }, [ticketId]);

  const checkAuth = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/admin/auth/me`,
        {
          credentials: "include",
        }
      );

      if (!response.ok) {
        router.push("/admin/login");
      }
    } catch (err) {
      console.error("Auth check failed:", err);
      router.push("/admin/login");
    }
  };

  const fetchTicketDetail = async () => {
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/admin/tickets/${ticketId}`,
        {
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch ticket details");
      }

      const data = await response.json();
      setTicket(data);
    } catch (err: any) {
      console.error("Fetch ticket error:", err);
      setError(err.message || "Failed to load ticket details");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendResponse = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!responseContent.trim()) {
      return;
    }

    setIsSending(true);
    setSendSuccess(false);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/admin/tickets/${ticketId}/respond`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            content: responseContent,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to send response");
      }

      setSendSuccess(true);
      setResponseContent("");

      // Refresh ticket details
      setTimeout(() => {
        fetchTicketDetail();
        setSendSuccess(false);
      }, 2000);
    } catch (err: any) {
      console.error("Send response error:", err);
      alert(err.message || "Failed to send response");
    } finally {
      setIsSending(false);
    }
  };

  const handleUpdateStatus = async (newStatus: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/admin/tickets/${ticketId}/status`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            status: newStatus,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to update status");
      }

      // Refresh ticket details
      fetchTicketDetail();
    } catch (err: any) {
      console.error("Update status error:", err);
      alert(err.message || "Failed to update status");
    }
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case "email":
        return "📧";
      case "whatsapp":
        return "💬";
      case "web_form":
        return "🌐";
      default:
        return "📋";
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case "urgent":
        return "text-[#EF4444]";
      case "high":
        return "text-[#F97316]";
      case "medium":
        return "text-[#F59E0B]";
      default:
        return "text-[#10B981]";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case "escalated":
        return "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/30";
      case "processing":
        return "bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/30";
      case "resolved":
        return "bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30";
      default:
        return "bg-[#94A3B8]/10 text-[#94A3B8] border-[#94A3B8]/30";
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0A0E27] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[#3B82F6]"></div>
          <p className="text-[#94A3B8] mt-4">Loading ticket...</p>
        </div>
      </div>
    );
  }

  if (error || !ticket) {
    return (
      <div className="min-h-screen bg-[#0A0E27] flex items-center justify-center">
        <div className="glass-card p-8 max-w-md">
          <p className="text-[#EF4444] mb-4">{error || "Ticket not found"}</p>
          <button
            onClick={() => router.push("/admin/tickets")}
            className="btn-primary"
          >
            Back to Tickets
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0A0E27]">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-[600px] h-[600px] bg-[#2563EB]/10 rounded-full blur-3xl top-0 right-0" />
        <div className="absolute w-[500px] h-[500px] bg-[#3B82F6]/10 rounded-full blur-3xl bottom-0 left-0" />
      </div>

      <div className="container mx-auto px-4 pt-24 pb-8 relative z-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push("/admin/tickets")}
              className="p-2 hover:bg-white/5 rounded-lg transition-colors"
            >
              <HiArrowLeft className="w-6 h-6 text-[#94A3B8]" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-[#F8FAFC]">
                {getChannelIcon(ticket.ticket.source_channel)}{" "}
                {ticket.ticket.ticket_number}
              </h1>
              <p className="text-[#94A3B8] text-sm">
                Escalated {new Date(ticket.ticket.escalated_at).toLocaleString()}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(
                ticket.ticket.status
              )}`}
            >
              {ticket.ticket.status.toUpperCase()}
            </span>
            <span className={`text-sm font-medium ${getPriorityColor(ticket.ticket.priority)}`}>
              {ticket.ticket.priority.toUpperCase()} PRIORITY
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Conversation */}
          <div className="lg:col-span-2 space-y-6">
            {/* Customer Info */}
            <div className="glass-card p-6">
              <h2 className="text-lg font-bold text-[#F8FAFC] mb-4">
                Customer Information
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center gap-3">
                  <HiUser className="w-5 h-5 text-[#3B82F6]" />
                  <div>
                    <p className="text-xs text-[#64748B]">Name</p>
                    <p className="text-[#F8FAFC] font-medium">
                      {ticket.ticket.customer_name}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <HiMail className="w-5 h-5 text-[#3B82F6]" />
                  <div>
                    <p className="text-xs text-[#64748B]">Email</p>
                    <p className="text-[#F8FAFC] font-medium">
                      {ticket.ticket.customer_email}
                    </p>
                  </div>
                </div>
                {ticket.ticket.customer_phone && (
                  <div className="flex items-center gap-3">
                    <HiPhone className="w-5 h-5 text-[#3B82F6]" />
                    <div>
                      <p className="text-xs text-[#64748B]">Phone</p>
                      <p className="text-[#F8FAFC] font-medium">
                        {ticket.ticket.customer_phone}
                      </p>
                    </div>
                  </div>
                )}
                <div className="flex items-center gap-3">
                  <HiClock className="w-5 h-5 text-[#3B82F6]" />
                  <div>
                    <p className="text-xs text-[#64748B]">Category</p>
                    <p className="text-[#F8FAFC] font-medium capitalize">
                      {ticket.ticket.category}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Escalation Reason */}
            <div className="glass-card p-6">
              <h2 className="text-lg font-bold text-[#F8FAFC] mb-3">
                Escalation Reason
              </h2>
              <p className="text-[#94A3B8]">{ticket.ticket.escalation_reason}</p>
            </div>

            {/* Conversation History */}
            <div className="glass-card p-6">
              <h2 className="text-lg font-bold text-[#F8FAFC] mb-4">
                Conversation History
              </h2>
              <div className="space-y-4 max-h-[500px] overflow-y-auto">
                {ticket.messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.role === "customer" ? "justify-start" : "justify-end"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] p-4 rounded-lg ${
                        message.role === "customer"
                          ? "bg-[#1E293B] border border-white/10"
                          : message.role === "agent"
                          ? "bg-[#3B82F6]/20 border border-[#3B82F6]/30"
                          : "bg-[#F59E0B]/20 border border-[#F59E0B]/30"
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-medium text-[#CBD5E1]">
                          {message.role === "customer"
                            ? "Customer"
                            : message.role === "agent"
                            ? "AI Agent"
                            : "System"}
                        </span>
                        <span className="text-xs text-[#64748B]">
                          {new Date(message.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-[#F8FAFC] whitespace-pre-wrap">
                        {message.content}
                      </p>
                    </div>
                  </div>
                ))}

                {/* Human Responses */}
                {ticket.responses.map((response) => (
                  <div key={response.id} className="flex justify-end">
                    <div className="max-w-[80%] p-4 rounded-lg bg-[#10B981]/20 border border-[#10B981]/30">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-medium text-[#10B981]">
                          You ({response.admin_name})
                        </span>
                        <span className="text-xs text-[#64748B]">
                          {new Date(response.sent_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-[#F8FAFC] whitespace-pre-wrap">
                        {response.content}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Response Form */}
            <div className="glass-card p-6">
              <h2 className="text-lg font-bold text-[#F8FAFC] mb-4">
                Send Response
              </h2>
              <form onSubmit={handleSendResponse}>
                <textarea
                  value={responseContent}
                  onChange={(e) => setResponseContent(e.target.value)}
                  placeholder="Type your response here..."
                  className="input-field min-h-[150px] mb-4"
                  disabled={isSending}
                  required
                />

                {sendSuccess && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-4 p-3 bg-[#10B981]/10 border border-[#10B981]/30 rounded-lg text-[#10B981] text-sm flex items-center gap-2"
                  >
                    <HiCheckCircle className="w-5 h-5" />
                    Response sent successfully via {ticket.ticket.source_channel}!
                  </motion.div>
                )}

                <button
                  type="submit"
                  disabled={isSending || !responseContent.trim()}
                  className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <HiPaperAirplane className="w-5 h-5" />
                  {isSending ? "Sending..." : "Send Response"}
                </button>
              </form>
            </div>
          </div>

          {/* Right Column - Actions */}
          <div className="space-y-6">
            {/* Status Management */}
            <div className="glass-card p-6">
              <h2 className="text-lg font-bold text-[#F8FAFC] mb-4">
                Update Status
              </h2>
              <div className="space-y-2">
                <button
                  onClick={() => handleUpdateStatus("processing")}
                  disabled={ticket.ticket.status === "processing"}
                  className="w-full px-4 py-2 bg-[#3B82F6]/10 hover:bg-[#3B82F6]/20 border border-[#3B82F6]/30 rounded-lg text-[#3B82F6] font-medium transition-all disabled:opacity-50"
                >
                  Mark as Processing
                </button>
                <button
                  onClick={() => handleUpdateStatus("resolved")}
                  disabled={ticket.ticket.status === "resolved"}
                  className="w-full px-4 py-2 bg-[#10B981]/10 hover:bg-[#10B981]/20 border border-[#10B981]/30 rounded-lg text-[#10B981] font-medium transition-all disabled:opacity-50"
                >
                  Mark as Resolved
                </button>
              </div>
            </div>

            {/* Ticket Info */}
            <div className="glass-card p-6">
              <h2 className="text-lg font-bold text-[#F8FAFC] mb-4">
                Ticket Details
              </h2>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-[#64748B]">Channel</p>
                  <p className="text-[#F8FAFC] font-medium capitalize">
                    {getChannelIcon(ticket.ticket.source_channel)}{" "}
                    {ticket.ticket.source_channel.replace("_", " ")}
                  </p>
                </div>
                <div>
                  <p className="text-[#64748B]">Created</p>
                  <p className="text-[#F8FAFC] font-medium">
                    {new Date(ticket.ticket.created_at).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-[#64748B]">Messages</p>
                  <p className="text-[#F8FAFC] font-medium">
                    {ticket.messages.length}
                  </p>
                </div>
                <div>
                  <p className="text-[#64748B]">Your Responses</p>
                  <p className="text-[#F8FAFC] font-medium">
                    {ticket.responses.length}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
