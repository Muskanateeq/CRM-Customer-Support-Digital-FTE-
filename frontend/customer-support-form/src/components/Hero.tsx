"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { HiLightningBolt, HiShieldCheck, HiChatAlt2 } from "react-icons/hi";

interface HeroProps {
  isAuthenticated: boolean;
}

export default function Hero({ isAuthenticated }: HeroProps) {
  const router = useRouter();

  const handleStartChatting = () => {
    if (isAuthenticated) {
      // If authenticated, scroll to support portal or go to /support
      router.push("/support");
    } else {
      // If not authenticated, redirect to signup
      router.push("/signup");
    }
  };

  return (
    <section className="min-h-screen flex items-center justify-center px-6 pt-32 pb-20 relative overflow-hidden">
      {/* Animated Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute w-[600px] h-[600px] bg-[#2563EB]/20 rounded-full blur-3xl"
          animate={{
            x: [0, 100, 0],
            y: [0, -100, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          style={{ top: "-300px", right: "-300px" }}
        />
        <motion.div
          className="absolute w-[500px] h-[500px] bg-[#3B82F6]/15 rounded-full blur-3xl"
          animate={{
            x: [0, -100, 0],
            y: [0, 100, 0],
            scale: [1, 1.3, 1],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          style={{ bottom: "-250px", left: "-250px" }}
        />
      </div>

      {/* Top Center Badge */}
      <div className="absolute top-24 left-0 right-0 flex justify-center z-20">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass border border-[#2563EB]/30">
            <motion.span
              className="w-2 h-2 bg-[#10B981] rounded-full"
              animate={{
                opacity: [1, 0.3, 1],
                scale: [1, 0.8, 1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            ></motion.span>
            <span className="text-xs text-[#CBD5E1]">AI Agent Online • Instant Response</span>
          </div>
        </motion.div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto w-full z-10 relative">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Side - Text Content */}
          <div>
            {/* Main Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-3xl md:text-2xl lg:text-5xl font-extrabold mb-4 leading-tight"
            >
              <span className="gradient-text">24/7 AI-Powered</span>
              <br />
              <span className="text-[#F8FAFC]">Customer Support</span>
            </motion.h1>

            {/* Subheadline */}
            <motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="text-sm md:text-base text-[#94A3B8] mb-6 leading-relaxed"
            >
              Get instant, intelligent responses to your queries anytime, anywhere.
              Our AI agent understands your needs and provides personalized support
              across all channels.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="flex flex-col sm:flex-row items-start gap-3 mb-6"
            >
              <button
                onClick={handleStartChatting}
                className="btn-primary text-sm px-6 py-2.5 flex items-center gap-2"
              >
                Start Chatting Now
                <HiChatAlt2 className="w-4 h-4" />
              </button>
              <Link
                href="/help"
                className="btn-secondary text-sm px-6 py-2.5"
              >
                View Help Center
              </Link>
            </motion.div>

            {/* Trust Badges */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.8 }}
              className="flex flex-wrap items-center gap-4"
            >
              <div className="flex items-center gap-2 text-[#CBD5E1]">
                <HiLightningBolt className="w-4 h-4 text-[#F59E0B]" />
                <span className="text-xs font-medium">Instant Response</span>
              </div>
              <div className="flex items-center gap-2 text-[#CBD5E1]">
                <HiShieldCheck className="w-4 h-4 text-[#10B981]" />
                <span className="text-xs font-medium">Secure & Private</span>
              </div>
              <div className="flex items-center gap-2 text-[#CBD5E1]">
                <HiChatAlt2 className="w-4 h-4 text-[#3B82F6]" />
                <span className="text-xs font-medium">Multi-Channel</span>
              </div>
            </motion.div>
          </div>

          {/* Right Side - Illustration/Bot */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1, delay: 0.4 }}
            className="block"
          >
            <div className="relative">
              {/* Main Bot Card */}
              <div className="glass-card p-5 rounded-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#10B981] to-[#34D399] flex items-center justify-center">
                    <HiChatAlt2 className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-[#F8FAFC]">AI Assistant</h3>
                    <div className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-[#10B981] rounded-full animate-pulse"></span>
                      <span className="text-xs text-[#94A3B8]">Online</span>
                    </div>
                  </div>
                </div>

                {/* Sample Messages */}
                <div className="space-y-3">
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, delay: 1 }}
                    className="bg-[#1E293B]/50 p-3 rounded-xl rounded-bl-sm"
                  >
                    <p className="text-xs text-[#CBD5E1]">
                      Hi! How can I help you today? 👋
                    </p>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, delay: 1.2 }}
                    className="bg-gradient-to-br from-[#2563EB] to-[#3B82F6] p-3 rounded-xl rounded-br-sm ml-6"
                  >
                    <p className="text-xs text-white">
                      I need help with my order
                    </p>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, delay: 1.4 }}
                    className="bg-[#1E293B]/50 p-3 rounded-xl rounded-bl-sm"
                  >
                    <p className="text-xs text-[#CBD5E1]">
                      I&apos;d be happy to help! Let me check your order status... ✓
                    </p>
                  </motion.div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-3 mt-4 pt-4 border-t border-white/10">
                  <div className="text-center">
                    <div className="text-lg font-bold text-gradient">&lt;2s</div>
                    <div className="text-[10px] text-[#64748B]">Response</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-gradient">24/7</div>
                    <div className="text-[10px] text-[#64748B]">Available</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-gradient">98%</div>
                    <div className="text-[10px] text-[#64748B]">Satisfied</div>
                  </div>
                </div>
              </div>

              {/* Floating Elements */}
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 3, repeat: Infinity }}
                className="absolute -top-3 -right-3 w-14 h-14 rounded-full bg-gradient-to-br from-[#F59E0B] to-[#D97706] flex items-center justify-center shadow-xl"
              >
                <HiLightningBolt className="w-7 h-7 text-white" />
              </motion.div>

              <motion.div
                animate={{ y: [0, 10, 0] }}
                transition={{ duration: 4, repeat: Infinity }}
                className="absolute -bottom-3 -left-3 w-12 h-12 rounded-full bg-gradient-to-br from-[#10B981] to-[#059669] flex items-center justify-center shadow-xl"
              >
                <HiShieldCheck className="w-6 h-6 text-white" />
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 1.5 }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="w-6 h-10 border-2 border-[#3B82F6]/50 rounded-full flex items-start justify-center p-2"
        >
          <motion.div
            animate={{ y: [0, 12, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-1.5 h-1.5 bg-[#3B82F6] rounded-full"
          />
        </motion.div>
      </motion.div>
    </section>
  );
}
