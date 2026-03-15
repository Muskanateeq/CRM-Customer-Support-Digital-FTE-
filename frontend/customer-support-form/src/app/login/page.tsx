"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import LoginForm from "@/components/auth/LoginForm";

export default function LoginPage() {
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
          className="w-full max-w-md"
        >
          {/* Logo */}
          <div className="text-center mb-8">
            <Link href="/">
              <h1 className="text-3xl font-bold gradient-text">Custora CRM</h1>
            </Link>
          </div>

          {/* Login Card */}
          <div className="glass-card p-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-[#F8FAFC] mb-2">Welcome Back</h2>
              <p className="text-[#94A3B8]">Sign in to your account to continue</p>
            </div>

            <LoginForm />

            <div className="mt-6 text-center text-sm text-[#94A3B8]">
              Don&apos;t have an account?{" "}
              <Link href="/signup" className="text-[#3B82F6] hover:text-[#60A5FA] font-medium">
                Sign up
              </Link>
            </div>
          </div>

          {/* Back to Home */}
          <div className="mt-6 text-center">
            <Link href="/" className="text-[#94A3B8] hover:text-[#F8FAFC] text-sm">
              ← Back to Home
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
