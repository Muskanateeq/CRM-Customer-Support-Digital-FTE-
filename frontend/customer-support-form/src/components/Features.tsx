"use client";

import { motion } from "framer-motion";
import { HiMail, HiGlobe } from "react-icons/hi";
import { SiWhatsapp } from "react-icons/si";

const features = [
  {
    icon: HiMail,
    title: "Email Support",
    subtitle: "Gmail Integration",
    description:
      "Send us an email anytime. Our AI agent monitors your inbox and responds with detailed, helpful answers within minutes.",
    color: "from-[#EA4335] to-[#FBBC04]",
    bgColor: "bg-[#EA4335]/10",
  },
  {
    icon: SiWhatsapp,
    title: "WhatsApp Chat",
    subtitle: "Twilio Integration",
    description:
      "Get quick responses on WhatsApp. Perfect for on-the-go support with instant notifications and conversational replies.",
    color: "from-[#25D366] to-[#128C7E]",
    bgColor: "bg-[#25D366]/10",
  },
  {
    icon: HiGlobe,
    title: "Web Form",
    subtitle: "Live Chat",
    description:
      "Chat directly on our website with real-time AI responses. Get instant help with streaming answers as you type.",
    color: "from-[#3B82F6] to-[#2563EB]",
    bgColor: "bg-[#3B82F6]/10",
  },
];

export default function Features() {
  return (
    <section id="features" className="py-20 px-6 relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#1E293B]/30 to-transparent" />

      <div className="max-w-6xl mx-auto relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-3">
            <span className="gradient-text">Multi-Channel Support</span>
          </h2>
          <p className="text-lg text-[#94A3B8] max-w-2xl mx-auto">
            Get help through your preferred communication channel. All connected to one unified AI system.
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              whileHover={{ y: -8 }}
              className="glass-card p-6 group cursor-pointer"
            >
              {/* Icon */}
              <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg`}>
                <feature.icon className="w-7 h-7 text-white" />
              </div>

              {/* Title */}
              <h3 className="text-xl font-bold mb-1 text-[#F8FAFC] group-hover:text-gradient transition-all">
                {feature.title}
              </h3>

              {/* Subtitle */}
              <p className="text-xs text-[#3B82F6] font-medium mb-3">
                {feature.subtitle}
              </p>

              {/* Description */}
              <p className="text-[#94A3B8] text-sm leading-relaxed">
                {feature.description}
              </p>

              {/* Hover indicator */}
              <div className="mt-4 flex items-center gap-2 text-[#3B82F6] opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-xs font-medium">Learn more</span>
                <svg className="w-3 h-3 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="text-center mt-12"
        >
          <div className="inline-flex items-center gap-2 px-5 py-2.5 glass rounded-full">
            <div className="flex -space-x-2">
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#EA4335] to-[#FBBC04] flex items-center justify-center">
                <HiMail className="w-3.5 h-3.5 text-white" />
              </div>
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#25D366] to-[#128C7E] flex items-center justify-center">
                <SiWhatsapp className="w-3.5 h-3.5 text-white" />
              </div>
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#3B82F6] to-[#2563EB] flex items-center justify-center">
                <HiGlobe className="w-3.5 h-3.5 text-white" />
              </div>
            </div>
            <span className="text-[#CBD5E1] text-xs font-medium">All channels connected to one unified system</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
