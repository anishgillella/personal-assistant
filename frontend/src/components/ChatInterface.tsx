"use client";

import { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  Loader2,
  Wrench,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Sparkles,
  Coins,
  RotateCcw,
} from "lucide-react";
import type { Message, ToolUsage, TokenUsageStats } from "@/lib/types";
import api from "@/lib/api";

interface ChatMessage extends Message {
  tools_used?: ToolUsage[];
  isLoading?: boolean;
  timestamp?: string;
  tokens?: number;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [tokenUsage, setTokenUsage] = useState<TokenUsageStats | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch token usage on mount and after each message
  const fetchTokenUsage = async () => {
    try {
      const usage = await api.getTokenUsage();
      setTokenUsage(usage);
    } catch {
      // Silently fail - token usage is not critical
    }
  };

  useEffect(() => {
    fetchTokenUsage();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setError(null);

    // Add user message
    setMessages((prev) => [
      ...prev,
      { role: "user", content: userMessage },
    ]);

    // Add loading message
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "", isLoading: true },
    ]);

    setIsLoading(true);

    try {
      const response = await api.sendMessage(userMessage, conversationId);

      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Replace loading message with actual response
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          role: "assistant",
          content: response.response || "",
          tools_used: response.tools_used,
          timestamp: response.timestamp,
          tokens: response.usage?.total_tokens,
        };
        return newMessages;
      });

      // Update token usage
      fetchTokenUsage();

      if (!response.success && response.error) {
        setError(response.error);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
      // Remove loading message on error
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setConversationId(undefined);
    setError(null);
    inputRef.current?.focus();
  };

  const handleResetUsage = async () => {
    try {
      await api.resetTokenUsage();
      setTokenUsage({ prompt_tokens: 0, completion_tokens: 0, total_tokens: 0, request_count: 0 });
    } catch {
      // Silently fail
    }
  };

  const formatTokenCount = (count: number) => {
    if (count >= 1000000) {
      return `${(count / 1000000).toFixed(1)}M`;
    } else if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}k`;
    }
    return count.toString();
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 shadow-lg shadow-violet-200">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">QA Assistant</h1>
            <p className="text-xs text-gray-500">Powered by Gemini 2.5 Flash</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {/* Token Usage Display */}
          {tokenUsage && (
            <div className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg border border-gray-200">
              <Coins className="w-4 h-4 text-amber-500" />
              <div className="text-xs">
                <span className="text-gray-600">{formatTokenCount(tokenUsage.total_tokens)} tokens</span>
                <span className="text-gray-400 mx-1">|</span>
                <span className="text-gray-500">{tokenUsage.request_count} requests</span>
              </div>
              <button
                onClick={handleResetUsage}
                className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                title="Reset usage"
              >
                <RotateCcw className="w-3 h-3" />
              </button>
            </div>
          )}
          <button
            onClick={handleNewChat}
            className="px-4 py-2 text-sm font-medium text-violet-600 bg-violet-50 rounded-lg hover:bg-violet-100 transition-colors"
          >
            New Chat
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="flex items-center justify-center w-16 h-16 mb-4 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 shadow-xl shadow-violet-200">
              <Bot className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              How can I help you today?
            </h2>
            <p className="text-gray-500 max-w-md mb-6">
              I can search the web, check Wikipedia, run code,
              convert units, and more. Ask me anything!
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg">
              {[
                "What is 25% of 80?",
                "Convert 100 miles to km",
                "How many days until Christmas?",
                "Who was Albert Einstein?",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setInput(suggestion)}
                  className="px-4 py-3 text-sm text-left text-gray-700 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 hover:border-violet-300 transition-all"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((message, index) => (
              <MessageBubble key={index} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mx-4 mb-4 px-4 py-3 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-500 hover:text-red-700"
          >
            ×
          </button>
        </div>
      )}

      {/* Input Area */}
      <div className="px-4 pb-4">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          <div className="relative flex items-end bg-white border border-gray-200 rounded-2xl shadow-sm focus-within:border-violet-400 focus-within:ring-2 focus-within:ring-violet-100 transition-all">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask me anything..."
              rows={1}
              className="flex-1 px-4 py-3 bg-transparent border-none resize-none focus:outline-none text-gray-900 placeholder-gray-400 max-h-32"
              style={{ minHeight: "48px" }}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="m-2 p-2 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-violet-200 transition-all"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          <p className="mt-2 text-xs text-center text-gray-400">
            Press Enter to send, Shift + Enter for new line
          </p>
        </form>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const [showTools, setShowTools] = useState(false);
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
          isUser
            ? "bg-gray-200"
            : "bg-gradient-to-br from-violet-500 to-purple-600"
        }`}
      >
        {isUser ? (
          <User className="w-4 h-4 text-gray-600" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>

      {/* Content */}
      <div className={`flex-1 max-w-[80%] ${isUser ? "text-right" : ""}`}>
        <div
          className={`inline-block px-4 py-3 rounded-2xl ${
            isUser
              ? "bg-gradient-to-r from-violet-500 to-purple-600 text-white"
              : "bg-white border border-gray-200 text-gray-900"
          }`}
        >
          {message.isLoading ? (
            <div className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-gray-500">Thinking...</span>
            </div>
          ) : (
            <div className="whitespace-pre-wrap">{message.content}</div>
          )}
        </div>

        {/* Tools Used and Token Info */}
        <div className="mt-2 flex items-center gap-3 flex-wrap">
          {message.tools_used && message.tools_used.length > 0 && (
            <button
              onClick={() => setShowTools(!showTools)}
              className="flex items-center gap-1 text-xs text-gray-500 hover:text-violet-600 transition-colors"
            >
              <Wrench className="w-3 h-3" />
              <span>
                {message.tools_used.length} tool
                {message.tools_used.length > 1 ? "s" : ""} used
              </span>
              {showTools ? (
                <ChevronUp className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
            </button>
          )}
          {message.tokens && !isUser && (
            <span className="flex items-center gap-1 text-xs text-gray-400">
              <Coins className="w-3 h-3" />
              {message.tokens} tokens
            </span>
          )}
        </div>

        {showTools && message.tools_used && (
          <div className="mt-2 space-y-2">
            {message.tools_used.map((tool, idx) => (
              <div
                key={idx}
                className="p-3 bg-gray-50 border border-gray-200 rounded-xl text-left"
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-0.5 text-xs font-medium bg-violet-100 text-violet-700 rounded-full">
                    {tool.name}
                  </span>
                </div>
                <div className="text-xs text-gray-600">
                  <div className="mb-1">
                    <span className="font-medium">Input:</span>{" "}
                    <code className="px-1 py-0.5 bg-gray-100 rounded">
                      {JSON.stringify(tool.arguments)}
                    </code>
                  </div>
                  <div>
                    <span className="font-medium">Result:</span>{" "}
                    <code className="px-1 py-0.5 bg-gray-100 rounded">
                      {JSON.stringify(tool.result).substring(0, 100)}
                      {JSON.stringify(tool.result).length > 100 && "..."}
                    </code>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
