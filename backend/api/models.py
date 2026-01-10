from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    query: str = Field(..., description="The user's question or message")
    conversation_id: Optional[str] = Field(
        None, description="Optional conversation ID for context"
    )


class ToolUsage(BaseModel):
    """Model for tool usage information."""

    name: str
    arguments: dict[str, Any]
    result: dict[str, Any]


class TokenUsageInfo(BaseModel):
    """Model for token usage information."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    conversation_id: str
    tools_used: list[ToolUsage] = []
    timestamp: str
    usage: Optional[TokenUsageInfo] = None


class TokenUsageResponse(BaseModel):
    """Response model for token usage endpoint."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    request_count: int


class Message(BaseModel):
    """Model for a single message in a conversation."""

    role: str
    content: str
    tool_calls: Optional[list[dict]] = None
    tool_call_id: Optional[str] = None


class ConversationResponse(BaseModel):
    """Response model for conversation endpoint."""

    conversation_id: str
    messages: list[Message]


class ConversationListItem(BaseModel):
    """Model for conversation list item."""

    conversation_id: str
    message_count: int
    last_message: Optional[str] = None


class EvaluationRequest(BaseModel):
    """Request model for running evaluation."""

    dataset_path: Optional[str] = Field(
        None, description="Path to evaluation dataset JSON file"
    )


class MetricScore(BaseModel):
    """Model for individual metric score."""

    name: str
    score: float
    details: Optional[str] = None


class EvaluationItem(BaseModel):
    """Model for a single evaluation item."""

    question: str
    expected_answer: str
    actual_response: str
    tools_used: list[str]
    metrics: list[MetricScore]
    overall_score: float


class EvaluationResult(BaseModel):
    """Response model for evaluation results."""

    success: bool
    timestamp: str
    total_questions: int
    average_score: float
    metric_averages: dict[str, float]
    results: list[EvaluationItem]
    error: Optional[str] = None


class EvaluationStatus(BaseModel):
    """Model for evaluation status."""

    status: str  # "idle", "running", "completed", "failed"
    progress: Optional[int] = None
    total: Optional[int] = None
    message: Optional[str] = None
