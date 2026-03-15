"use client";

import { useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import SupportLayout from "@/components/SupportLayout";

export default function SupportPage() {
  const { user, isLoading, refreshSession } = useAuth();

  // Refresh session on mount (important after OAuth redirects)
  useEffect(() => {
    console.log('[SupportPage] Refreshing session on mount...');
    refreshSession();
  }, [refreshSession]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0A0E27] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-[#3B82F6] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#94A3B8]">Loading...</p>
        </div>
      </div>
    );
  }

  // If NOT authenticated, show sign-up prompt
  if (!user) {
    return (
      <div className="min-h-screen bg-[#0A0E27] relative overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute w-[600px] h-[600px] bg-[#2563EB]/10 rounded-full blur-3xl top-0 right-0" />
          <div className="absolute w-[500px] h-[500px] bg-[#3B82F6]/10 rounded-full blur-3xl bottom-0 left-0" />
        </div>

        <div className="container mx-auto px-4 py-24 relative z-10 flex items-center justify-center min-h-screen">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-2xl w-full"
          >
            {/* Lock Icon */}
            <div className="text-center mb-8">
              <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-[#2563EB]/20 to-[#3B82F6]/20 flex items-center justify-center">
                <svg
                  className="w-10 h-10 text-[#3B82F6]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
              </div>
              <h1 className="text-4xl font-bold gradient-text mb-4">
                Sign Up to Access Support Portal
              </h1>
              <p className="text-[#94A3B8] text-lg">
                Create a free account to get instant access to our AI-powered support assistant.
                Get personalized help, track your tickets, and resolve issues faster.
              </p>
            </div>

            {/* Features */}
            <div className="glass-card p-8 mb-8">
              <h3 className="text-xl font-semibold text-[#F8FAFC] mb-6">
                What you&apos;ll get:
              </h3>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-[#3B82F6]/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-4 h-4 text-[#3B82F6]" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[#F8FAFC] font-medium mb-1">24/7 AI Support Agent</h4>
                    <p className="text-[#94A3B8] text-sm">Get instant responses to your queries anytime, anywhere</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-[#3B82F6]/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-4 h-4 text-[#3B82F6]" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[#F8FAFC] font-medium mb-1">Track Your Tickets</h4>
                    <p className="text-[#94A3B8] text-sm">Monitor all your support requests in one place</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-[#3B82F6]/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-4 h-4 text-[#3B82F6]" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="text-[#F8FAFC] font-medium mb-1">Personalized Experience</h4>
                    <p className="text-[#94A3B8] text-sm">Get help tailored to your specific needs and history</p>
                  </div>
                </div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/signup"
                className="px-8 py-3 bg-gradient-to-r from-[#2563EB] to-[#3B82F6] text-white font-semibold rounded-lg hover:shadow-lg hover:shadow-[#3B82F6]/30 transition-all text-center"
              >
                Create Free Account
              </Link>
              <Link
                href="/login"
                className="px-8 py-3 border border-white/10 text-[#F8FAFC] font-semibold rounded-lg hover:bg-white/5 transition-all text-center"
              >
                Sign In
              </Link>
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  // If authenticated, show full support portal (form + chatbot)
  return <SupportLayout />;
}
