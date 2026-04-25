"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import authClient from "@/lib/auth-client";
import AuthGate from "@/components/AuthGate";

export default function WhatsAppFeaturePage() {
  const router = useRouter();
  const { data: session, isPending } = authClient.useSession();

  useEffect(() => {
    // If user is authenticated, redirect to WhatsApp
    if (session?.user) {
      const whatsappUrl = "https://wa.me/14155238886";
      window.location.href = whatsappUrl;
    }
  }, [session]);

  // Show loading while checking auth
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

  // Show AuthGate if not authenticated
  if (!session) {
    return (
      <AuthGate
        title="Sign In to Use WhatsApp Support"
        description="Create a free account to access our AI-powered WhatsApp support system."
        features={[
          {
            title: "Instant WhatsApp Chat",
            description: "Get quick responses directly on WhatsApp"
          },
          {
            title: "Mobile-Friendly",
            description: "Perfect for on-the-go support with instant notifications"
          },
          {
            title: "Conversational AI",
            description: "Natural chat experience with our intelligent AI agent"
          },
          {
            title: "Message History",
            description: "Access your complete WhatsApp conversation history"
          },
          {
            title: "Real-Time Responses",
            description: "Get answers within seconds, 24/7"
          },
          {
            title: "Secure & Private",
            description: "End-to-end encrypted conversations"
          },
        ]}
      />
    );
  }

  // Show loading while redirecting
  return (
    <div className="min-h-screen bg-[#0A0E27] flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[#10B981]"></div>
        <p className="text-[#94A3B8] mt-4">Redirecting to WhatsApp...</p>
      </div>
    </div>
  );
}
