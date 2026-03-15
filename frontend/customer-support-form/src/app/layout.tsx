import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navigation from "@/components/Navigation";
import { AuthProvider } from "@/contexts/AuthContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Custora - AI-Powered Customer Support",
  description: "Get instant, intelligent responses to your queries 24/7. Our AI agent understands your needs and provides personalized support.",
  keywords: ["customer support", "AI", "chatbot", "help desk", "support ticket"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <Navigation />
          {children}
          <footer className="text-center py-8 border-t border-[#3991bd]/10 text-gray-600">
            <p>&copy; 2024 Custora. AI-Powered Customer Success Platform.</p>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
