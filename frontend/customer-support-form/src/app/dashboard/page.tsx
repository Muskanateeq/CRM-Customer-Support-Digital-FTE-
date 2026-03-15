"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { HiTicket, HiClock, HiCheckCircle, HiChartBar, HiUser, HiMail } from "react-icons/hi";

interface DashboardStats {
  total_tickets: number;
  open_tickets: number;
  resolved_tickets: number;
  avg_response_time: string;
  total_customers: number;
  total_conversations: number;
}

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

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentTickets, setRecentTickets] = useState<Ticket[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError("");

    try {
      // Fetch dashboard stats
      const statsResponse = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/tickets/dashboard/stats`
      );

      if (!statsResponse.ok) {
        throw new Error("Failed to fetch dashboard stats");
      }

      const statsData = await statsResponse.json();
      setStats(statsData);

      // Fetch recent tickets
      const ticketsResponse = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/tickets/dashboard/recent?limit=5`
      );

      if (!ticketsResponse.ok) {
        throw new Error("Failed to fetch recent tickets");
      }

      const ticketsData = await ticketsResponse.json();
      setRecentTickets(ticketsData.tickets || []);

    } catch (err) {
      console.error("Dashboard fetch error:", err);
      setError("Failed to load dashboard data");
    } finally {
      setIsLoading(false);
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    return `${diffDays} days ago`;
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
          className="mb-12"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#2563EB] to-[#3B82F6] flex items-center justify-center">
              <HiUser className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl md:text-4xl font-bold gradient-text">
                My Dashboard
              </h1>
              <p className="text-[#94A3B8]">Welcome back!</p>
            </div>
          </div>
        </motion.div>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[#3B82F6]"></div>
            <p className="text-[#94A3B8] mt-4">Loading dashboard...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="glass-card p-6 mb-6 border-[#EF4444]/30">
            <p className="text-[#EF4444]">{error}</p>
            <button
              onClick={fetchDashboardData}
              className="mt-4 btn-primary text-sm"
            >
              Retry
            </button>
          </div>
        )}

        {/* Stats Grid */}
        {!isLoading && stats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12"
          >
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <HiTicket className="w-8 h-8 text-[#3B82F6]" />
                <span className="text-3xl font-bold text-gradient">{stats.total_tickets}</span>
              </div>
              <h3 className="text-[#CBD5E1] font-medium">Total Tickets</h3>
              <p className="text-xs text-[#64748B] mt-1">All time</p>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <HiClock className="w-8 h-8 text-[#F59E0B]" />
                <span className="text-3xl font-bold text-[#F59E0B]">{stats.open_tickets}</span>
              </div>
              <h3 className="text-[#CBD5E1] font-medium">Open Tickets</h3>
              <p className="text-xs text-[#64748B] mt-1">Active now</p>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <HiCheckCircle className="w-8 h-8 text-[#10B981]" />
                <span className="text-3xl font-bold text-[#10B981]">{stats.resolved_tickets}</span>
              </div>
              <h3 className="text-[#CBD5E1] font-medium">Resolved</h3>
              <p className="text-xs text-[#64748B] mt-1">Completed</p>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <HiChartBar className="w-8 h-8 text-[#3B82F6]" />
                <span className="text-2xl font-bold text-gradient">{stats.avg_response_time}</span>
              </div>
              <h3 className="text-[#CBD5E1] font-medium">Avg Response</h3>
              <p className="text-xs text-[#64748B] mt-1">Time to first reply</p>
            </div>
          </motion.div>
        )}

        {/* Recent Tickets */}
        {!isLoading && recentTickets.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="glass-card p-8"
          >
            <h2 className="text-2xl font-bold text-[#F8FAFC] mb-6 flex items-center gap-2">
              <HiTicket className="w-6 h-6 text-[#3B82F6]" />
              Recent Tickets
            </h2>

            <div className="space-y-4">
              {recentTickets.map((ticket, index) => (
                <motion.div
                  key={ticket.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: 0.5 + index * 0.1 }}
                  className="p-4 bg-[#1E293B]/50 rounded-lg border border-white/5 hover:border-[#3B82F6]/30 transition-all cursor-pointer"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-sm text-[#64748B]">#{ticket.ticket_number}</span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                            ticket.status === "open"
                              ? "bg-[#F59E0B]/10 text-[#F59E0B]"
                              : ticket.status === "resolved"
                              ? "bg-[#10B981]/10 text-[#10B981]"
                              : "bg-[#3B82F6]/10 text-[#3B82F6]"
                          }`}
                        >
                          {ticket.status.toUpperCase()}
                        </span>
                      </div>
                      <h3 className="text-[#F8FAFC] font-medium mb-2">{ticket.subject || "No subject"}</h3>
                      <div className="flex items-center gap-4 text-sm text-[#94A3B8]">
                        <span className="capitalize">{ticket.category}</span>
                        <span>•</span>
                        <span className="capitalize">{ticket.priority} priority</span>
                        <span>•</span>
                        <span>{formatTimeAgo(ticket.created_at)}</span>
                      </div>
                    </div>
                    <button
                      onClick={() => router.push(`/tickets/${ticket.id}`)}
                      className="text-[#3B82F6] hover:text-[#60A5FA] text-sm font-medium transition-colors"
                    >
                      View →
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>

            <div className="mt-6 text-center">
              <a href="/tickets" className="text-[#3B82F6] hover:text-[#60A5FA] font-medium text-sm">
                View All Tickets →
              </a>
            </div>
          </motion.div>
        )}

        {/* Empty State */}
        {!isLoading && !error && recentTickets.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card p-12 text-center"
          >
            <HiTicket className="w-16 h-16 mx-auto mb-4 text-[#64748B]" />
            <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">
              No Tickets Yet
            </h3>
            <p className="text-[#94A3B8] mb-6">
              Submit a support request to get started
            </p>
            <a href="/" className="btn-primary inline-block">
              Create Ticket
            </a>
          </motion.div>
        )}

        {/* Activity Section */}
        {!isLoading && stats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="mt-8 glass-card p-8"
          >
            <h2 className="text-2xl font-bold text-[#F8FAFC] mb-6 flex items-center gap-2">
              <HiChartBar className="w-6 h-6 text-[#3B82F6]" />
              System Stats
            </h2>

            <div className="space-y-4 text-[#94A3B8]">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-[#10B981] rounded-full"></div>
                <span>Total Customers: {stats.total_customers}</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-[#3B82F6] rounded-full"></div>
                <span>Total Conversations: {stats.total_conversations}</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-[#F59E0B] rounded-full"></div>
                <span>Average Response Time: {stats.avg_response_time}</span>
              </div>
            </div>
          </motion.div>
        )}

        {/* Quick Actions */}
        {!isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="mt-8 flex flex-wrap gap-4"
          >
            <a href="/" className="btn-primary flex items-center gap-2">
              <HiMail className="w-5 h-5" />
              New Support Request
            </a>
            <a href="/tickets" className="btn-secondary flex items-center gap-2">
              <HiTicket className="w-5 h-5" />
              View All Tickets
            </a>
          </motion.div>
        )}
      </div>
    </div>
  );
}
