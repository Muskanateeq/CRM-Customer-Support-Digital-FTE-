"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import authClient from "@/lib/auth-client";
import AuthGate from "@/components/AuthGate";

export default function WebFormFeaturePage() {
  const router = useRouter();
  const { data: session, isPending } = authClient.useSession();

  useEffect(() => {
    // If user is authenticated, redirect to support page
    if (session?.user) {
      router.push("/support");
    }
  }, [session, router]);

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
        title="Sign In to Use Web Form Support"
        description="Create a free account to access our AI-powered live chat support system."
        features={[
          {
            title: "Real-Time Live Chat",
            description: "Chat directly on our website with instant AI responses"
          },
          {
            title: "Streaming Responses",
            description: "See answers appear in real-time as the AI types"
          },
          {
            title: "Smart Context Awareness",
            description: "AI remembers your conversation and provides relevant help"
          },
          {
            title: "Multi-Turn Conversations",
            description: "Have natural back-and-forth discussions with our AI"
          },
          {
            title: "Instant Ticket Creation",
            description: "Automatically create support tickets from your chats"
          },
          {
            title: "Full Chat History",
            description: "Access all your conversations from your dashboard"
          },
        ]}
      />
    );
  }

  // Show loading while redirecting
  return (
    <div className="min-h-screen bg-[#0A0E27] flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[#3B82F6]"></div>
        <p className="text-[#94A3B8] mt-4">Redirecting to support chat...</p>
      </div>
    </div>
  );
}
