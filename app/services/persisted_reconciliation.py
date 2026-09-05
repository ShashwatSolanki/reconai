from __future__ import annotations

from app.domain.reconciliation import ReconciliationResult
from app.repositories.settlement_repository import SettlementRepository
from app.repositories.transaction_repository import TransactionRepository
from app.services.batch_reconciliation import BatchReconciliationService


class PersistedReconciliationService:
    """Reconcile persisted transactions against persisted settlements."""

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        settlement_repository: SettlementRepository,
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