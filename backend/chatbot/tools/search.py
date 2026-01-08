from typing import Any
from serpapi import GoogleSearch
from chatbot.config import settings


class SearchTool:
    """Web search tool using SerpAPI."""

    name = "search"
    description = "Search the web for current information, facts, news, or any topic. Use this for questions about recent events, statistics, or specific factual data."

    def get_schema(self) -> dict:
        """Return OpenAI-compatible function schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to look up on the web",
                        }
                    },
                    "required": ["query"],
                },
            },
        }

    def execute(self, query: str) -> dict[str, Any]:
        """
        Execute a web search using SerpAPI.

        Args:
            query: The search query

        Returns:
            Dictionary containing search results
        """
        try:
            if not settings.SERPAPI_API_KEY:
                return {
                    "success": False,
                    "error": "SerpAPI key not configured",
                    "results": [],
                }

            params = {
                "q": query,
                "api_key": settings.SERPAPI_API_KEY,
                "engine": "google",
                "num": 5,  # Get top 5 results
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            # Extract organic results
            organic_results = results.get("organic_results", [])

            formatted_results = []
            for result in organic_results[:5]:
                formatted_results.append(
                    {
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "link": result.get("link", ""),
                    }
                )

            # Also check for answer box or knowledge graph
            answer_box = results.get("answer_box", {})
            knowledge_graph = results.get("knowledge_graph", {})

            summary = ""
            if answer_box:
                summary = answer_box.get("answer") or answer_box.get("snippet", "")
            elif knowledge_graph:
                summary = knowledge_graph.get("description", "")

            return {
                "success": True,
                "query": query,
                "summary": summary,
                "results": formatted_results,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": [],
            }
