from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import json
import os
from datetime import datetime

from api.models import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    ConversationListItem,
    EvaluationRequest,
    EvaluationResult,
    EvaluationStatus,
    Message,
    ToolUsage,
    TokenUsageInfo,
    TokenUsageResponse,
)
from chatbot import ChatAgent
from evaluation import Evaluator

router = APIRouter()

# Global instances
chat_agent = ChatAgent()
evaluator = Evaluator(chat_agent)

# Evaluation state
evaluation_state = {
    "status": "idle",
    "progress": 0,
    "total": 0,
    "message": None,
    "latest_result": None,
}


# ============== Chat Endpoints ==============


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the chatbot and get a response.
    """
    result = chat_agent.chat(
        query=request.query,
        conversation_id=request.conversation_id,
    )

    # Extract usage info
    usage_data = result.get("usage", {})
    usage = TokenUsageInfo(
        prompt_tokens=usage_data.get("prompt_tokens", 0),
        completion_tokens=usage_data.get("completion_tokens", 0),
        total_tokens=usage_data.get("total_tokens", 0),
    ) if usage_data else None

    return ChatResponse(
        success=result.get("success", False),
        response=result.get("response"),
        error=result.get("error"),
        conversation_id=result.get("conversation_id", ""),
        tools_used=[
            ToolUsage(
                name=t["name"],
                arguments=t["arguments"],
                result=t["result"],
            )
            for t in result.get("tools_used", [])
        ],
        timestamp=result.get("timestamp", datetime.utcnow().isoformat()),
        usage=usage,
    )


# ============== Conversation Endpoints ==============


@router.get("/conversations")
async def list_conversations() -> list[ConversationListItem]:
    """
    List all conversations.
    """
    conversations = chat_agent.get_all_conversations()
    items = []

    for conv_id, messages in conversations.items():
        # Filter out system messages for display
        user_messages = [m for m in messages if m.get("role") == "user"]
        last_message = user_messages[-1]["content"] if user_messages else None

        items.append(
            ConversationListItem(
                conversation_id=conv_id,
                message_count=len(messages),
                last_message=last_message[:100] if last_message else None,
            )
        )

    return items


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str) -> ConversationResponse:
    """
    Get a specific conversation by ID.
    """
    messages = chat_agent.get_conversation(conversation_id)

    if messages is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationResponse(
        conversation_id=conversation_id,
        messages=[
            Message(
                role=m.get("role", ""),
                content=m.get("content", ""),
                tool_calls=m.get("tool_calls"),
                tool_call_id=m.get("tool_call_id"),
            )
            for m in messages
        ],
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str) -> dict:
    """
    Delete a conversation.
    """
    if chat_agent.clear_conversation(conversation_id):
        return {"success": True, "message": "Conversation deleted"}
    raise HTTPException(status_code=404, detail="Conversation not found")


# ============== Evaluation Endpoints ==============


def run_evaluation_task(dataset_path: Optional[str] = None):
    """Background task to run evaluation."""
    global evaluation_state

    try:
        evaluation_state["status"] = "running"
        evaluation_state["message"] = "Starting evaluation..."

        # Use default dataset path if not provided
        if not dataset_path:
            dataset_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data",
                "evaluation_dataset.json",
            )

        # Run evaluation with progress callback
        def progress_callback(current: int, total: int):
            evaluation_state["progress"] = current
            evaluation_state["total"] = total
            evaluation_state["message"] = f"Evaluating question {current}/{total}"

        result = evaluator.run_evaluation(
            dataset_path=dataset_path,
            progress_callback=progress_callback,
        )

        evaluation_state["status"] = "completed"
        evaluation_state["latest_result"] = result
        evaluation_state["message"] = "Evaluation completed successfully"

        # Save results to file
        results_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data",
            "results",
        )
        os.makedirs(results_dir, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        results_path = os.path.join(results_dir, f"evaluation_{timestamp}.json")

        with open(results_path, "w") as f:
            json.dump(result, f, indent=2)

    except Exception as e:
        evaluation_state["status"] = "failed"
        evaluation_state["message"] = str(e)
        evaluation_state["latest_result"] = None


@router.post("/evaluation/run")
async def run_evaluation(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Start an evaluation run (async).
    """
    global evaluation_state

    if evaluation_state["status"] == "running":
        raise HTTPException(status_code=409, detail="Evaluation already in progress")

    evaluation_state = {
        "status": "running",
        "progress": 0,
        "total": 0,
        "message": "Initializing...",
        "latest_result": None,
    }

    background_tasks.add_task(run_evaluation_task, request.dataset_path)

    return {"success": True, "message": "Evaluation started"}


@router.get("/evaluation/status")
async def get_evaluation_status() -> EvaluationStatus:
    """
    Get the current evaluation status.
    """
    return EvaluationStatus(
        status=evaluation_state["status"],
        progress=evaluation_state["progress"],
        total=evaluation_state["total"],
        message=evaluation_state["message"],
    )


@router.get("/evaluation/results")
async def get_evaluation_results() -> EvaluationResult:
    """
    Get the latest evaluation results.
    """
    # First check in-memory result
    if evaluation_state.get("latest_result"):
        return EvaluationResult(**evaluation_state["latest_result"])

    # Try to load the most recent results file
    results_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data",
        "results",
    )

    if not os.path.exists(results_dir):
        raise HTTPException(status_code=404, detail="No evaluation results found")

    result_files = sorted(
        [f for f in os.listdir(results_dir) if f.startswith("evaluation_")],
        reverse=True,
    )

    if not result_files:
        raise HTTPException(status_code=404, detail="No evaluation results found")

    latest_file = os.path.join(results_dir, result_files[0])

    with open(latest_file, "r") as f:
        result = json.load(f)

    return EvaluationResult(**result)


# ============== Token Usage Endpoints ==============


@router.get("/usage", response_model=TokenUsageResponse)
async def get_token_usage() -> TokenUsageResponse:
    """
    Get cumulative token usage statistics.
    """
    usage = chat_agent.get_token_usage()
    return TokenUsageResponse(**usage)


@router.post("/usage/reset")
async def reset_token_usage() -> dict:
    """
    Reset token usage counters.
    """
    chat_agent.reset_token_usage()
    return {"success": True, "message": "Token usage counters reset"}


# ============== Health Check ==============


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }
