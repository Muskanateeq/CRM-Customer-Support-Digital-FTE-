"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  HiTicket,
  HiClock,
  HiCheckCircle,
  HiChartBar,
  HiLogout,
  HiRefresh,
} from "react-icons/hi";

interface DashboardStats {
  total_escalated: number;
  open_escalated: number;
  in_progress: number;
  resolved_today: number;
  avg_response_time: string;
}

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

export default function AdminDashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentTickets, setRecentTickets] = useState<Ticket[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [adminName, setAdminName] = useState("Admin");

  useEffect(() => {
    checkAuth();
    fetchDashboardData();
  }, []);

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
        return;
      }

      const data = await response.json();
      setAdminName(data.name);
    } catch (err) {
      console.error("Auth check failed:", err);
      router.push("/admin/login");
    }
  };

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError("");

    try {
      // Fetch stats
      const statsResponse = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/admin/tickets/dashboard/stats`,
        {
          credentials: "include",
        }
      );

      if (!statsResponse.ok) {
        throw new Error("Failed to fetch stats");
      }

      const statsData = await statsResponse.json();
      setStats(statsData);

      // Fetch recent escalated tickets
      const ticketsResponse = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/admin/tickets/list?limit=5`,
        {
          credentials: "include",
        }
      );

      if (!ticketsResponse.ok) {
        throw new Error("Failed to fetch tickets");
      }

      const ticketsData = await ticketsResponse.json();
      setRecentTickets(ticketsData);
    } catch (err: any) {
      console.error("Dashboard fetch error:", err);
      setError(err.message || "Failed to load dashboard data");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/admin/auth/logout`,
        {
          method: "POST",
          credentials: "include",
        }
      );
      router.push("/admin/login");
    } catch (err) {
      console.error("Logout error:", err);
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
            <h1 className="text-3xl font-bold gradient-text">Admin Dashboard</h1>
            <p className="text-[#94A3B8] mt-1">Welcome back, {adminName}!</p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchDashboardData}
              className="flex items-center gap-2 px-4 py-2 bg-[#1E293B]/50 hover:bg-[#1E293B] border border-white/10 rounded-lg text-[#94A3B8] hover:text-[#3B82F6] transition-all"
            >
              <HiRefresh className="w-5 h-5" />
              Refresh
            </button>
          </div>
        </div>

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
            transition={{ duration: 0.6 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-12"
          >
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <HiTicket className="w-8 h-8 text-[#3B82F6]" />
                <span className="text-3xl font-bold text-gradient">
                  {stats.total_escalated}
                </span>
              </div>
              <h3 className="text-[#CBD5E1] font-medium">Total Escalated</h3>
              <p className="text-xs text-[#64748B] mt-1">All time</p>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <HiClock className="w-8 h-8 text-[#EF4444]" />
                <span className="text-3xl font-bold text-[#EF4444]">
                  {stats.open_escalated}
                </span>
              </div>
              <h3 className="text-[#CBD5E1] font-medium">Open</h3>
              <p className="text-xs text-[#64748B] mt-1">Needs attention</p>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <HiChartBar className="w-8 h-8 text-[#F59E0B]" />
                <span className="text-3xl font-bold text-[#F59E0B]">
                  {stats.in_progress}
                </span>
              </div>
              <h3 className="text-[#CBD5E1] font-medium">In Progress</h3>
              <p className="text-xs text-[#64748B] mt-1">Being handled</p>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <HiCheckCircle className="w-8 h-8 text-[#10B981]" />
                <span className="text-3xl font-bold text-[#10B981]">
                  {stats.resolved_today}
                </span>
              </div>
              <h3 className="text-[#CBD5E1] font-medium">Resolved Today</h3>
              <p className="text-xs text-[#64748B] mt-1">Completed</p>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <HiClock className="w-8 h-8 text-[#3B82F6]" />
                <span className="text-2xl font-bold text-gradient">
                  {stats.avg_response_time}
                </span>
              </div>
              <h3 className="text-[#CBD5E1] font-medium">Avg Response</h3>
              <p className="text-xs text-[#64748B] mt-1">Time to reply</p>
            </div>
          </motion.div>
        )}

        {/* Recent Escalated Tickets */}
        {!isLoading && recentTickets.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="glass-card p-8"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-[#F8FAFC]">
                Recent Escalations
              </h2>
              <a
                href="/admin/tickets"
                className="text-[#3B82F6] hover:text-[#60A5FA] text-sm font-medium"
              >
                View All →
              </a>
            </div>

            <div className="space-y-4">
              {recentTickets.map((ticket, index) => (
                <motion.div
                  key={ticket.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                  className="p-4 bg-[#1E293B]/50 rounded-lg border border-white/5 hover:border-[#3B82F6]/30 transition-all cursor-pointer"
                  onClick={() => router.push(`/admin/tickets/${ticket.id}`)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-sm text-[#64748B]">
                          {getChannelIcon(ticket.source_channel)}{" "}
                          {ticket.ticket_number}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(
                            ticket.status
                          )}`}
                        >
                          {ticket.status.toUpperCase()}
                        </span>
                      </div>
                      <h3 className="text-[#F8FAFC] font-medium mb-2">
                        {ticket.customer_name}
                      </h3>
                      <p className="text-sm text-[#94A3B8] mb-2">
                        {ticket.escalation_reason}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-[#64748B]">
                        <span>{ticket.customer_email}</span>
                        <span>•</span>
                        <span className="capitalize">{ticket.category}</span>
                        <span>•</span>
                        <span className={getPriorityColor(ticket.priority)}>
                          {ticket.priority.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <button className="text-[#3B82F6] hover:text-[#60A5FA] text-sm font-medium">
                      View →
                    </button>
                  </div>
                </motion.div>
              ))}
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
              No Escalated Tickets
            </h3>
            <p className="text-[#94A3B8]">
              All tickets are being handled by AI. Great job!
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
