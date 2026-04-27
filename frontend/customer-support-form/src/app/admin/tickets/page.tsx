"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  HiTicket,
  HiSearch,
  HiFilter,
  HiChevronRight,
} from "react-icons/hi";
import { getBackendURL } from "@/lib/config";

interface Ticket {
  id: string;
  ticket_number: string;
  customer_name: string;
  customer_email: string;
  category: string;
  priority: string;
  status: string;
  source_channel: string;
  escalation_reason: string;
  created_at: string;
  escalated_at: string;
}

export default function AdminTicketsPage() {
  const router = useRouter();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [channelFilter, setChannelFilter] = useState("");

  useEffect(() => {
    checkAuth();
    fetchTickets();
  }, [statusFilter, channelFilter]);

  const checkAuth = async () => {
    try {
      const backendURL = getBackendURL();
      const response = await fetch(
        `${backendURL}/api/v1/admin/auth/me`,
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

  const fetchTickets = async () => {
    setIsLoading(true);
    setError("");

    try {
      const backendURL = getBackendURL();
      let url = `${backendURL}/api/v1/admin/tickets/list?limit=50`;

      if (statusFilter) {
        url += `&status=${statusFilter}`;
      }

      if (channelFilter) {
        url += `&channel=${channelFilter}`;
      }

      const response = await fetch(url, {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to fetch tickets");
      }

      const data = await response.json();
      setTickets(data);
    } catch (err: any) {
      console.error("Fetch tickets error:", err);
      setError(err.message || "Failed to load tickets");
    } finally {
      setIsLoading(false);
    }
  };

  const filteredTickets = tickets.filter((ticket) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      ticket.ticket_number.toLowerCase().includes(query) ||
      ticket.customer_name.toLowerCase().includes(query) ||
      ticket.customer_email.toLowerCase().includes(query) ||
      ticket.escalation_reason.toLowerCase().includes(query)
    );
  });

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
    switch (priority.toLowerCase()) {
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
    switch (status.toLowerCase()) {
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
          <div>
            <h1 className="text-3xl font-bold gradient-text">Escalated Tickets</h1>
            <p className="text-[#94A3B8] mt-1">
              Manage customer escalations requiring human attention
            </p>
          </div>

          <a
            href="/admin/dashboard"
            className="text-[#3B82F6] hover:text-[#60A5FA] text-sm font-medium"
          >
            ← Back to Dashboard
          </a>
        </div>

        {/* Filters */}
        <div className="glass-card p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search tickets..."
                className="input-field"
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-field"
            >
              <option value="">All Statuses</option>
              <option value="escalated">Escalated</option>
              <option value="processing">Processing</option>
              <option value="resolved">Resolved</option>
            </select>

            {/* Channel Filter */}
            <select
              value={channelFilter}
              onChange={(e) => setChannelFilter(e.target.value)}
              className="input-field"
            >
              <option value="">All Channels</option>
              <option value="email">Email</option>
              <option value="whatsapp">WhatsApp</option>
              <option value="web_form">Web Form</option>
            </select>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[#3B82F6]"></div>
            <p className="text-[#94A3B8] mt-4">Loading tickets...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="glass-card p-6 mb-6 border-[#EF4444]/30">
            <p className="text-[#EF4444]">{error}</p>
            <button
              onClick={fetchTickets}
              className="mt-4 btn-primary text-sm"
            >
              Retry
            </button>
          </div>
        )}

        {/* Tickets List */}
        {!isLoading && !error && (
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-[#F8FAFC]">
                {filteredTickets.length} Ticket{filteredTickets.length !== 1 ? "s" : ""}
              </h2>
            </div>

            {filteredTickets.length === 0 ? (
              <div className="text-center py-12">
                <HiTicket className="w-16 h-16 mx-auto mb-4 text-[#64748B]" />
                <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">
                  No Tickets Found
                </h3>
                <p className="text-[#94A3B8]">
                  {searchQuery || statusFilter || channelFilter
                    ? "Try adjusting your filters"
                    : "No escalated tickets at the moment"}
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredTickets.map((ticket, index) => (
                  <motion.div
                    key={ticket.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.05 }}
                    className="p-4 bg-[#1E293B]/50 rounded-lg border border-white/5 hover:border-[#3B82F6]/30 transition-all cursor-pointer group"
                    onClick={() => router.push(`/admin/tickets/${ticket.id}`)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 flex-1">
                        <div className="text-2xl">
                          {getChannelIcon(ticket.source_channel)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-1">
                            <span className="text-sm font-medium text-[#F8FAFC]">
                              {ticket.ticket_number}
                            </span>
                            <span
                              className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(
                                ticket.status
                              )}`}
                            >
                              {ticket.status.toUpperCase()}
                            </span>
                            <span className={`text-xs font-medium ${getPriorityColor(ticket.priority)}`}>
                              {ticket.priority.toUpperCase()}
                            </span>
                          </div>
                          <h3 className="text-[#F8FAFC] font-medium mb-1">
                            {ticket.customer_name}
                          </h3>
                          <p className="text-sm text-[#94A3B8] mb-1">
                            {ticket.escalation_reason}
                          </p>
                          <div className="flex items-center gap-3 text-xs text-[#64748B]">
                            <span>{ticket.customer_email}</span>
                            <span>•</span>
                            <span className="capitalize">{ticket.category}</span>
                            <span>•</span>
                            <span>
                              {new Date(ticket.escalated_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      </div>
                      <HiChevronRight className="w-5 h-5 text-[#94A3B8] group-hover:text-[#3B82F6] group-hover:translate-x-1 transition-all" />
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
