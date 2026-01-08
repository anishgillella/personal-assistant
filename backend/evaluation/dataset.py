import json
from typing import Any
from pathlib import Path


class DatasetLoader:
    """Loader for evaluation datasets."""

    @staticmethod
    def load(path: str) -> list[dict[str, Any]]:
        """
        Load an evaluation dataset from a JSON file.

        Args:
            path: Path to the JSON file

        Returns:
            List of evaluation items

        Expected format:
        [
            {
                "question": "What is 2 + 2?",
                "expected_answer": "4",
                "category": "math",  # optional
                "expected_tools": ["calculator"]  # optional
            },
            ...
        ]
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found: {path}")

        with open(path, "r") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("Dataset must be a JSON array")

        # Validate each item
        for i, item in enumerate(data):
            if "question" not in item:
                raise ValueError(f"Item {i} missing 'question' field")
            if "expected_answer" not in item:
                raise ValueError(f"Item {i} missing 'expected_answer' field")

        return data

    @staticmethod
    def save(data: list[dict[str, Any]], path: str) -> None:
        """
        Save an evaluation dataset to a JSON file.

        Args:
            data: List of evaluation items
            path: Path to save the JSON file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(data, f, indent=2)
