"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import authClient from "@/lib/auth-client";
import AuthGate from "@/components/AuthGate";

export default function EmailFeaturePage() {
  const router = useRouter();
  const { data: session, isPending } = authClient.useSession();

  useEffect(() => {
    // If user is authenticated, redirect to Gmail compose
    if (session?.user) {
      const gmailUrl = "https://mail.google.com/mail/?view=cm&to=custora.support@gmail.com&su=Support%20Request&body=Hi%20Custora%20Support%20Team,%0D%0A%0D%0APlease%20describe%20your%20issue%20here...";
      window.location.href = gmailUrl;
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
        title="Sign In to Use Email Support"
        description="Create a free account to access our AI-powered email support system."
        features={[
          {
            title: "24/7 Email Support",
            description: "Get detailed responses to your emails within minutes"
          },
          {
            title: "Gmail Integration",
            description: "Seamlessly integrated with your Gmail account"
          },
          {
            title: "Smart AI Responses",
            description: "Our AI understands context and provides helpful solutions"
          },
          {
            title: "Conversation History",
            description: "Access all your email conversations in one place"
          },
          {
            title: "Priority Support",
            description: "Authenticated users get faster response times"
          },
          {
            title: "Ticket Tracking",
            description: "Track all your support tickets from your dashboard"
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
        <p className="text-[#94A3B8] mt-4">Redirecting to Gmail...</p>
      </div>
    </div>
  );
}
