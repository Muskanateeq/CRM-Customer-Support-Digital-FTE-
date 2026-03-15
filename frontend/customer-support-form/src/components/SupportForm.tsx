"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { HiUser, HiMail, HiDocumentText, HiTag, HiExclamation, HiChatAlt2 } from "react-icons/hi";

interface SupportFormProps {
  onSubmit: (
    email: string,
    name: string,
    subject: string,
    category: string,
    priority: string,
    message: string
  ) => void;
  isLoading: boolean;
}

const categories = [
  { value: "", label: "Select category", disabled: true },
  { value: "order_status", label: "📦 Order Status", description: "Track orders, cancellations" },
  { value: "shipping", label: "🚚 Shipping", description: "Delivery, international shipping" },
  { value: "returns", label: "↩️ Returns & Refunds", description: "Return items, refunds, exchanges" },
  { value: "payment", label: "💳 Payment", description: "Billing, declined payments" },
  { value: "account", label: "👤 Account", description: "Login, profile, password" },
  { value: "product", label: "🛍️ Product Info", description: "Availability, specs, reviews" },
  { value: "general", label: "📋 General", description: "Other inquiries" },
];

const priorities = [
  { value: "", label: "Select priority", disabled: true },
  { value: "low", label: "🟢 Low", description: "General inquiry, no rush", color: "#10B981" },
  { value: "medium", label: "🟡 Medium", description: "Need help within 24 hours", color: "#F59E0B" },
  { value: "high", label: "🟠 High", description: "Urgent, need help within 4 hours", color: "#F97316" },
  { value: "urgent", label: "🔴 Critical", description: "System down, immediate attention", color: "#EF4444" },
];

export default function SupportForm({ onSubmit, isLoading }: SupportFormProps) {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    category: "",
    priority: "",
    message: "",
  });
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!formData.category) {
      setError("Please select a category");
      return;
    }
    if (!formData.priority) {
      setError("Please select a priority level");
      return;
    }

    try {
      onSubmit(
        formData.email,
        formData.name,
        formData.subject,
        formData.category,
        formData.priority,
        formData.message
      );
      // Clear only message and subject, keep name/email/category/priority for follow-ups
      setFormData({ ...formData, message: "", subject: "" });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const messageLength = formData.message.length;
  const maxLength = 5000;

  return (
    <motion.div
      initial={{ opacity: 0, x: -30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6 }}
      className="glass-card p-6 h-full overflow-y-auto"
    >
      <div className="mb-4">
        <h2 className="text-xl font-bold mb-1 text-[#F8FAFC] flex items-center gap-2">
          <HiChatAlt2 className="w-5 h-5 text-[#3B82F6]" />
          Submit Support Request
        </h2>
        <p className="text-[#94A3B8] text-xs">
          Fill out the form and chat with our AI assistant in real-time.
        </p>
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4 p-3 bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-lg text-[#F87171] text-xs flex items-start gap-2"
        >
          <HiExclamation className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </motion.div>
      )}

      <form onSubmit={handleSubmit} className="space-y-3">
        {/* Name & Email - Same Line */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {/* Name */}
          <div>
            <label htmlFor="name" className="block mb-1.5 font-medium text-[#CBD5E1] text-xs flex items-center gap-1.5">
              <HiUser className="w-3.5 h-3.5" />
              Your Name *
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="John Doe"
              required
              disabled={isLoading}
              className="input-field text-sm py-2"
            />
          </div>

          {/* Email */}
          <div>
            <label htmlFor="email" className="block mb-1.5 font-medium text-[#CBD5E1] text-xs flex items-center gap-1.5">
              <HiMail className="w-3.5 h-3.5" />
              Email Address *
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="john@example.com"
              required
              disabled={isLoading}
              className="input-field text-sm py-2"
            />
          </div>
        </div>

        {/* Subject */}
        <div>
          <label htmlFor="subject" className="block mb-1.5 font-medium text-[#CBD5E1] text-xs flex items-center gap-1.5">
            <HiDocumentText className="w-3.5 h-3.5" />
            Subject *
          </label>
          <input
            type="text"
            id="subject"
            name="subject"
            value={formData.subject}
            onChange={handleChange}
            placeholder="Brief description of your issue"
            required
            disabled={isLoading}
            className="input-field text-sm py-2"
          />
        </div>

        {/* Category & Priority - Same Line */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {/* Category */}
          <div>
            <label htmlFor="category" className="block mb-1.5 font-medium text-[#CBD5E1] text-xs flex items-center gap-1.5">
              <HiTag className="w-3.5 h-3.5" />
              Category *
            </label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              required
              disabled={isLoading}
              className="input-field cursor-pointer text-sm py-2"
            >
              {categories.map((cat) => (
                <option key={cat.value} value={cat.value} disabled={cat.disabled}>
                  {cat.label}
                </option>
              ))}
            </select>
            {formData.category && (
              <p className="mt-0.5 text-[10px] text-[#94A3B8]">
                {categories.find((c) => c.value === formData.category)?.description}
              </p>
            )}
          </div>

          {/* Priority */}
          <div>
            <label htmlFor="priority" className="block mb-1.5 font-medium text-[#CBD5E1] text-xs flex items-center gap-1.5">
              <HiExclamation className="w-3.5 h-3.5" />
              Priority *
            </label>
            <select
              id="priority"
              name="priority"
              value={formData.priority}
              onChange={handleChange}
              required
              disabled={isLoading}
              className="input-field cursor-pointer text-sm py-2"
            >
              {priorities.map((pri) => (
                <option key={pri.value} value={pri.value} disabled={pri.disabled}>
                  {pri.label}
                </option>
              ))}
            </select>
            {formData.priority && (
              <p className="mt-0.5 text-[10px] text-[#94A3B8]">
                {priorities.find((p) => p.value === formData.priority)?.description}
              </p>
            )}
          </div>
        </div>

        {/* Message */}
        <div>
          <label htmlFor="message" className="block mb-1.5 font-medium text-[#CBD5E1] text-xs">
            Message *
          </label>
          <textarea
            id="message"
            name="message"
            value={formData.message}
            onChange={handleChange}
            placeholder="Describe your issue in detail..."
            required
            rows={5}
            maxLength={maxLength}
            disabled={isLoading}
            className="input-field resize-none text-sm"
          />
          <div className="mt-0.5 flex justify-between items-center text-[10px]">
            <span className="text-[#94A3B8]">Be as detailed as possible</span>
            <span className={`${messageLength > maxLength * 0.9 ? "text-[#F59E0B]" : "text-[#64748B]"}`}>
              {messageLength} / {maxLength}
            </span>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full btn-primary text-sm py-2.5 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Sending...
            </>
          ) : (
            <>
              Send Message
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </>
          )}
        </button>
      </form>

      {/* Info Box */}
      <div className="mt-4 p-3 bg-[#3B82F6]/10 border border-[#3B82F6]/30 rounded-lg">
        <p className="text-xs text-[#93C5FD] flex items-start gap-2">
          <span className="text-base">💡</span>
          <span>
            <strong>Tip:</strong> Each submission creates a support ticket. View your conversation history and all tickets using the &quot;View All Tickets&quot; button in the chat panel.
          </span>
        </p>
      </div>

      {/* Security Badge */}
      <div className="mt-3 flex items-center justify-center gap-2 text-[10px] text-[#64748B]">
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
        </svg>
        <span>Your data is encrypted and secure</span>
      </div>
    </motion.div>
  );
}
