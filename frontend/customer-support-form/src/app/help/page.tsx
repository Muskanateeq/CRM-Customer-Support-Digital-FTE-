"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  HiSearch,
  HiQuestionMarkCircle,
  HiBookOpen,
  HiVideoCamera,
  HiLightningBolt,
  HiChevronRight,
} from "react-icons/hi";

interface PopularTopic {
  title: string;
  category: string;
  views: number;
}

interface Category {
  title: string;
  description: string;
  articles: number;
  color: string;
  category: string;
}

interface SearchResult {
  id: string;
  title: string;
  category: string;
  views: number;
  created_at: string;
}

export default function HelpPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [popularTopics, setPopularTopics] = useState<PopularTopic[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchHelpData();
  }, []);

  const fetchHelpData = async () => {
    setIsLoading(true);
    setError("");

    try {
      // Fetch popular topics
      const topicsResponse = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/tickets/help/popular?limit=5`
      );

      if (!topicsResponse.ok) {
        throw new Error("Failed to fetch popular topics");
      }

      const topicsData = await topicsResponse.json();
      setPopularTopics(topicsData.topics || []);

      // Fetch categories
      const categoriesResponse = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/tickets/help/categories`
      );

      if (!categoriesResponse.ok) {
        throw new Error("Failed to fetch categories");
      }

      const categoriesData = await categoriesResponse.json();
      setCategories(categoriesData.categories || []);

    } catch (err) {
      console.error("Help data fetch error:", err);
      setError("Failed to load help data");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCategoryClick = async (categoryName: string) => {
    // Search for articles in this category
    setSearchQuery(categoryName);
    setIsSearching(true);
    setError("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/tickets/help/search?q=${encodeURIComponent(categoryName)}`
      );

      if (!response.ok) {
        throw new Error("Search failed");
      }

      const data = await response.json();
      setSearchResults(data.articles || []);

      // Scroll to results
      window.scrollTo({ top: 400, behavior: 'smooth' });

    } catch (err) {
      console.error("Category search error:", err);
      setError("Failed to load category articles. Please try again.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setError("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/tickets/help/search?q=${encodeURIComponent(searchQuery)}`
      );

      if (!response.ok) {
        throw new Error("Search failed");
      }

      const data = await response.json();
      setSearchResults(data.articles || []);
      console.log("Search results:", data.articles);

    } catch (err) {
      console.error("Search error:", err);
      setError("Failed to search. Please try again.");
    } finally {
      setIsSearching(false);
    }
  };

  const getIconForCategory = (categoryTitle: string) => {
    if (categoryTitle.includes("Technical")) return HiQuestionMarkCircle;
    if (categoryTitle.includes("Billing")) return HiVideoCamera;
    return HiBookOpen;
  };

  return (
    <div className="min-h-screen bg-[#0A0E27]">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-[600px] h-[600px] bg-[#2563EB]/10 rounded-full blur-3xl top-0 right-0" />
        <div className="absolute w-[500px] h-[500px] bg-[#3B82F6]/10 rounded-full blur-3xl bottom-0 left-0" />
      </div>

      <div className="container mx-auto px-4 py-24 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 glass rounded-full mb-6">
            <HiQuestionMarkCircle className="w-5 h-5 text-[#3B82F6]" />
            <span className="text-sm text-[#CBD5E1]">We&apos;re here to help</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="gradient-text">Help Center</span>
          </h1>
          <p className="text-xl text-[#94A3B8] max-w-2xl mx-auto">
            Find answers, guides, and resources to get the most out of Custora
          </p>
        </motion.div>

        {/* Search Box */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="max-w-2xl mx-auto mb-16"
        >
          <div className="glass-card p-6">
            <div className="flex gap-3">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                placeholder="Search for help articles, guides, tutorials..."
                className="flex-1 input-field"
              />
              <button
                onClick={handleSearch}
                disabled={isSearching}
                className="btn-primary px-8 flex items-center gap-2 disabled:opacity-50"
              >
                <HiSearch className="w-5 h-5" />
                {isSearching ? "Searching..." : "Search"}
              </button>
            </div>
          </div>
        </motion.div>

        {/* Error State */}
        {error && (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="glass-card p-6 border-[#EF4444]/30">
              <p className="text-[#EF4444]">{error}</p>
              <button
                onClick={fetchHelpData}
                className="mt-4 btn-primary text-sm"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Search Results */}
        {searchResults.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto mb-16"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-[#F8FAFC]">
                Search Results ({searchResults.length})
              </h2>
              <button
                onClick={() => setSearchResults([])}
                className="text-sm text-[#3B82F6] hover:text-[#60A5FA]"
              >
                Clear Results
              </button>
            </div>

            <div className="glass-card p-6">
              <div className="space-y-3">
                {searchResults.map((result, index) => (
                  <motion.div
                    key={result.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.05 }}
                    className="p-4 bg-[#1E293B]/50 rounded-lg border border-white/5 hover:border-[#3B82F6]/30 transition-all cursor-pointer group"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 flex-1">
                        <HiLightningBolt className="w-5 h-5 text-[#F59E0B] flex-shrink-0" />
                        <div className="flex-1">
                          <h3 className="text-[#F8FAFC] font-medium group-hover:text-[#3B82F6] transition-colors">
                            {result.title}
                          </h3>
                          <div className="flex items-center gap-3 mt-1">
                            <span className="text-xs text-[#64748B]">{result.category}</span>
                            <span className="text-xs text-[#64748B]">•</span>
                            <span className="text-xs text-[#64748B]">{result.views} views</span>
                          </div>
                        </div>
                      </div>
                      <HiChevronRight className="w-5 h-5 text-[#94A3B8] group-hover:text-[#3B82F6] group-hover:translate-x-1 transition-all" />
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[#3B82F6]"></div>
            <p className="text-[#94A3B8] mt-4">Loading help center...</p>
          </div>
        )}

        {/* Categories */}
        {!isLoading && categories.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mb-16"
          >
            <h2 className="text-2xl font-bold text-[#F8FAFC] mb-8 text-center">
              Browse by Category
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
              {categories.map((category, index) => {
                const IconComponent = getIconForCategory(category.title);
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.5 + index * 0.1 }}
                    whileHover={{ y: -8 }}
                    onClick={() => handleCategoryClick(category.category)}
                    className="glass-card p-6 cursor-pointer group"
                  >
                    <div
                      className={`w-14 h-14 rounded-xl bg-gradient-to-br ${category.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
                    >
                      <IconComponent className="w-7 h-7 text-white" />
                    </div>
                    <h3 className="text-xl font-bold text-[#F8FAFC] mb-2 group-hover:text-gradient transition-all">
                      {category.title}
                    </h3>
                    <p className="text-[#94A3B8] text-sm mb-4">{category.description}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-[#64748B]">{category.articles} articles</span>
                      <HiChevronRight className="w-5 h-5 text-[#3B82F6] group-hover:translate-x-1 transition-transform" />
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}

        {/* Popular Topics */}
        {!isLoading && popularTopics.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="max-w-4xl mx-auto mb-16"
          >
            <h2 className="text-2xl font-bold text-[#F8FAFC] mb-8 flex items-center gap-2">
              <HiLightningBolt className="w-6 h-6 text-[#F59E0B]" />
              Popular Topics
            </h2>

            <div className="glass-card p-6">
              <div className="space-y-3">
                {popularTopics.map((topic, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: 0.7 + index * 0.05 }}
                    className="p-4 bg-[#1E293B]/50 rounded-lg border border-white/5 hover:border-[#3B82F6]/30 transition-all cursor-pointer group"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 flex-1">
                        <HiLightningBolt className="w-5 h-5 text-[#F59E0B] flex-shrink-0" />
                        <div className="flex-1">
                          <h3 className="text-[#F8FAFC] font-medium group-hover:text-[#3B82F6] transition-colors">
                            {topic.title}
                          </h3>
                          <div className="flex items-center gap-3 mt-1">
                            <span className="text-xs text-[#64748B]">{topic.category}</span>
                            <span className="text-xs text-[#64748B]">•</span>
                            <span className="text-xs text-[#64748B]">{topic.views} views</span>
                          </div>
                        </div>
                      </div>
                      <HiChevronRight className="w-5 h-5 text-[#94A3B8] group-hover:text-[#3B82F6] group-hover:translate-x-1 transition-all" />
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Empty State */}
        {!isLoading && !error && popularTopics.length === 0 && categories.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card p-12 text-center max-w-2xl mx-auto mb-16"
          >
            <HiQuestionMarkCircle className="w-16 h-16 mx-auto mb-4 text-[#64748B]" />
            <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">
              No Help Articles Yet
            </h3>
            <p className="text-[#94A3B8] mb-6">
              Help articles will appear here as tickets are created
            </p>
            <a href="/support" className="btn-primary inline-block">
              Contact Support
            </a>
          </motion.div>
        )}

        {/* Contact Support CTA */}
        {!isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="max-w-3xl mx-auto text-center"
          >
            <div className="glass-card p-8">
              <h2 className="text-2xl font-bold text-[#F8FAFC] mb-3">
                Still need help?
              </h2>
              <p className="text-[#94A3B8] mb-6">
                Can&apos;t find what you&apos;re looking for? Our AI assistant is here to help 24/7
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a href="/support" className="btn-primary">
                  Contact Support
                </a>
                <a href="/tickets" className="btn-secondary">
                  Check Ticket Status
                </a>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
