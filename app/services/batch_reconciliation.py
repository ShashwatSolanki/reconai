from __future__ import annotations

from app.domain.batch_reconciliation import BatchReconciliationSummary
from app.domain.reconciliation import ReconciliationResult, ReconciliationStatus
from app.domain.settlement import Settlement
from app.domain.transaction import Transaction
from app.services.reconciliation_engine import ReconciliationEngine


class BatchReconciliationService:
    """Reconcile a collection of transactions against settlement records."""

    def __init__(self, engine: ReconciliationEngine) -> None:
        self._engine = engine

    def reconcile(
        self,
        transactions: list[Transaction],
        settlements: list[Settlement],
    ) -> list[ReconciliationResult]:
        """Reconcile all transactions while preserving transaction order."""

        return [
            self._engine.reconcile(
                transaction=transaction,
                settlements=[
                    settlement
                    for settlement in settlements
                    if settlement.transaction_reference == transaction.transaction_id
                ],
            )
            for transaction in transactions
        ]

    def summarize(
        self,
        results: list[ReconciliationResult],
    ) -> BatchReconciliationSummary:
        """Summarize reconciliation results by status."""

        counts = {
            status: sum(result.status == status for result in results)
            for status in ReconciliationStatus
        }

        return BatchReconciliationSummary(
            total_transactions=len(results),
            matched=counts[ReconciliationStatus.MATCHED],
            partial_matches=counts[ReconciliationStatus.PARTIAL_MATCH],
            mismatches=counts[ReconciliationStatus.MISMATCH],
            missing_settlements=counts[ReconciliationStatus.MISSING_SETTLEMENT],
            duplicates=counts[ReconciliationStatus.DUPLICATE],
        )