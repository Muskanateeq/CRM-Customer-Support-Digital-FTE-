"use client";

import { useEffect } from "react";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import SupportPortalLocked from "@/components/SupportPortalLocked";
import SupportLayout from "@/components/SupportLayout";
import { useAuth } from "@/hooks/useAuth";

export default function Home() {
  const { user, refreshSession } = useAuth();

  // Refresh session on mount (important after OAuth redirects)
  useEffect(() => {
    console.log('[HomePage] Refreshing session on mount...');
    refreshSession();
  }, [refreshSession]);

  return (
    <main className="bg-[#0A0E27]">
      <Hero isAuthenticated={!!user} />
      <Features />
      {/* Show SupportLayout for authenticated users, locked portal for unauthenticated */}
      {user ? <SupportLayout /> : <SupportPortalLocked />}
    </main>
  );
}
