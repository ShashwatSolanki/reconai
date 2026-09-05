from __future__ import annotations

from typing import Protocol

from app.domain.batch_reconciliation import BatchReconciliationSummary
from app.domain.reconciliation import ReconciliationResult
from app.domain.settlement import Settlement
from app.domain.transaction import Transaction
from app.services.batch_reconciliation import BatchReconciliationService


class TransactionRepositoryProtocol(Protocol):
    """Repository contract required by persisted reconciliation."""

    def get_by_merchant(self, merchant_id: str) -> list[Transaction]:
        ...


class SettlementRepositoryProtocol(Protocol):
    """Repository contract required by persisted reconciliation."""

    def get_by_merchant(self, merchant_id: str) -> list[Settlement]:
        ...


class PersistedReconciliationService:
    """Reconcile persisted transactions against persisted settlements."""

    def __init__(
        self,
        transaction_repository: TransactionRepositoryProtocol,
        settlement_repository: SettlementRepositoryProtocol,
        reconciliation_service: BatchReconciliationService,
    ) -> None:
        self._transaction_repository = transaction_repository
        self._settlement_repository = settlement_repository
        self._reconciliation_service = reconciliation_service

    def reconcile_merchant(self, merchant_id: str) -> list[ReconciliationResult]:
        transactions = self._transaction_repository.get_by_merchant(merchant_id)
        settlements = self._settlement_repository.get_by_merchant(merchant_id)

        return self._reconciliation_service.reconcile(
            transactions=transactions,
            settlements=settlements,
        )

    def summarize(
        self,
        results: list[ReconciliationResult],
    ) -> BatchReconciliationSummary:
        return self._reconciliation_service.summarize(results)