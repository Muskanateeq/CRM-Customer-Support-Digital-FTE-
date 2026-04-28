"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { HiTicket, HiClock, HiCheckCircle, HiChartBar, HiUser, HiMail, HiRefresh } from "react-icons/hi";
import authClient from "@/lib/auth-client";
import AuthGate from "@/components/AuthGate";
import { getBackendURL } from "@/lib/config";

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
  source_channel: string;
  created_at: string;
  customer_name: string;
  customer_email: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const { data: session, isPending } = authClient.useSession();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentTickets, setRecentTickets] = useState<Ticket[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Fetch dashboard data function
  const fetchDashboardData = async (silent = false) => {
    // Silent refresh doesn't show full loading state
    if (!silent) {
      setIsLoading(true);
    } else {
      setIsRefreshing(true);
    }
    setError("");

    try {
      const backendURL = getBackendURL();

      // Fetch dashboard stats
      const statsResponse = await fetch(
        `${backendURL}/api/v1/tickets/dashboard/stats`
      );

      if (!statsResponse.ok) {
        throw new Error("Failed to fetch dashboard stats");
      }

      const statsData = await statsResponse.json();
      setStats(statsData);

      // Fetch recent tickets
      const ticketsResponse = await fetch(
        `${backendURL}/api/v1/tickets/dashboard/recent?limit=5`
      );

      if (!ticketsResponse.ok) {
        throw new Error("Failed to fetch recent tickets");
      }

      const ticketsData = await ticketsResponse.json();
      setRecentTickets(ticketsData.tickets || []);

      // Update last updated timestamp
      setLastUpdated(new Date());

    } catch (err) {
      console.error("Dashboard fetch error:", err);
      setError("Failed to load dashboard data");
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleManualRefresh = () => {
    fetchDashboardData(true);
  };

  const getTimeAgo = (date: Date | null) => {
    if (!date) return "";
    const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);
    if (seconds < 10) return "just now";
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m ago`;
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

  // Effect hook - runs after authentication is checked
  useEffect(() => {
    // Only fetch data if user is authenticated
    if (session && !isPending) {
      fetchDashboardData();

      // Auto-refresh every 30 seconds
      const interval = setInterval(() => {
        fetchDashboardData(true); // Silent refresh
      }, 30000);

      // Cleanup interval on unmount
      return () => clearInterval(interval);
    }
  }, [session, isPending]);

  // Check authentication - render loading or auth gate
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
        title="Sign Up to Access Dashboard"
        description="Create a free account to get instant access to your personalized support dashboard."
        features={[
          {
            title: "View All Tickets",
            description: "See all your support tickets in one centralized dashboard"
          },
          {
            title: "Real-Time Tracking",
            description: "Monitor ticket status and updates as they happen"
          },
          {
            title: "Response Analytics",
            description: "Track average response times and support performance"
          },
          {
            title: "Conversation History",
            description: "Access complete chat logs and ticket conversations"
          },
          {
            title: "AI Insights",
            description: "Get intelligent analytics and recommendations"
          },
          {
            title: "Account Management",
            description: "Manage your profile and notification preferences"
          },
        ]}
      />
    );
  }

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
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#2563EB] to-[#3B82F6] flex items-center justify-center">
                <HiUser className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl md:text-4xl font-bold gradient-text">
                  My Dashboard
                </h1>
                <p className="text-[#94A3B8]">
                  Welcome back, {session?.user?.name || 'User'}!
                </p>
              </div>
            </div>

            {/* Refresh Button */}
            <div className="flex items-center gap-3">
              {lastUpdated && (
                <span className="text-sm text-[#64748B]">
                  Updated {getTimeAgo(lastUpdated)}
                </span>
              )}
              <button
                onClick={handleManualRefresh}
                disabled={isRefreshing}
                className="flex items-center gap-2 px-4 py-2 bg-[#1E293B]/50 hover:bg-[#1E293B] border border-white/10 rounded-lg text-[#94A3B8] hover:text-[#3B82F6] transition-all disabled:opacity-50"
                title="Refresh dashboard"
              >
                <HiRefresh className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
                <span className="hidden sm:inline">Refresh</span>
              </button>
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
              onClick={() => fetchDashboardData()}
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
                          className={`px-2 py-0.5 rounded-full text-xs font-medium border ${
                            ticket.status === "open"
                              ? "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30"
                              : ticket.status === "escalated"
                              ? "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/30"
                              : ticket.status === "processing"
                              ? "bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/30"
                              : ticket.status === "resolved"
                              ? "bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30"
                              : "bg-[#94A3B8]/10 text-[#94A3B8] border-[#94A3B8]/30"
                          }`}
                        >
                          {ticket.status.toUpperCase()}
                        </span>
                        <span className={`text-xs font-medium ${
                          ticket.priority === "urgent"
                            ? "text-[#EF4444]"
                            : ticket.priority === "high"
                            ? "text-[#F97316]"
                            : ticket.priority === "medium"
                            ? "text-[#F59E0B]"
                            : "text-[#10B981]"
                        }`}>
                          {ticket.priority.toUpperCase()}
                        </span>
                      </div>
                      <h3 className="text-[#F8FAFC] font-medium mb-1">
                        {ticket.customer_name || "Unknown Customer"}
                      </h3>
                      <p className="text-sm text-[#94A3B8] mb-2">
                        {ticket.customer_email || "No email"}
                      </p>
                      <p className="text-sm text-[#CBD5E1] mb-2">
                        {ticket.subject || "No subject"}
                      </p>
                      <div className="flex items-center gap-3 text-xs text-[#64748B]">
                        <span className="capitalize">{ticket.category.replace('_', ' ')}</span>
                        <span>•</span>
                        <span className="capitalize">{ticket.source_channel.replace('_', ' ')}</span>
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
            <a href="/support" className="btn-primary inline-block">
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
            <a href="/support" className="btn-primary flex items-center gap-2">
              <HiMail className="w-5 h-5" />
              New Support Request
            </a>
            <a href="/tickets" className="btn-secondary flex items-center gap-2">
              <HiTicket className="w-5 h-5" />
              View All Tickets
            </a>
          </motion.div>
        )}

        {/* Contact Channels */}
        {!isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1 }}
            className="mt-8 glass-card p-8"
          >
            <h2 className="text-2xl font-bold text-[#F8FAFC] mb-6 flex items-center gap-2">
              <HiMail className="w-6 h-6 text-[#3B82F6]" />
              Contact Support
            </h2>
            <p className="text-[#94A3B8] mb-6">
              Need help? Reach out to us through any of these channels:
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Email */}
              <div className="p-4 bg-[#1E293B]/50 rounded-lg border border-white/5 hover:border-[#3B82F6]/30 transition-all">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-full bg-[#3B82F6]/20 flex items-center justify-center">
                    <HiMail className="w-5 h-5 text-[#3B82F6]" />
                  </div>
                  <div>
                    <h3 className="text-[#F8FAFC] font-medium">Email Support</h3>
                    <p className="text-xs text-[#64748B]">24/7 AI-powered responses</p>
                  </div>
                </div>
                <a
                  href="mailto:custora.support@gmail.com"
                  className="text-[#3B82F6] hover:text-[#60A5FA] text-sm font-medium transition-colors"
                >
                  custora.support@gmail.com
                </a>
              </div>

              {/* WhatsApp */}
              <div className="p-4 bg-[#1E293B]/50 rounded-lg border border-white/5 hover:border-[#10B981]/30 transition-all">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-full bg-[#10B981]/20 flex items-center justify-center">
                    <svg className="w-5 h-5 text-[#10B981]" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-[#F8FAFC] font-medium">WhatsApp</h3>
                    <p className="text-xs text-[#64748B]">Instant messaging support</p>
                  </div>
                </div>
                <a
                  href="https://wa.me/14155238886"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[#10B981] hover:text-[#34D399] text-sm font-medium transition-colors"
                >
                  +1 (415) 523-8886
                </a>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
