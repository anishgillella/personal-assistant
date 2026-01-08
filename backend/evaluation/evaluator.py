import json
from typing import Any, Callable, Optional
from datetime import datetime
import numpy as np

from evaluation.dataset import DatasetLoader
from evaluation.metrics import MetricsCalculator
from chatbot.agent import ChatAgent


class Evaluator:
    """
    Evaluator for running comprehensive chatbot evaluations.
    """

    def __init__(self, chat_agent: ChatAgent):
        """
        Initialize the evaluator.

        Args:
            chat_agent: The chat agent to evaluate
        """
        self.chat_agent = chat_agent
        self.metrics_calculator = MetricsCalculator()
        self.dataset_loader = DatasetLoader()

    def evaluate_single(
        self,
        question: str,
        expected_answer: str,
        expected_tools: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Evaluate a single question-answer pair.

        Args:
            question: The question to ask
            expected_answer: The expected answer
            expected_tools: Optional list of expected tools

        Returns:
            Evaluation result for this item
        """
        # Get response from chatbot (use new conversation each time for isolation)
        response = self.chat_agent.chat(query=question, conversation_id=None)

        actual_response = response.get("response", "")
        actual_tools = [t["name"] for t in response.get("tools_used", [])]

        # Calculate all metrics
        metrics = self.metrics_calculator.calculate_all_metrics(
            question=question,
            expected_answer=expected_answer,
            actual_response=actual_response,
            expected_tools=expected_tools,
            actual_tools=actual_tools,
        )

        # Calculate overall score (weighted average)
        weights = {
            "relevance": 0.25,
            "accuracy": 0.30,
            "completeness": 0.20,
            "coherence": 0.10,
            "tool_usage": 0.15,
        }

        overall_score = sum(
            metrics[m]["score"] * weights[m] for m in weights
        )

        return {
            "question": question,
            "expected_answer": expected_answer,
            "actual_response": actual_response,
            "tools_used": actual_tools,
            "metrics": [
                {
                    "name": name,
                    "score": data["score"],
                    "details": data.get("explanation", ""),
                }
                for name, data in metrics.items()
            ],
            "overall_score": round(overall_score, 3),
        }

    def run_evaluation(
        self,
        dataset_path: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> dict[str, Any]:
        """
        Run evaluation on a dataset.

        Args:
            dataset_path: Path to the evaluation dataset JSON file
            progress_callback: Optional callback for progress updates

        Returns:
            Complete evaluation results
        """
        # Load dataset
        dataset = self.dataset_loader.load(dataset_path)
        total = len(dataset)

        results = []
        metric_scores = {
            "relevance": [],
            "accuracy": [],
            "completeness": [],
            "coherence": [],
            "tool_usage": [],
        }

        for i, item in enumerate(dataset):
            if progress_callback:
                progress_callback(i + 1, total)

            # Evaluate single item
            result = self.evaluate_single(
                question=item["question"],
                expected_answer=item["expected_answer"],
                expected_tools=item.get("expected_tools"),
            )

            results.append(result)

            # Collect metric scores
            for metric in result["metrics"]:
                metric_name = metric["name"]
                if metric_name in metric_scores:
                    metric_scores[metric_name].append(metric["score"])

        # Calculate averages
        metric_averages = {
            name: round(float(np.mean(scores)), 3) if scores else 0.0
            for name, scores in metric_scores.items()
        }

        overall_scores = [r["overall_score"] for r in results]
        average_score = round(float(np.mean(overall_scores)), 3) if overall_scores else 0.0

        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "total_questions": total,
            "average_score": average_score,
            "metric_averages": metric_averages,
            "results": results,
        }


# CLI entry point for running evaluation standalone
if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Run chatbot evaluation")
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/evaluation_dataset.json",
        help="Path to evaluation dataset",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/results/evaluation_results.json",
        help="Path to save results",
    )

    args = parser.parse_args()

    # Initialize
    agent = ChatAgent()
    evaluator = Evaluator(agent)

    print(f"Running evaluation on {args.dataset}...")

    def progress(current, total):
        print(f"Progress: {current}/{total}")

    results = evaluator.run_evaluation(
        dataset_path=args.dataset,
        progress_callback=progress,
    )

    # Save results
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nEvaluation complete!")
    print(f"Average Score: {results['average_score']}")
    print(f"Metric Averages: {results['metric_averages']}")
    print(f"Results saved to {args.output}")
