// API Response Types

export interface ToolUsage {
  name: string;
  arguments: Record<string, unknown>;
  result: Record<string, unknown>;
}

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface TokenUsageStats {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  request_count: number;
}

export interface ChatResponse {
  success: boolean;
  response: string | null;
  error: string | null;
  conversation_id: string;
  tools_used: ToolUsage[];
  timestamp: string;
  usage?: TokenUsage | null;
}

export interface Message {
  role: string;
  content: string;
  tool_calls?: Record<string, unknown>[];
  tool_call_id?: string;
}

export interface ConversationResponse {
  conversation_id: string;
  messages: Message[];
}

export interface ConversationListItem {
  conversation_id: string;
  message_count: number;
  last_message: string | null;
}

export interface MetricScore {
  name: string;
  score: number;
  details: string | null;
}

export interface EvaluationItem {
  question: string;
  expected_answer: string;
  actual_response: string;
  tools_used: string[];
  metrics: MetricScore[];
  overall_score: number;
}

export interface EvaluationResult {
  success: boolean;
  timestamp: string;
  total_questions: number;
  average_score: number;
  metric_averages: Record<string, number>;
  results: EvaluationItem[];
  error: string | null;
}

export interface EvaluationStatus {
  status: "idle" | "running" | "completed" | "failed";
  progress?: number | null;
  total?: number | null;
  message?: string | null;
}
