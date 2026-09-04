from __future__ import annotations

from app.domain.money import Money
from app.domain.reconciliation import ReconciliationResult, ReconciliationStatus
from app.domain.settlement import Settlement
from app.domain.transaction import Transaction


class ReconciliationEngine:
    """Deterministic engine for reconciling transactions against settlements."""

    def reconcile(
        self,
        transaction: Transaction,
        settlements: list[Settlement],
    ) -> ReconciliationResult:
        """Reconcile one transaction against its candidate settlements."""

        matching_settlements = [
            settlement
            for settlement in settlements
            if settlement.transaction_reference == transaction.transaction_id
        ]

        if not matching_settlements:
            return ReconciliationResult(
                transaction_id=transaction.transaction_id,
                settlement_id=None,
                status=ReconciliationStatus.MISSING_SETTLEMENT,
                expected_amount=transaction.amount,
                actual_amount=None,
                difference=None,
                reason="No settlement record was found for the transaction.",
            )

        if len(matching_settlements) > 1:
            return ReconciliationResult(
                transaction_id=transaction.transaction_id,
                settlement_id=None,
                status=ReconciliationStatus.DUPLICATE,
                expected_amount=transaction.amount,
                actual_amount=None,
                difference=None,
                reason="Multiple settlement records reference the same transaction.",
            )

        settlement = matching_settlements[0]

        if settlement.amount == transaction.amount:
            return ReconciliationResult(
                transaction_id=transaction.transaction_id,
                settlement_id=settlement.settlement_id,
                status=ReconciliationStatus.MATCHED,
                expected_amount=transaction.amount,
                actual_amount=settlement.amount,
                difference=Money(0),
                reason="Transaction and settlement amounts match exactly.",
            )

        difference = (
            transaction.amount.subtract(settlement.amount)
            if settlement.amount.amount < transaction.amount.amount
            else settlement.amount.subtract(transaction.amount)
        )

        status = (
            ReconciliationStatus.PARTIAL_MATCH
            if settlement.amount.amount < transaction.amount.amount
            else ReconciliationStatus.MISMATCH
        )

        return ReconciliationResult(
            transaction_id=transaction.transaction_id,
            settlement_id=settlement.settlement_id,
            status=status,
            expected_amount=transaction.amount,
            actual_amount=settlement.amount,
            difference=difference,
            reason=(
                "Settlement amount is lower than the transaction amount."
                if status == ReconciliationStatus.PARTIAL_MATCH
                else "Settlement amount differs from the transaction amount."
            ),
        )