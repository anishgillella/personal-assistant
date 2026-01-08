import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Configuration settings for the chatbot."""

    # OpenRouter API configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Model configuration
    MODEL_NAME: str = "google/gemini-2.5-flash"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7

    # SerpAPI configuration
    SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "")

    # System prompt for the agent
    SYSTEM_PROMPT: str = """You are a helpful, intelligent assistant that can answer questions on a wide range of topics.

You have access to the following tools:
1. **search**: Use this to search the web for current information, facts, news, or any topic you need up-to-date information about.
2. **calculator**: Use this for any mathematical calculations, from simple arithmetic to complex expressions.

Guidelines:
- Use tools when they would help provide accurate, up-to-date information
- For factual questions about current events, statistics, or specific data, use the search tool
- For any mathematical calculations, use the calculator tool
- Always provide clear, well-structured responses
- If you're unsure about something, say so rather than making things up
- Be concise but thorough in your answers"""

    # App configuration
    APP_NAME: str = "QA Chatbot"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


settings = Settings()
