"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { HiSearch, HiTicket, HiClock, HiCheckCircle, HiExclamationCircle } from "react-icons/hi";
import authClient from "@/lib/auth-client";
import AuthGate from "@/components/AuthGate";
import { getBackendURL } from "@/lib/config";

interface Ticket {
  id: string;
  ticket_number: string;
  subject: string;
  category: string;
  priority: string;
  status: string;
  created_at: string;
  customer_name: string;
  customer_email: string;
}

export default function TicketsPage() {
  const router = useRouter();
  const { data: session, isPending } = authClient.useSession();
  const [searchQuery, setSearchQuery] = useState("");
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  // Check authentication
  if (isPending) {
    return (
      <div className="min-h-screen bg-[#0A0E27] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[#3B82F6]"></div>
          <p className="text-[#94A3B8] mt-4">Loading...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <AuthGate
        title="Sign Up to Track Your Tickets"
        description="Create a free account to manage and track all your support tickets in one place."
        features={[
          {
            title: "Track All Tickets",
            description: "View and manage all your support requests from one dashboard"
          },
          {
            title: "Detailed History",
            description: "Access complete ticket history and conversation logs"
          },
          {
            title: "Real-Time Updates",
            description: "Get instant notifications when ticket status changes"
          },
          {
            title: "Anytime Access",
            description: "Check your tickets from anywhere, on any device"
          },
          {
            title: "Priority Support",
            description: "Receive faster responses and dedicated assistance"
          },
          {
            title: "Export Reports",
            description: "Download ticket reports and conversation transcripts"
          },
        ]}
      />
    );
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setError("Please enter a ticket ID or email address");
      return;
    }

    setIsLoading(true);
    setError("");
    setTickets([]);

    try {
      const backendURL = getBackendURL();
      const response = await fetch(
        `${backendURL}/api/v1/tickets/search?q=${encodeURIComponent(searchQuery)}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch tickets");
      }

      const data = await response.json();
      setTickets(data.tickets || []);

      if (data.tickets.length === 0) {
        setError("No tickets found. Please check your ticket ID or email address.");
      }
    } catch (err) {
      console.error("Search error:", err);
      setError("Failed to search tickets. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "open":
        return <HiClock className="w-5 h-5 text-[#F59E0B]" />;
      case "in_progress":
        return <HiExclamationCircle className="w-5 h-5 text-[#3B82F6]" />;
      case "resolved":
        return <HiCheckCircle className="w-5 h-5 text-[#10B981]" />;
      case "closed":
        return <HiCheckCircle className="w-5 h-5 text-[#64748B]" />;
      default:
        return <HiTicket className="w-5 h-5 text-[#94A3B8]" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "open":
        return "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30";
      case "in_progress":
        return "bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/30";
      case "resolved":
        return "bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30";
      case "closed":
        return "bg-[#64748B]/10 text-[#64748B] border-[#64748B]/30";
      default:
        return "bg-[#94A3B8]/10 text-[#94A3B8] border-[#94A3B8]/30";
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case "low":
        return "text-[#10B981]";
      case "medium":
        return "text-[#F59E0B]";
      case "high":
        return "text-[#F97316]";
      case "urgent":
        return "text-[#EF4444]";
      default:
        return "text-[#94A3B8]";
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0E27]">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-[600px] h-[600px] bg-[#2563EB]/10 rounded-full blur-3xl top-0 right-0" />
        <div className="absolute w-[500px] h-[500px] bg-[#3B82F6]/10 rounded-full blur-3xl bottom-0 left-0" />
      </div>

      <div className="container mx-auto px-4 py-24 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 glass rounded-full mb-6">
            <HiTicket className="w-5 h-5 text-[#3B82F6]" />
            <span className="text-sm text-[#CBD5E1]">Track Your Support Request</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="gradient-text">Check Ticket Status</span>
          </h1>
          <p className="text-xl text-[#94A3B8] max-w-2xl mx-auto">
            Enter your ticket ID or email address to view your support requests
          </p>
        </motion.div>

        {/* Search Box */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="max-w-2xl mx-auto mb-12"
        >
          <div className="glass-card p-6">
            <div className="flex gap-3">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                placeholder="Enter ticket ID (e.g., TKT-12345) or email address"
                className="flex-1 input-field"
                disabled={isLoading}
              />
              <button
                onClick={handleSearch}
                disabled={isLoading}
                className="btn-primary px-8 flex items-center gap-2"
              >
                <HiSearch className="w-5 h-5" />
                {isLoading ? "Searching..." : "Search"}
              </button>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 p-4 bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-lg text-[#F87171] text-sm flex items-start gap-2"
              >
                <HiExclamationCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Tickets List */}
        {tickets.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="max-w-4xl mx-auto"
          >
            <h2 className="text-2xl font-bold text-[#F8FAFC] mb-6 flex items-center gap-2">
              <HiTicket className="w-6 h-6 text-[#3B82F6]" />
              Your Tickets ({tickets.length})
            </h2>

            <div className="space-y-4">
              {tickets.map((ticket, index) => (
                <motion.div
                  key={ticket.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  className="glass-card p-6 hover:border-[#3B82F6]/50 transition-all cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(ticket.status)}
                      <div>
                        <h3 className="text-lg font-semibold text-[#F8FAFC]">
                          {ticket.subject}
                        </h3>
                        <p className="text-sm text-[#94A3B8]">
                          Ticket #{ticket.ticket_number}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(
                        ticket.status
                      )}`}
                    >
                      {ticket.status.replace("_", " ").toUpperCase()}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-[#64748B]">Category</span>
                      <p className="text-[#CBD5E1] font-medium capitalize">
                        {ticket.category}
                      </p>
                    </div>
                    <div>
                      <span className="text-[#64748B]">Priority</span>
                      <p className={`font-medium capitalize ${getPriorityColor(ticket.priority)}`}>
                        {ticket.priority}
                      </p>
                    </div>
                    <div>
                      <span className="text-[#64748B]">Created</span>
                      <p className="text-[#CBD5E1] font-medium">
                        {new Date(ticket.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <span className="text-[#64748B]">Customer</span>
                      <p className="text-[#CBD5E1] font-medium">{ticket.customer_name}</p>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-white/10">
                    <button
                      onClick={() => router.push(`/tickets/${ticket.id}`)}
                      className="text-[#3B82F6] hover:text-[#60A5FA] text-sm font-medium flex items-center gap-2 transition-colors"
                    >
                      View Details
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Empty State */}
        {!isLoading && tickets.length === 0 && !error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="max-w-md mx-auto text-center"
          >
            <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-[#2563EB] to-[#3B82F6] flex items-center justify-center">
              <HiTicket className="w-12 h-12 text-white" />
            </div>
            <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">
              Search for Your Tickets
            </h3>
            <p className="text-[#94A3B8] mb-6">
              Enter your ticket ID or email address above to view your support requests
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
