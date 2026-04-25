"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AdminLoginPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to main login page
    router.push("/login");
  }, [router]);

  return (
    <div className="min-h-screen bg-[#0A0E27] flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[#3B82F6] mb-4"></div>
        <p className="text-[#94A3B8]">Redirecting to login...</p>
      </div>
    </div>
  );
}
