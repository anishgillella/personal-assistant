import urllib.request
import urllib.parse
import json
from typing import Any


class WikipediaTool:
    """Wikipedia search and summary tool for authoritative factual information."""

    name = "wikipedia"
    description = "Search Wikipedia for authoritative information about historical events, scientific concepts, people, places, and general knowledge. Returns summaries from Wikipedia articles."

    # Required by Wikipedia API - must include contact info
    USER_AGENT = "QAChatbot/1.0 (https://github.com/qa-chatbot; qa-chatbot@example.com)"

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
                            "description": "The topic or subject to search on Wikipedia",
                        },
                        "sentences": {
                            "type": "integer",
                            "description": "Number of sentences to return in the summary (default: 5)",
                        },
                    },
                    "required": ["query"],
                },
            },
        }

    def execute(self, query: str, sentences: int = 5) -> dict[str, Any]:
        """
        Search Wikipedia and return a summary.

        Args:
            query: The topic to search for
            sentences: Number of sentences to include in summary

        Returns:
            Dictionary containing the Wikipedia summary
        """
        try:
            # First, search for the page
            search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": 1,
            }

            search_url_full = f"{search_url}?{urllib.parse.urlencode(search_params)}"
            req = urllib.request.Request(search_url_full, headers={"User-Agent": self.USER_AGENT})
            with urllib.request.urlopen(req, timeout=10) as response:
                search_data = json.loads(response.read().decode())

            search_results = search_data.get("query", {}).get("search", [])
            if not search_results:
                return {
                    "success": False,
                    "error": f"No Wikipedia article found for '{query}'",
                    "query": query,
                }

            # Get the page title from search results
            page_title = search_results[0]["title"]

            # Now get the summary
            summary_params = {
                "action": "query",
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "titles": page_title,
                "format": "json",
                "exsentences": min(sentences, 10),
            }

            summary_url = f"{search_url}?{urllib.parse.urlencode(summary_params)}"
            req = urllib.request.Request(summary_url, headers={"User-Agent": self.USER_AGENT})
            with urllib.request.urlopen(req, timeout=10) as response:
                summary_data = json.loads(response.read().decode())

            pages = summary_data.get("query", {}).get("pages", {})
            page = next(iter(pages.values()))

            if "extract" not in page:
                return {
                    "success": False,
                    "error": "Could not extract summary from Wikipedia",
                    "query": query,
                }

            return {
                "success": True,
                "query": query,
                "title": page.get("title", page_title),
                "summary": page["extract"],
                "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(page_title.replace(' ', '_'))}",
            }

        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "query": query,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Wikipedia search error: {str(e)}",
                "query": query,
            }
