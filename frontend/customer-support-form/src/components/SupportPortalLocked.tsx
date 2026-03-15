"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { HiLockClosed, HiChatAlt2, HiShieldCheck, HiUserGroup } from "react-icons/hi";

export default function SupportPortalLocked() {
  return (
    <div className="min-h-screen bg-[#0A0E27] relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-[800px] h-[800px] bg-[#2563EB]/10 rounded-full blur-3xl -top-96 -right-96 animate-pulse-glow" />
        <div className="absolute w-[600px] h-[600px] bg-[#3B82F6]/10 rounded-full blur-3xl -bottom-96 -left-96 animate-pulse-glow" />
      </div>

      <div className="container mx-auto px-4 pt-20 pb-8 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-6"
          id="support-portal"
        >
          <h1 className="text-2xl md:text-3xl font-bold mb-2">
            <span className="gradient-text">Support Portal</span>
          </h1>
          <p className="text-[#94A3B8] text-sm">
            Get instant help from our AI-powered support assistant
          </p>
        </motion.div>

        {/* Locked State */}
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="glass-card p-6 md:p-8 rounded-2xl text-center relative overflow-hidden"
          >
            {/* Lock Icon with Glow */}
            <div className="relative inline-block mb-4">
              <motion.div
                animate={{
                  scale: [1, 1.1, 1],
                  opacity: [0.5, 0.8, 0.5],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
                className="absolute inset-0 bg-[#3B82F6]/30 rounded-full blur-2xl"
              />
              <div className="relative w-16 h-16 md:w-20 md:h-20 rounded-full bg-gradient-to-br from-[#2563EB] to-[#3B82F6] flex items-center justify-center">
                <HiLockClosed className="w-8 h-8 md:w-10 md:h-10 text-white" />
              </div>
            </div>

            {/* Heading */}
            <h2 className="text-xl md:text-2xl font-bold text-[#F8FAFC] mb-3">
              Sign Up to Access Support Portal
            </h2>

            {/* Description */}
            <p className="text-[#94A3B8] text-sm md:text-base mb-6 max-w-2xl mx-auto">
              Create a free account to get instant access to our AI-powered support assistant.
              Get personalized help, track your tickets, and resolve issues faster.
            </p>

            {/* Features Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
              <div className="bg-[#1E293B]/50 p-3 rounded-xl border border-white/10">
                <HiChatAlt2 className="w-7 h-7 text-[#3B82F6] mx-auto mb-2" />
                <h3 className="text-[#F8FAFC] font-semibold text-sm mb-1">24/7 AI Support</h3>
                <p className="text-[#64748B] text-xs">Instant responses anytime</p>
              </div>

              <div className="bg-[#1E293B]/50 p-3 rounded-xl border border-white/10">
                <HiShieldCheck className="w-7 h-7 text-[#10B981] mx-auto mb-2" />
                <h3 className="text-[#F8FAFC] font-semibold text-sm mb-1">Secure & Private</h3>
                <p className="text-[#64748B] text-xs">Your data is protected</p>
              </div>

              <div className="bg-[#1E293B]/50 p-3 rounded-xl border border-white/10">
                <HiUserGroup className="w-7 h-7 text-[#F59E0B] mx-auto mb-2" />
                <h3 className="text-[#F8FAFC] font-semibold text-sm mb-1">Track Tickets</h3>
                <p className="text-[#64748B] text-xs">Manage all your requests</p>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                href="/signup"
                className="w-full sm:w-auto px-6 py-2.5 bg-gradient-to-r from-[#2563EB] to-[#3B82F6] text-white font-semibold rounded-lg hover:shadow-lg hover:shadow-[#3B82F6]/30 transition-all flex items-center justify-center gap-2 text-sm"
              >
                Create Free Account
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>

              <Link
                href="/login"
                className="w-full sm:w-auto px-6 py-2.5 bg-[#1E293B] text-[#F8FAFC] font-semibold rounded-lg border border-white/10 hover:bg-[#334155] transition-all text-sm"
              >
                Already have an account? Sign In
              </Link>
            </div>

            {/* Trust Badge */}
            <div className="mt-6 pt-4 border-t border-white/10">
              <p className="text-[#64748B] text-xs">
                Join thousands of customers getting instant support
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
