from __future__ import annotations

from dataclasses import dataclass

from app.domain.evaluation import GroundTruth
from app.domain.reconciliation import (
    ReconciliationResult,
    ReconciliationStatus,
)


@dataclass(frozen=True, slots=True)
class EvaluationMetricsResult:
    """Evaluation metrics calculated from ground truth and predictions."""

    total_transactions: int
    correct_status_predictions: int
    status_accuracy: float
    actual_exceptions: int
    predicted_exceptions: int
    true_positive_exceptions: int
    exception_precision: float
    exception_recall: float


class EvaluationMetrics:
    """Calculate reconciliation and exception-detection metrics."""

    def calculate(
        self,
        ground_truth: list[GroundTruth],
        results: list[ReconciliationResult],
    ) -> EvaluationMetricsResult:
        """Compare reconciliation results against known ground truth."""

        if len(ground_truth) != len(results):
            raise ValueError(
                "Ground truth and reconciliation results must have the same length."
            )

        total_transactions = len(ground_truth)

        correct_status_predictions = sum(
            truth.expected_status.value == result.status.value
            for truth, result in zip(ground_truth, results, strict=True)
        )

        actual_exceptions = sum(item.has_exception for item in ground_truth)

        predicted_exceptions = sum(
            result.status != ReconciliationStatus.MATCHED
            for result in results
        )

        true_positive_exceptions = sum(
            truth.has_exception and result.status != ReconciliationStatus.MATCHED
            for truth, result in zip(ground_truth, results, strict=True)
        )

        status_accuracy = (
            correct_status_predictions / total_transactions
            if total_transactions
            else 0.0
        )

        exception_precision = (
            true_positive_exceptions / predicted_exceptions
            if predicted_exceptions
            else 0.0
        )

        exception_recall = (
            true_positive_exceptions / actual_exceptions
            if actual_exceptions
            else 0.0
        )

        return EvaluationMetricsResult(
            total_transactions=total_transactions,
            correct_status_predictions=correct_status_predictions,
            status_accuracy=status_accuracy,
            actual_exceptions=actual_exceptions,
            predicted_exceptions=predicted_exceptions,
            true_positive_exceptions=true_positive_exceptions,
            exception_precision=exception_precision,
            exception_recall=exception_recall,
        )