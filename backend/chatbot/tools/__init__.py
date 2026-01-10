from chatbot.tools.search import SearchTool
from chatbot.tools.calculator import CalculatorTool
from chatbot.tools.wikipedia import WikipediaTool
from chatbot.tools.weather import WeatherTool
from chatbot.tools.code_executor import CodeExecutorTool
from chatbot.tools.unit_converter import UnitConverterTool
from chatbot.tools.datetime_tool import DateTimeTool

# Tool registry
AVAILABLE_TOOLS = {
    "search": SearchTool(),
    "calculator": CalculatorTool(),
    "wikipedia": WikipediaTool(),
    "weather": WeatherTool(),
    "code_executor": CodeExecutorTool(),
    "unit_converter": UnitConverterTool(),
    "datetime": DateTimeTool(),
}


def get_tool(name: str):
    """Get a tool by name."""
    return AVAILABLE_TOOLS.get(name)


def get_all_tools():
    """Get all available tools."""
    return AVAILABLE_TOOLS


def get_tool_schemas():
    """Get OpenAI-compatible tool schemas for all tools."""
    return [tool.get_schema() for tool in AVAILABLE_TOOLS.values()]


__all__ = [
    "SearchTool",
    "CalculatorTool",
    "WikipediaTool",
    "WeatherTool",
    "CodeExecutorTool",
    "UnitConverterTool",
    "DateTimeTool",
    "AVAILABLE_TOOLS",
    "get_tool",
    "get_all_tools",
    "get_tool_schemas",
]
