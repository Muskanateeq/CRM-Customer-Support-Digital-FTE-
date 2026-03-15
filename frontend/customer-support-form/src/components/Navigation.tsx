"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import ProfileDropdown from "./ProfileDropdown";

export default function Navigation() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, isAuthenticated, logout } = useAuth();

  // Debug logging
  useEffect(() => {
    console.log('[Navigation] Auth state updated:', {
      user: user ? { id: user.id, email: user.email, name: user.name } : null,
      isAuthenticated
    });
  }, [user, isAuthenticated]);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const menuItems = [
    { name: "Home", href: "/" },
    { name: "Features", href: "/#features" },
    { name: "Support", href: "/support" },
    { name: "Dashboard", href: "/dashboard" },
    { name: "Check Status", href: "/tickets" },
    { name: "Help", href: "/help" },
  ];

  return (
    <nav
      className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        scrolled
          ? "bg-[#0F172A]/90 backdrop-blur-xl"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#2563EB] to-[#3B82F6] flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:shadow-[#2563EB]/50 transition-all">
              <span className="text-white font-bold text-xl">C</span>
            </div>
            <span className="text-2xl font-bold gradient-text">Custora</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden lg:flex items-center gap-1">
            {menuItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className="relative px-4 py-2 text-[#CBD5E1] hover:text-[#F8FAFC] rounded-lg transition-all group overflow-hidden"
              >
                <span className="relative z-10 text-sm font-medium">{item.name}</span>
                <div className="absolute inset-0 bg-gradient-to-r from-[#2563EB]/0 via-[#2563EB]/10 to-[#2563EB]/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-gradient-to-r from-[#2563EB] to-[#3B82F6] group-hover:w-3/4 transition-all duration-300" />
              </Link>
            ))}
          </div>

          {/* CTA Buttons / User Info */}
          <div className="hidden lg:flex items-center gap-3">
            {isAuthenticated ? (
              <ProfileDropdown />
            ) : (
              <>
                <Link
                  href="/login"
                  className="px-6 py-2.5 text-[#CBD5E1] hover:text-[#F8FAFC] font-medium text-sm transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  href="/signup"
                  className="btn-primary text-sm font-semibold"
                >
                  Get Started →
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 text-[#CBD5E1] hover:text-[#F8FAFC] hover:bg-white/5 rounded-lg transition-all"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {mobileMenuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden mt-4 pb-4 animate-fade-in">
            <div className="flex flex-col gap-2">
              {menuItems.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className="px-4 py-3 text-[#CBD5E1] hover:text-[#F8FAFC] hover:bg-white/5 rounded-lg transition-all"
                >
                  <span className="font-medium">{item.name}</span>
                </Link>
              ))}
              <div className="h-px bg-white/10 my-2" />

              {isAuthenticated ? (
                <>
                  {/* User Info Mobile */}
                  <div className="px-4 py-3 flex items-center gap-3">
                    {user?.image ? (
                      <img
                        src={user.image}
                        alt={user.name || "User"}
                        className="w-8 h-8 rounded-full border-2 border-[#3B82F6]"
                      />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#2563EB] to-[#3B82F6] flex items-center justify-center text-white font-medium text-sm">
                        {user?.name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || "U"}
                      </div>
                    )}
                    <span className="text-[#F8FAFC] font-medium">
                      {user?.name || user?.email}
                    </span>
                  </div>
                  <button
                    onClick={() => {
                      logout();
                      setMobileMenuOpen(false);
                    }}
                    className="px-4 py-3 text-[#94A3B8] hover:text-[#F8FAFC] text-left font-medium transition-colors"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    onClick={() => setMobileMenuOpen(false)}
                    className="px-4 py-3 text-[#CBD5E1] hover:text-[#F8FAFC] font-medium transition-colors"
                  >
                    Sign In
                  </Link>
                  <Link
                    href="/signup"
                    onClick={() => setMobileMenuOpen(false)}
                    className="btn-primary text-center"
                  >
                    Get Started →
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
