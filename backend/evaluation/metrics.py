import re
import json
from typing import Any, Optional
from openai import OpenAI
from chatbot.config import settings


class MetricsCalculator:
    """
    Calculator for evaluation metrics using LLM-as-judge approach.
    """

    def __init__(self):
        """Initialize with OpenRouter client for LLM-based evaluation."""
        self.client = OpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
        )

    def _llm_judge(
        self,
        question: str,
        expected_answer: str,
        actual_response: str,
        metric_name: str,
        metric_description: str,
    ) -> dict[str, Any]:
        """
        Use LLM as a judge to score a specific metric.

        Args:
            question: The original question
            expected_answer: The expected/reference answer
            actual_response: The chatbot's actual response
            metric_name: Name of the metric being evaluated
            metric_description: Description of what the metric measures

        Returns:
            Dictionary with score (0-1) and explanation
        """
        prompt = f"""You are an expert evaluator assessing the quality of a chatbot's response.

Question: {question}

Expected Answer: {expected_answer}

Actual Response: {actual_response}

Evaluate the actual response for the following metric:
**{metric_name}**: {metric_description}

Provide your evaluation in the following JSON format:
{{
    "score": <float between 0 and 1>,
    "explanation": "<brief explanation of the score>"
}}

Score Guidelines:
- 1.0: Perfect/Excellent
- 0.8: Very Good
- 0.6: Good/Acceptable
- 0.4: Below Average
- 0.2: Poor
- 0.0: Completely Wrong/Missing

Respond ONLY with the JSON object, no additional text."""

        try:
            response = self.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=256,
                temperature=0.1,  # Low temperature for consistent evaluation
            )

            content = response.choices[0].message.content.strip()

            # Try to parse JSON from response
            # Handle cases where the response might have markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)

            return {
                "score": float(result.get("score", 0)),
                "explanation": result.get("explanation", ""),
            }

        except Exception as e:
            # Fallback to simple heuristic if LLM fails
            return {
                "score": 0.5,
                "explanation": f"LLM evaluation failed: {str(e)}",
            }

    def calculate_relevance(
        self,
        question: str,
        expected_answer: str,
        actual_response: str,
    ) -> dict[str, Any]:
        """
        Calculate relevance score: How well does the response address the question?
        """
        return self._llm_judge(
            question=question,
            expected_answer=expected_answer,
            actual_response=actual_response,
            metric_name="Relevance",
            metric_description="How directly and appropriately does the response address the user's question? Does it stay on topic and provide information the user asked for?",
        )

    def calculate_accuracy(
        self,
        question: str,
        expected_answer: str,
        actual_response: str,
    ) -> dict[str, Any]:
        """
        Calculate accuracy score: Is the information factually correct?
        """
        return self._llm_judge(
            question=question,
            expected_answer=expected_answer,
            actual_response=actual_response,
            metric_name="Accuracy",
            metric_description="Is the factual information in the response correct? Compare against the expected answer and check for any errors, hallucinations, or incorrect statements.",
        )

    def calculate_completeness(
        self,
        question: str,
        expected_answer: str,
        actual_response: str,
    ) -> dict[str, Any]:
        """
        Calculate completeness score: Does the response cover all aspects?
        """
        return self._llm_judge(
            question=question,
            expected_answer=expected_answer,
            actual_response=actual_response,
            metric_name="Completeness",
            metric_description="Does the response fully answer the question? Are all important aspects covered? Is there any key information missing that was in the expected answer?",
        )

    def calculate_coherence(
        self,
        question: str,
        expected_answer: str,
        actual_response: str,
    ) -> dict[str, Any]:
        """
        Calculate coherence score: Is the response well-structured and readable?
        """
        return self._llm_judge(
            question=question,
            expected_answer=expected_answer,
            actual_response=actual_response,
            metric_name="Coherence",
            metric_description="Is the response well-organized, logically structured, and easy to understand? Does it flow naturally and use clear language?",
        )

    def calculate_tool_usage(
        self,
        question: str,
        expected_tools: Optional[list[str]],
        actual_tools: list[str],
    ) -> dict[str, Any]:
        """
        Calculate tool usage score: Were the right tools used appropriately?

        Args:
            question: The original question
            expected_tools: List of tools that should have been used
            actual_tools: List of tools that were actually used

        Returns:
            Dictionary with score and explanation
        """
        if expected_tools is None:
            # If no expected tools specified, give full score if any tools used appropriately
            # or partial score based on whether tools seem relevant
            if not actual_tools:
                return {
                    "score": 0.7,
                    "explanation": "No tools used, but no specific tools were expected",
                }
            return {
                "score": 0.8,
                "explanation": f"Tools used: {', '.join(actual_tools)}",
            }

        if not expected_tools and not actual_tools:
            return {
                "score": 1.0,
                "explanation": "Correctly used no tools as expected",
            }

        if not expected_tools and actual_tools:
            return {
                "score": 0.6,
                "explanation": f"Used tools ({', '.join(actual_tools)}) when none were expected",
            }

        if expected_tools and not actual_tools:
            return {
                "score": 0.2,
                "explanation": f"Expected tools ({', '.join(expected_tools)}) but none were used",
            }

        # Calculate overlap
        expected_set = set(expected_tools)
        actual_set = set(actual_tools)

        correct_tools = expected_set & actual_set
        missing_tools = expected_set - actual_set
        extra_tools = actual_set - expected_set

        # Score based on correct tools
        precision = len(correct_tools) / len(actual_set) if actual_set else 0
        recall = len(correct_tools) / len(expected_set) if expected_set else 0

        # F1-like score
        if precision + recall > 0:
            score = 2 * (precision * recall) / (precision + recall)
        else:
            score = 0

        explanation_parts = []
        if correct_tools:
            explanation_parts.append(f"Correctly used: {', '.join(correct_tools)}")
        if missing_tools:
            explanation_parts.append(f"Missing: {', '.join(missing_tools)}")
        if extra_tools:
            explanation_parts.append(f"Extra: {', '.join(extra_tools)}")

        return {
            "score": score,
            "explanation": ". ".join(explanation_parts),
        }

    def calculate_all_metrics(
        self,
        question: str,
        expected_answer: str,
        actual_response: str,
        expected_tools: Optional[list[str]] = None,
        actual_tools: Optional[list[str]] = None,
    ) -> dict[str, dict[str, Any]]:
        """
        Calculate all metrics for a response.

        Returns:
            Dictionary mapping metric names to their scores and explanations
        """
        metrics = {
            "relevance": self.calculate_relevance(
                question, expected_answer, actual_response
            ),
            "accuracy": self.calculate_accuracy(
                question, expected_answer, actual_response
            ),
            "completeness": self.calculate_completeness(
                question, expected_answer, actual_response
            ),
            "coherence": self.calculate_coherence(
                question, expected_answer, actual_response
            ),
            "tool_usage": self.calculate_tool_usage(
                question, expected_tools, actual_tools or []
            ),
        }

        return metrics
