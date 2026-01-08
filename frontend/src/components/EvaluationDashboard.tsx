"use client";

import { useState, useEffect } from "react";
import {
  Play,
  Loader2,
  CheckCircle2,
  XCircle,
  AlertCircle,
  BarChart3,
  Target,
  TrendingUp,
  Clock,
  ChevronDown,
  ChevronUp,
  RefreshCw,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Cell,
} from "recharts";
import type { EvaluationResult, EvaluationStatus, EvaluationItem } from "@/lib/types";
import api from "@/lib/api";

const METRIC_COLORS: Record<string, string> = {
  relevance: "#8b5cf6",
  accuracy: "#06b6d4",
  completeness: "#10b981",
  coherence: "#f59e0b",
  tool_usage: "#ec4899",
};

const METRIC_LABELS: Record<string, string> = {
  relevance: "Relevance",
  accuracy: "Accuracy",
  completeness: "Completeness",
  coherence: "Coherence",
  tool_usage: "Tool Usage",
};

export default function EvaluationDashboard() {
  const [results, setResults] = useState<EvaluationResult | null>(null);
  const [status, setStatus] = useState<EvaluationStatus>({ status: "idle" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchResults = async () => {
    try {
      const data = await api.getEvaluationResults();
      setResults(data);
      setError(null);
    } catch {
      // No results yet is ok
      setResults(null);
    }
  };

  const fetchStatus = async () => {
    try {
      const data = await api.getEvaluationStatus();
      setStatus(data);
    } catch {
      // Status fetch failed
    }
  };

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      await Promise.all([fetchResults(), fetchStatus()]);
      setLoading(false);
    };
    init();
  }, []);

  useEffect(() => {
    if (status.status === "running") {
      const interval = setInterval(async () => {
        await fetchStatus();
        if (status.status === "completed") {
          await fetchResults();
        }
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [status.status]);

  const handleRunEvaluation = async () => {
    try {
      setError(null);
      await api.runEvaluation();
      setStatus({ status: "running", progress: 0, total: 0, message: "Starting..." });

      // Poll for completion
      const pollInterval = setInterval(async () => {
        const newStatus = await api.getEvaluationStatus();
        setStatus(newStatus);

        if (newStatus.status === "completed" || newStatus.status === "failed") {
          clearInterval(pollInterval);
          if (newStatus.status === "completed") {
            await fetchResults();
          } else {
            setError(newStatus.message || "Evaluation failed");
          }
        }
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start evaluation");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-violet-500" />
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto bg-gray-50">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Evaluation Dashboard</h1>
            <p className="text-gray-500 mt-1">
              Analyze chatbot performance across multiple metrics
            </p>
          </div>
          <div className="flex items-center gap-3">
            {results && (
              <button
                onClick={fetchResults}
                className="flex items-center gap-2 px-4 py-2 text-gray-600 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
            )}
            <button
              onClick={handleRunEvaluation}
              disabled={status.status === "running"}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-violet-500 to-purple-600 text-white font-medium rounded-xl hover:shadow-lg hover:shadow-violet-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {status.status === "running" ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Run Evaluation
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-6 px-4 py-3 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3">
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

        {/* Progress Banner */}
        {status.status === "running" && (
          <div className="mb-6 px-4 py-4 bg-violet-50 border border-violet-200 rounded-xl">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-violet-700">
                {status.message || "Running evaluation..."}
              </span>
              <span className="text-sm text-violet-600">
                {status.progress} / {status.total}
              </span>
            </div>
            <div className="w-full h-2 bg-violet-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-violet-500 to-purple-600 rounded-full transition-all duration-300"
                style={{
                  width: status.total
                    ? `${(status.progress! / status.total) * 100}%`
                    : "0%",
                }}
              />
            </div>
          </div>
        )}

        {results ? (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <SummaryCard
                icon={Target}
                label="Overall Score"
                value={`${(results.average_score * 100).toFixed(1)}%`}
                color="violet"
              />
              <SummaryCard
                icon={BarChart3}
                label="Questions Evaluated"
                value={results.total_questions.toString()}
                color="cyan"
              />
              <SummaryCard
                icon={TrendingUp}
                label="Best Metric"
                value={getBestMetric(results.metric_averages)}
                color="emerald"
              />
              <SummaryCard
                icon={Clock}
                label="Last Run"
                value={formatTimestamp(results.timestamp)}
                color="amber"
              />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Bar Chart */}
              <div className="bg-white rounded-2xl border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Metric Averages
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={Object.entries(results.metric_averages).map(
                        ([name, score]) => ({
                          name: METRIC_LABELS[name] || name,
                          score: score * 100,
                          fill: METRIC_COLORS[name] || "#8b5cf6",
                        })
                      )}
                      margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis
                        dataKey="name"
                        tick={{ fontSize: 12 }}
                        tickLine={false}
                      />
                      <YAxis
                        domain={[0, 100]}
                        tick={{ fontSize: 12 }}
                        tickLine={false}
                        tickFormatter={(v) => `${v}%`}
                      />
                      <Tooltip
                        formatter={(value: number) => [`${value.toFixed(1)}%`, "Score"]}
                        contentStyle={{
                          borderRadius: "12px",
                          border: "1px solid #e5e7eb",
                        }}
                      />
                      <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                        {Object.entries(results.metric_averages).map(
                          ([name], index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={METRIC_COLORS[name] || "#8b5cf6"}
                            />
                          )
                        )}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Radar Chart */}
              <div className="bg-white rounded-2xl border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Performance Overview
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart
                      data={Object.entries(results.metric_averages).map(
                        ([name, score]) => ({
                          metric: METRIC_LABELS[name] || name,
                          score: score * 100,
                        })
                      )}
                    >
                      <PolarGrid stroke="#e5e7eb" />
                      <PolarAngleAxis
                        dataKey="metric"
                        tick={{ fontSize: 11 }}
                      />
                      <PolarRadiusAxis
                        angle={90}
                        domain={[0, 100]}
                        tick={{ fontSize: 10 }}
                      />
                      <Radar
                        name="Score"
                        dataKey="score"
                        stroke="#8b5cf6"
                        fill="#8b5cf6"
                        fillOpacity={0.3}
                      />
                      <Tooltip
                        formatter={(value: number) => [`${value.toFixed(1)}%`, "Score"]}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Detailed Results */}
            <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">
                  Detailed Results
                </h3>
              </div>
              <div className="divide-y divide-gray-100">
                {results.results.map((item, index) => (
                  <ResultItem key={index} item={item} index={index} />
                ))}
              </div>
            </div>
          </>
        ) : (
          /* Empty State */
          <div className="flex flex-col items-center justify-center py-16 bg-white rounded-2xl border border-gray-200">
            <div className="flex items-center justify-center w-16 h-16 mb-4 rounded-2xl bg-gray-100">
              <BarChart3 className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No Evaluation Results
            </h3>
            <p className="text-gray-500 mb-6 text-center max-w-md">
              Run an evaluation to see how your chatbot performs across different
              metrics.
            </p>
            <button
              onClick={handleRunEvaluation}
              disabled={status.status === "running"}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-violet-500 to-purple-600 text-white font-medium rounded-xl hover:shadow-lg hover:shadow-violet-200 transition-all"
            >
              <Play className="w-4 h-4" />
              Run Evaluation
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function SummaryCard({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  color: "violet" | "cyan" | "emerald" | "amber";
}) {
  const colorClasses = {
    violet: "bg-violet-50 text-violet-600",
    cyan: "bg-cyan-50 text-cyan-600",
    emerald: "bg-emerald-50 text-emerald-600",
    amber: "bg-amber-50 text-amber-600",
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-5">
      <div className="flex items-center gap-3 mb-3">
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
        <span className="text-sm text-gray-500">{label}</span>
      </div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
    </div>
  );
}

function ResultItem({ item, index }: { item: EvaluationItem; index: number }) {
  const [expanded, setExpanded] = useState(false);
  const scoreColor =
    item.overall_score >= 0.8
      ? "text-emerald-600 bg-emerald-50"
      : item.overall_score >= 0.6
      ? "text-amber-600 bg-amber-50"
      : "text-red-600 bg-red-50";

  return (
    <div className="px-6 py-4">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left"
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm text-gray-400">#{index + 1}</span>
              {item.overall_score >= 0.8 ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              ) : item.overall_score >= 0.6 ? (
                <AlertCircle className="w-4 h-4 text-amber-500" />
              ) : (
                <XCircle className="w-4 h-4 text-red-500" />
              )}
            </div>
            <p className="text-gray-900 font-medium truncate">{item.question}</p>
          </div>
          <div className="flex items-center gap-3">
            <span
              className={`px-2.5 py-1 text-sm font-medium rounded-lg ${scoreColor}`}
            >
              {(item.overall_score * 100).toFixed(0)}%
            </span>
            {expanded ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </div>
        </div>
      </button>

      {expanded && (
        <div className="mt-4 space-y-4 pl-6">
          {/* Expected vs Actual */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 rounded-xl">
              <p className="text-xs font-medium text-gray-500 mb-2">
                Expected Answer
              </p>
              <p className="text-sm text-gray-700">{item.expected_answer}</p>
            </div>
            <div className="p-4 bg-violet-50 rounded-xl">
              <p className="text-xs font-medium text-violet-600 mb-2">
                Actual Response
              </p>
              <p className="text-sm text-gray-700">{item.actual_response}</p>
            </div>
          </div>

          {/* Tools Used */}
          {item.tools_used.length > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Tools:</span>
              {item.tools_used.map((tool) => (
                <span
                  key={tool}
                  className="px-2 py-0.5 text-xs font-medium bg-violet-100 text-violet-700 rounded-full"
                >
                  {tool}
                </span>
              ))}
            </div>
          )}

          {/* Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {item.metrics.map((metric) => (
              <div
                key={metric.name}
                className="p-3 bg-gray-50 rounded-xl text-center"
              >
                <p className="text-xs text-gray-500 mb-1">
                  {METRIC_LABELS[metric.name] || metric.name}
                </p>
                <p
                  className="text-lg font-bold"
                  style={{ color: METRIC_COLORS[metric.name] || "#8b5cf6" }}
                >
                  {(metric.score * 100).toFixed(0)}%
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function getBestMetric(averages: Record<string, number>): string {
  let best = "";
  let bestScore = -1;
  for (const [name, score] of Object.entries(averages)) {
    if (score > bestScore) {
      bestScore = score;
      best = name;
    }
  }
  return METRIC_LABELS[best] || best;
}

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  if (diff < 60000) return "Just now";
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return date.toLocaleDateString();
}
