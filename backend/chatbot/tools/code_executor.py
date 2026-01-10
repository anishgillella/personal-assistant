import ast
import sys
import io
import math
import json
import re
from typing import Any
from contextlib import redirect_stdout, redirect_stderr


class CodeExecutorTool:
    """Safe Python code executor with sandboxed environment."""

    name = "code_executor"
    description = "Execute Python code in a safe sandbox. Supports basic operations, math, string manipulation, list operations, and simple algorithms. Prints and return values are captured."

    # Maximum execution time equivalent (we limit operations instead)
    MAX_ITERATIONS = 10000
    MAX_OUTPUT_LENGTH = 5000

    # Safe built-in functions
    SAFE_BUILTINS = {
        "abs": abs,
        "all": all,
        "any": any,
        "bin": bin,
        "bool": bool,
        "chr": chr,
        "dict": dict,
        "divmod": divmod,
        "enumerate": enumerate,
        "filter": filter,
        "float": float,
        "format": format,
        "frozenset": frozenset,
        "hex": hex,
        "int": int,
        "isinstance": isinstance,
        "len": len,
        "list": list,
        "map": map,
        "max": max,
        "min": min,
        "oct": oct,
        "ord": ord,
        "pow": pow,
        "print": print,
        "range": range,
        "repr": repr,
        "reversed": reversed,
        "round": round,
        "set": set,
        "slice": slice,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "type": type,
        "zip": zip,
    }

    # Safe math functions
    SAFE_MATH = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "floor": math.floor,
        "ceil": math.ceil,
        "pi": math.pi,
        "e": math.e,
        "factorial": math.factorial,
        "gcd": math.gcd,
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
                        "code": {
                            "type": "string",
                            "description": "The Python code to execute. Keep it simple and focused.",
                        }
                    },
                    "required": ["code"],
                },
            },
        }

    def _validate_code(self, code: str) -> tuple[bool, str]:
        """
        Validate code for safety.

        Args:
            code: The Python code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Parse the code into an AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"

        # Disallowed patterns
        dangerous_attrs = {
            "__import__",
            "__builtins__",
            "__class__",
            "__bases__",
            "__subclasses__",
            "__mro__",
            "__code__",
            "__globals__",
            "__dict__",
            "__getattribute__",
            "__setattr__",
            "__delattr__",
        }

        dangerous_names = {
            "eval",
            "exec",
            "compile",
            "open",
            "input",
            "file",
            "os",
            "sys",
            "subprocess",
            "importlib",
            "builtins",
            "globals",
            "locals",
            "vars",
            "dir",
            "getattr",
            "setattr",
            "delattr",
            "breakpoint",
        }

        for node in ast.walk(tree):
            # Check for import statements
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                return False, "Import statements are not allowed"

            # Check for attribute access to dangerous attributes
            if isinstance(node, ast.Attribute):
                if node.attr in dangerous_attrs:
                    return False, f"Access to '{node.attr}' is not allowed"

            # Check for calls to dangerous functions
            if isinstance(node, ast.Name):
                if node.id in dangerous_names:
                    return False, f"Use of '{node.id}' is not allowed"

            # Check for with statements (could be used for file operations)
            if isinstance(node, ast.With):
                return False, "With statements are not allowed"

            # Limit recursion depth by checking function definitions
            if isinstance(node, ast.FunctionDef):
                # Check for deeply nested functions (potential for recursion attacks)
                nested_funcs = sum(
                    1 for n in ast.walk(node) if isinstance(n, ast.FunctionDef)
                )
                if nested_funcs > 3:
                    return False, "Too many nested function definitions"

        return True, ""

    def execute(self, code: str) -> dict[str, Any]:
        """
        Execute Python code in a sandboxed environment.

        Args:
            code: The Python code to execute

        Returns:
            Dictionary containing execution result
        """
        try:
            # Validate the code first
            is_valid, error_msg = self._validate_code(code)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg,
                    "code": code[:500],
                }

            # Create sandboxed globals
            sandbox_globals = {
                "__builtins__": self.SAFE_BUILTINS,
                "math": type("math", (), self.SAFE_MATH)(),
            }
            # Add math functions directly to namespace
            sandbox_globals.update(self.SAFE_MATH)

            # Capture stdout and stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            # Execute the code
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Compile and execute
                compiled = compile(code, "<sandbox>", "exec")
                exec(compiled, sandbox_globals)

            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()

            # Get any result variable if defined
            result = sandbox_globals.get("result", None)

            # Truncate output if too long
            if len(stdout_output) > self.MAX_OUTPUT_LENGTH:
                stdout_output = (
                    stdout_output[: self.MAX_OUTPUT_LENGTH] + "\n... (output truncated)"
                )

            return {
                "success": True,
                "output": stdout_output.strip() if stdout_output else None,
                "result": (
                    str(result) if result is not None else None
                ),
                "error_output": stderr_output.strip() if stderr_output else None,
                "code": code[:500] + ("..." if len(code) > 500 else ""),
            }

        except Exception as e:
            error_type = type(e).__name__
            return {
                "success": False,
                "error": f"{error_type}: {str(e)}",
                "code": code[:500],
            }
