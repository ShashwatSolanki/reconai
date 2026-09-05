from __future__ import annotations

from dataclasses import dataclass

from app.domain.evaluation import GroundTruth
from app.domain.reconciliation import ReconciliationResult
from app.services.evaluation_ground_truth_generator import (
    EvaluationGroundTruthGenerator,
)
from app.services.evaluation_metrics import EvaluationMetrics, EvaluationMetricsResult
from app.services.reconciliation_engine import ReconciliationEngine
from app.services.synthetic_data_generator import SyntheticDataGenerator


@dataclass(frozen=True, slots=True)
class EvaluationRunResult:
    """Complete output produced by one evaluation run."""

    seed: int
    record_count: int
    total_transactions: int
    total_settlements: int
    ground_truth: list[GroundTruth]
    reconciliation_results: list[ReconciliationResult]
    metrics: EvaluationMetricsResult


class EvaluationRunner:
    """Run the complete deterministic reconciliation evaluation pipeline."""

    def __init__(
        self,
        seed: int = 42,
        record_count: int = 100,
    ) -> None:
        self._seed = seed
        self._record_count = record_count
        self._synthetic_generator = SyntheticDataGenerator(
            seed=seed,
            record_count=record_count,
        )
        self._ground_truth_generator = EvaluationGroundTruthGenerator()
        self._reconciliation_engine = ReconciliationEngine()
        self._metrics = EvaluationMetrics()

    def run(self) -> EvaluationRunResult:
        """Generate data, reconcile it, and calculate evaluation metrics."""
        transactions, settlements = self._synthetic_generator.generate()

        ground_truth = self._ground_truth_generator.generate(
            transactions=transactions,
            settlements=settlements,
        )

        reconciliation_results = [
            self._reconciliation_engine.reconcile(
                transaction=transaction,
                settlements=settlements,
            )
            for transaction in transactions
        ]

        metrics = self._metrics.calculate(
            ground_truth=ground_truth,
            results=reconciliation_results,
        )

        return EvaluationRunResult(
            seed=self._seed,
            record_count=self._record_count,
            total_transactions=len(transactions),
            total_settlements=len(settlements),
            ground_truth=ground_truth,
            reconciliation_results=reconciliation_results,
            metrics=metrics,
        )
