import json
import uuid
from typing import Any, Optional
from datetime import datetime
from openai import OpenAI
from chatbot.config import settings
from chatbot.tools import get_tool, get_tool_schemas


class TokenUsage:
    """Track token usage across sessions."""

    def __init__(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.request_count = 0

    def add(self, prompt_tokens: int, completion_tokens: int):
        """Add token usage from a request."""
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_tokens += prompt_tokens + completion_tokens
        self.request_count += 1

    def to_dict(self) -> dict:
        """Return usage as dictionary."""
        return {
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens,
            "request_count": self.request_count,
        }

    def reset(self):
        """Reset all counters."""
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.request_count = 0


class ChatAgent:
    """LLM-powered chatbot agent with tool calling capabilities."""

    def __init__(self):
        """Initialize the chat agent with OpenRouter client."""
        self.client = OpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.conversations: dict[str, list[dict]] = {}
        self.token_usage = TokenUsage()

    def _get_or_create_conversation(self, conversation_id: Optional[str] = None) -> tuple[str, list[dict]]:
        """
        Get existing conversation or create a new one.

        Args:
            conversation_id: Optional existing conversation ID

        Returns:
            Tuple of (conversation_id, messages list)
        """
        if conversation_id and conversation_id in self.conversations:
            return conversation_id, self.conversations[conversation_id]

        new_id = str(uuid.uuid4())
        self.conversations[new_id] = [
            {"role": "system", "content": settings.SYSTEM_PROMPT}
        ]
        return new_id, self.conversations[new_id]

    def _execute_tool_call(self, tool_call) -> dict[str, Any]:
        """
        Execute a tool call and return the result.

        Args:
            tool_call: The tool call object from the LLM

        Returns:
            Dictionary containing tool execution result
        """
        tool_name = tool_call.function.name
        tool = get_tool(tool_name)

        if not tool:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
            }

        try:
            arguments = json.loads(tool_call.function.arguments)
            result = tool.execute(**arguments)
            return result
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid tool arguments",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _track_usage(self, response) -> dict:
        """Extract and track token usage from response."""
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        if hasattr(response, "usage") and response.usage:
            usage["prompt_tokens"] = getattr(response.usage, "prompt_tokens", 0) or 0
            usage["completion_tokens"] = getattr(response.usage, "completion_tokens", 0) or 0
            usage["total_tokens"] = getattr(response.usage, "total_tokens", 0) or 0

            self.token_usage.add(
                usage["prompt_tokens"],
                usage["completion_tokens"]
            )

        return usage

    def chat(
        self,
        query: str,
        conversation_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Process a user query and return a response.

        Args:
            query: The user's question or message
            conversation_id: Optional conversation ID for context

        Returns:
            Dictionary containing response, tools used, and metadata
        """
        conversation_id, messages = self._get_or_create_conversation(conversation_id)

        # Add user message
        messages.append({"role": "user", "content": query})

        tools_used = []
        max_tool_iterations = 5  # Prevent infinite loops
        request_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        try:
            for iteration in range(max_tool_iterations):
                # Call the LLM
                response = self.client.chat.completions.create(
                    model=settings.MODEL_NAME,
                    messages=messages,
                    tools=get_tool_schemas(),
                    tool_choice="auto",
                    max_tokens=settings.MAX_TOKENS,
                    temperature=settings.TEMPERATURE,
                )

                # Track token usage
                usage = self._track_usage(response)
                request_usage["prompt_tokens"] += usage["prompt_tokens"]
                request_usage["completion_tokens"] += usage["completion_tokens"]
                request_usage["total_tokens"] += usage["total_tokens"]

                assistant_message = response.choices[0].message

                # Check if we need to execute tools
                if assistant_message.tool_calls:
                    # Add assistant message with tool calls
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in assistant_message.tool_calls
                        ],
                    })

                    # Execute each tool call
                    for tool_call in assistant_message.tool_calls:
                        tool_result = self._execute_tool_call(tool_call)

                        tools_used.append({
                            "name": tool_call.function.name,
                            "arguments": json.loads(tool_call.function.arguments),
                            "result": tool_result,
                        })

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result),
                        })

                    # Continue loop to get final response after tool execution
                    continue

                # No tool calls, we have the final response
                final_response = assistant_message.content or ""

                # Add assistant response to conversation
                messages.append({"role": "assistant", "content": final_response})

                return {
                    "success": True,
                    "response": final_response,
                    "conversation_id": conversation_id,
                    "tools_used": tools_used,
                    "timestamp": datetime.utcnow().isoformat(),
                    "usage": request_usage,
                }

            # If we've exhausted iterations, return what we have
            return {
                "success": True,
                "response": "I apologize, but I encountered an issue processing your request. Please try again.",
                "conversation_id": conversation_id,
                "tools_used": tools_used,
                "timestamp": datetime.utcnow().isoformat(),
                "usage": request_usage,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id,
                "tools_used": tools_used,
                "timestamp": datetime.utcnow().isoformat(),
                "usage": request_usage,
            }

    def get_conversation(self, conversation_id: str) -> Optional[list[dict]]:
        """
        Get a conversation by ID.

        Args:
            conversation_id: The conversation ID

        Returns:
            List of messages or None if not found
        """
        return self.conversations.get(conversation_id)

    def get_all_conversations(self) -> dict[str, list[dict]]:
        """Get all conversations."""
        return self.conversations

    def get_token_usage(self) -> dict:
        """Get cumulative token usage."""
        return self.token_usage.to_dict()

    def reset_token_usage(self):
        """Reset token usage counters."""
        self.token_usage.reset()

    def clear_conversation(self, conversation_id: str) -> bool:
        """
        Clear a conversation.

        Args:
            conversation_id: The conversation ID to clear

        Returns:
            True if cleared, False if not found
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False
