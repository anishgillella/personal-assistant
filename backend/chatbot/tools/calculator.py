import math
import re
from typing import Any


class CalculatorTool:
    """Safe mathematical calculator tool."""

    name = "calculator"
    description = "Perform mathematical calculations. Supports basic arithmetic (+, -, *, /), exponents (**), parentheses, and math functions like sqrt, sin, cos, tan, log, abs, round, floor, ceil."

    # Safe functions and constants allowed in calculations
    SAFE_FUNCTIONS = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow,
        # Math module functions
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "log": math.log,
        "log10": math.log10,
        "log2": math.log2,
        "exp": math.exp,
        "floor": math.floor,
        "ceil": math.ceil,
        "factorial": math.factorial,
        "gcd": math.gcd,
        "radians": math.radians,
        "degrees": math.degrees,
    }

    SAFE_CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
    }

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
                        "expression": {
                            "type": "string",
                            "description": "The mathematical expression to evaluate (e.g., '2 + 2', 'sqrt(16)', '3 * (4 + 5)')",
                        }
                    },
                    "required": ["expression"],
                },
            },
        }

    def _validate_expression(self, expression: str) -> bool:
        """
        Validate that the expression only contains safe characters and functions.

        Args:
            expression: The mathematical expression to validate

        Returns:
            True if valid, False otherwise
        """
        # Allow: numbers, operators, parentheses, decimal points, spaces, and function names
        allowed_pattern = r'^[\d\s\+\-\*\/\.\(\)\,\%\^a-zA-Z_]+$'
        if not re.match(allowed_pattern, expression):
            return False

        # Check for any potentially dangerous patterns
        dangerous_patterns = [
            r'__',  # Dunder methods
            r'import',
            r'exec',
            r'eval',
            r'open',
            r'file',
            r'input',
            r'print',
            r'os\.',
            r'sys\.',
            r'subprocess',
        ]

        expression_lower = expression.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, expression_lower):
                return False

        return True

    def execute(self, expression: str) -> dict[str, Any]:
        """
        Safely evaluate a mathematical expression.

        Args:
            expression: The mathematical expression to evaluate

        Returns:
            Dictionary containing the result or error
        """
        try:
            # Clean up the expression
            expression = expression.strip()

            # Replace ^ with ** for exponentiation
            expression = expression.replace("^", "**")

            # Validate the expression
            if not self._validate_expression(expression):
                return {
                    "success": False,
                    "error": "Invalid expression. Only mathematical operations are allowed.",
                    "expression": expression,
                }

            # Create safe evaluation context
            safe_dict = {
                "__builtins__": {},
                **self.SAFE_FUNCTIONS,
                **self.SAFE_CONSTANTS,
            }

            # Evaluate the expression
            result = eval(expression, safe_dict)

            # Handle complex numbers
            if isinstance(result, complex):
                if result.imag == 0:
                    result = result.real
                else:
                    return {
                        "success": True,
                        "expression": expression,
                        "result": f"{result.real} + {result.imag}i",
                        "type": "complex",
                    }

            # Round to avoid floating point issues for display
            if isinstance(result, float):
                # Keep precision but remove floating point artifacts
                result = round(result, 10)
                # Remove trailing zeros
                if result == int(result):
                    result = int(result)

            return {
                "success": True,
                "expression": expression,
                "result": result,
                "type": type(result).__name__,
            }

        except ZeroDivisionError:
            return {
                "success": False,
                "error": "Division by zero",
                "expression": expression,
            }
        except ValueError as e:
            return {
                "success": False,
                "error": f"Math error: {str(e)}",
                "expression": expression,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Calculation error: {str(e)}",
                "expression": expression,
            }
