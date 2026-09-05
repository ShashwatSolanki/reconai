from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from time import perf_counter

from app.domain.controller_evaluation import (
    BatchControllerResult,
    ControllerExceptionOutcome,
)
from app.domain.exception import ExceptionCategory
from app.domain.reconciliation import ReconciliationStatus
from app.domain.settlement import Settlement
from app.services.batch_reconciliation import BatchReconciliationService
from app.services.evaluation_ground_truth_generator import (
    EvaluationGroundTruthGenerator,
)
from app.services.evaluation_metrics import EvaluationMetrics
from app.services.reconai_service import ReconAIService
from app.services.reconciliation_engine import ReconciliationEngine
from app.services.synthetic_data_generator import SyntheticDataGenerator


class FinanceController:
    """Run the bounded reconciliation, investigation, and decision workflow."""

    def __init__(
        self,
        reconai_service: ReconAIService,
        seed: int = 42,
        record_count: int = 100,
        timer: Callable[[], float] = perf_counter,
    ) -> None:
        self._reconai_service = reconai_service
        self._seed = seed
        self._synthetic_generator = SyntheticDataGenerator(
            seed=seed,
            record_count=record_count,
        )
        self._ground_truth_generator = EvaluationGroundTruthGenerator()
        self._reconciliation_service = BatchReconciliationService(ReconciliationEngine())
        self._metrics = EvaluationMetrics()
        self._timer = timer

    def run(self) -> BatchControllerResult:
        """Process a synthetic batch and investigate only detected exceptions."""

        started_at = self._timer()
        transactions, settlements = self._synthetic_generator.generate()
        ground_truth = self._ground_truth_generator.generate(transactions, settlements)
        reconciliation_results = self._reconciliation_service.reconcile(
            transactions,
            settlements,
        )
        reconciliation_summary = self._reconciliation_service.summarize(
            reconciliation_results
        )
        self._reconai_service.record_reconciliation_summary(
            total_transactions=reconciliation_summary.total_transactions,
            matched=reconciliation_summary.matched,
            partial_matches=reconciliation_summary.partial_matches,
            mismatches=reconciliation_summary.mismatches,
            missing_settlements=reconciliation_summary.missing_settlements,
            duplicates=reconciliation_summary.duplicates,
        )

        transaction_by_id = {
            transaction.transaction_id: transaction for transaction in transactions
        }
        settlements_by_transaction = self._settlements_by_transaction(settlements)
        outcomes: list[ControllerExceptionOutcome] = []

        for result in reconciliation_results:
            if result.status == ReconciliationStatus.MATCHED:
                continue

            transaction = transaction_by_id[result.transaction_id]
            settlement = self._settlement_for_result(
                result.transaction_id,
                settlements_by_transaction,
            )
            exception = self._reconai_service.register_exception(
                result=result,
                transaction=transaction,
                settlement=settlement,
            )

            if exception is None:
                continue

            workflow = self._reconai_service.investigate(exception.exception_id)
            outcomes.append(
                ControllerExceptionOutcome(
                    exception=exception,
                    investigation=workflow["investigation"],
                    action=workflow["action"],
                )
            )

        metrics = self._metrics.calculate(ground_truth, reconciliation_results)
        elapsed = self._timer() - started_at
        resolved_records = sum(outcome.action.executed for outcome in outcomes)
        escalated_records = sum(
            outcome.action.requires_human_review for outcome in outcomes
        )
        exception_breakdown = Counter(
            outcome.exception.category for outcome in outcomes
        )
        average_confidence = (
            sum(outcome.investigation.confidence for outcome in outcomes) / len(outcomes)
            if outcomes
            else 0.0
        )

        return BatchControllerResult(
            seed=self._seed,
            total_records=len(transactions),
            matched_records=reconciliation_summary.matched,
            exception_records=len(outcomes),
            investigated_records=len(outcomes),
            resolved_records=resolved_records,
            escalated_records=escalated_records,
            unresolved_records=len(outcomes) - resolved_records - escalated_records,
            status_accuracy=metrics.status_accuracy,
            exception_precision=metrics.exception_precision,
            exception_recall=metrics.exception_recall,
            processing_time_seconds=elapsed,
            throughput_records_per_second=(len(transactions) / elapsed if elapsed else 0.0),
            average_investigation_confidence=average_confidence,
            exception_breakdown={
                category: exception_breakdown.get(category, 0)
                for category in ExceptionCategory
            },
            exception_outcomes=outcomes,
        )

    @staticmethod
    def _settlements_by_transaction(
        settlements: list[Settlement],
    ) -> dict[str, list[Settlement]]:
        grouped: dict[str, list[Settlement]] = {}
        for settlement in settlements:
            grouped.setdefault(settlement.transaction_reference, []).append(settlement)
        return grouped

    @staticmethod
    def _settlement_for_result(
        transaction_id: str,
        settlements_by_transaction: dict[str, list[Settlement]],
    ) -> Settlement | None:
        """Provide a representative settlement as evidence for duplicate cases."""

        candidates = settlements_by_transaction.get(transaction_id, [])
        return candidates[0] if candidates else None
