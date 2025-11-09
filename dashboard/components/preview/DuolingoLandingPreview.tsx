"use client";

/**
 * DUOLINGO-INSPIRED LANDING PAGE PREVIEW
 *
 * Features:
 * - Bright, welcoming hero with mascot illustration area
 * - Large, rounded buttons with 3D shadow effect
 * - Playful copy and encouraging language
 * - Bright color scheme (green, blue, orange)
 * - Fun feature cards with icons
 */

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  TrendingUp,
  Zap,
  Shield,
  Trophy,
  Star,
  Target,
  Sparkles,
} from "lucide-react";

export function DuolingoLandingPreview() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-green-50 to-blue-50">
      {/* Mascot/Illustration area - placeholder */}
      <div className="absolute top-20 right-10 opacity-20 pointer-events-none">
        <div className="w-64 h-64 rounded-full bg-gradient-to-br from-[#58CC02] to-[#1CB0F6]" />
      </div>

      {/* Hero Section */}
      <div className="container mx-auto px-4 pt-24 pb-16 relative">
        <div className="max-w-4xl mx-auto text-center">
          {/* Fun badge */}
          <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-to-r from-yellow-400 to-orange-400 text-white mb-8 duo-badge">
            <Sparkles className="w-5 h-5" />
            <span className="text-sm font-bold">
              AI-Powered Trading Made Fun!
            </span>
          </div>

          <h1 className="text-6xl md:text-7xl font-extrabold mb-6 leading-tight">
            <span className="text-gray-800">Learn to trade</span>
            <br />
            <span className="bg-gradient-to-r from-[#58CC02] to-[#1CB0F6] bg-clip-text text-transparent">
              while you earn! 🚀
            </span>
          </h1>

          <p className="text-2xl text-gray-700 mb-12 max-w-2xl mx-auto leading-relaxed">
            The <span className="font-bold text-[#58CC02]">fun, free</span> way
            to master prediction market trading with AI agents helping you every
            step!
          </p>

          {/* Main CTA */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <Button
              size="lg"
              className="duo-button text-xl px-12 py-8 rounded-2xl bg-[#58CC02] hover:bg-[#58CC02] text-white font-bold"
              style={{ boxShadow: "0 6px 0 #46A302" }}
            >
              <svg className="w-6 h-6 mr-3" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              GET STARTED
            </Button>
          </div>

          <p className="text-sm text-gray-600 mb-16">
            ✨ <span className="font-semibold">100% free</span> • No credit card
            needed • Start earning today
          </p>

          {/* Stats bar */}
          <div className="grid grid-cols-3 gap-8 max-w-3xl mx-auto mb-20">
            <div className="text-center">
              <p className="text-4xl font-bold text-gray-800 mb-2">10K+</p>
              <p className="text-sm text-gray-600">Happy Traders</p>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-gray-800 mb-2">$2M+</p>
              <p className="text-sm text-gray-600">Total Traded</p>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-gray-800 mb-2">98%</p>
              <p className="text-sm text-gray-600">Satisfaction</p>
            </div>
          </div>

          {/* Feature Cards with Duolingo style */}
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="duo-card bg-white hover:scale-105 transition-transform cursor-pointer">
              <div className="p-8">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-green-400 to-[#58CC02] flex items-center justify-center mb-6 mx-auto">
                  <TrendingUp className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-gray-800">
                  Real-Time Insights
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  Watch your portfolio grow with beautiful charts and instant
                  updates! 📊
                </p>
              </div>
            </div>

            <div className="duo-card bg-white hover:scale-105 transition-transform cursor-pointer">
              <div className="p-8">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-400 to-[#1CB0F6] flex items-center justify-center mb-6 mx-auto">
                  <Zap className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-gray-800">
                  AI Super Powers
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  Smart AI agents work 24/7 to find you the best trading
                  opportunities! 🤖
                </p>
              </div>
            </div>

            <div className="duo-card bg-white hover:scale-105 transition-transform cursor-pointer">
              <div className="p-8">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-orange-400 to-[#FF9600] flex items-center justify-center mb-6 mx-auto">
                  <Trophy className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-gray-800">
                  Earn Rewards
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  Build streaks, unlock achievements, and level up your trading
                  game! 🏆
                </p>
              </div>
            </div>
          </div>

          {/* Why it's awesome section */}
          <div className="mt-24 duo-card bg-gradient-to-r from-[#58CC02] to-[#1CB0F6] p-12 text-white">
            <h2 className="text-4xl font-bold mb-6">Why traders love us 💚</h2>
            <div className="grid md:grid-cols-2 gap-8 text-left max-w-3xl mx-auto">
              <div className="flex gap-4">
                <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center flex-shrink-0">
                  <Target className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h4 className="font-bold text-lg mb-2">Bite-sized trades</h4>
                  <p className="text-white/90">
                    Quick, fun trades that fit into your day. Just 5 minutes!
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center flex-shrink-0">
                  <Star className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h4 className="font-bold text-lg mb-2">
                    Personalized for you
                  </h4>
                  <p className="text-white/90">
                    AI learns your style and suggests perfect picks!
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center flex-shrink-0">
                  <Trophy className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h4 className="font-bold text-lg mb-2">Stay motivated</h4>
                  <p className="text-white/90">
                    Streaks, XP, and achievements keep you on track!
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center flex-shrink-0">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h4 className="font-bold text-lg mb-2">Safe & secure</h4>
                  <p className="text-white/90">
                    Your data is protected with bank-level security!
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Final CTA */}
          <div className="mt-24 text-center">
            <h2 className="text-4xl font-bold text-gray-800 mb-6">
              Ready to start your trading journey? 🎯
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Join thousands of traders leveling up their skills every day!
            </p>
            <Button
              size="lg"
              className="duo-button text-xl px-12 py-8 rounded-2xl bg-[#58CC02] hover:bg-[#58CC02] text-white font-bold"
              style={{ boxShadow: "0 6px 0 #46A302" }}
            >
              Start Trading Now - It's Free! 🚀
            </Button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-200 mt-24 bg-white">
        <div className="container mx-auto px-4 py-12">
          <p className="text-center text-gray-600">
            © 2025 Magic Conch Trading • Made with 💚 for traders everywhere
          </p>
        </div>
      </footer>
    </div>
  );
}
