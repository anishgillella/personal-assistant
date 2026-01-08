"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  MessageSquare,
  BarChart3,
  Settings,
  Sparkles,
  Github,
} from "lucide-react";

const navItems = [
  { href: "/", label: "Chat", icon: MessageSquare },
  { href: "/evaluation", label: "Evaluation", icon: BarChart3 },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex flex-col h-full w-64 bg-white border-r border-gray-200">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-200">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 shadow-lg shadow-violet-200">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-gray-900">QA Assistant</h1>
          <p className="text-xs text-gray-500">AI-Powered Chatbot</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4">
        <ul className="space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                    isActive
                      ? "bg-violet-50 text-violet-700 font-medium"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  }`}
                >
                  <item.icon
                    className={`w-5 h-5 ${
                      isActive ? "text-violet-600" : "text-gray-400"
                    }`}
                  />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="px-3 py-4 border-t border-gray-200">
        <div className="px-4 py-3 bg-gray-50 rounded-xl">
          <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
            <Settings className="w-4 h-4" />
            <span className="font-medium">Model</span>
          </div>
          <p className="text-xs text-gray-500">Gemini 2.5 Flash</p>
          <p className="text-xs text-gray-400">via OpenRouter</p>
        </div>
        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-3 mt-2 text-sm text-gray-500 hover:text-gray-700 transition-colors"
        >
          <Github className="w-4 h-4" />
          View on GitHub
        </a>
      </div>
    </div>
  );
}
