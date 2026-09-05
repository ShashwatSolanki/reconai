from __future__ import annotations

from app.domain.exception import (
    ExceptionCategory,
    ExceptionSeverity,
    FinancialException,
)
from app.domain.reconciliation import ReconciliationResult, ReconciliationStatus


class ExceptionClassifier:
    """Classifies reconciliation results into actionable financial exceptions."""

    def classify(
        self,
        result: ReconciliationResult,
    ) -> FinancialException | None:
        category_map = {
            ReconciliationStatus.PARTIAL_MATCH: ExceptionCategory.PARTIAL_SETTLEMENT,
            ReconciliationStatus.MISMATCH: ExceptionCategory.AMOUNT_MISMATCH,
            ReconciliationStatus.MISSING_SETTLEMENT: ExceptionCategory.MISSING_SETTLEMENT,
            ReconciliationStatus.DUPLICATE: ExceptionCategory.DUPLICATE_SETTLEMENT,
        }

        category = category_map.get(result.status)

        if category is None:
            return None

        severity = self._severity_for(category)

        return FinancialException(
            exception_id=f"exc_{result.transaction_id}",
            transaction_id=result.transaction_id,
            settlement_id=result.settlement_id,
            category=category,
            severity=severity,
            expected_amount=result.expected_amount,
            actual_amount=result.actual_amount,
            difference=result.difference,
            description=result.reason,
        )

    @staticmethod
    def _severity_for(category: ExceptionCategory) -> ExceptionSeverity:
        if category in {
            ExceptionCategory.DUPLICATE_SETTLEMENT,
            ExceptionCategory.MISSING_SETTLEMENT,
        }:
            return ExceptionSeverity.HIGH

        if category == ExceptionCategory.AMOUNT_MISMATCH:
            return ExceptionSeverity.MEDIUM

        return ExceptionSeverity.LOW