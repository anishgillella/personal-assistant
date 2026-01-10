import type {
  ChatResponse,
  EvaluationResult,
  EvaluationStatus,
  ConversationListItem,
  ConversationResponse,
  TokenUsageStats,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API error: ${response.status}`);
    }

    return response.json();
  }

  // Chat endpoints
  async sendMessage(
    query: string,
    conversationId?: string | null
  ): Promise<ChatResponse> {
    return this.request<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        query,
        conversation_id: conversationId,
      }),
    });
  }

  // Conversation endpoints
  async getConversations(): Promise<ConversationListItem[]> {
    return this.request<ConversationListItem[]>("/api/conversations");
  }

  async getConversation(conversationId: string): Promise<ConversationResponse> {
    return this.request<ConversationResponse>(
      `/api/conversations/${conversationId}`
    );
  }

  async deleteConversation(
    conversationId: string
  ): Promise<{ success: boolean; message: string }> {
    return this.request(`/api/conversations/${conversationId}`, {
      method: "DELETE",
    });
  }

  // Evaluation endpoints
  async runEvaluation(
    datasetPath?: string
  ): Promise<{ success: boolean; message: string }> {
    return this.request("/api/evaluation/run", {
      method: "POST",
      body: JSON.stringify({ dataset_path: datasetPath }),
    });
  }

  async getEvaluationStatus(): Promise<EvaluationStatus> {
    return this.request<EvaluationStatus>("/api/evaluation/status");
  }

  async getEvaluationResults(): Promise<EvaluationResult> {
    return this.request<EvaluationResult>("/api/evaluation/results");
  }

  // Token usage endpoints
  async getTokenUsage(): Promise<TokenUsageStats> {
    return this.request<TokenUsageStats>("/api/usage");
  }

  async resetTokenUsage(): Promise<{ success: boolean; message: string }> {
    return this.request("/api/usage/reset", {
      method: "POST",
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request("/api/health");
  }
}

const api = new ApiClient();
export default api;
