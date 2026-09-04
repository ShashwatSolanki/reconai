from __future__ import annotations

from app.domain.exception import ExceptionCategory, FinancialException
from app.domain.exception_investigation import (
    InvestigationRecommendation,
    InvestigationResult,
    RootCauseCategory,
)


class InvestigationService:
    """Investigate financial exceptions using deterministic baseline rules."""

    def investigate(self, exception: FinancialException) -> InvestigationResult:
        """Produce a structured investigation result for an exception."""

        if exception.category == ExceptionCategory.PARTIAL_SETTLEMENT:
            return InvestigationResult(
                exception_id=exception.exception_id,
                root_cause=RootCauseCategory.PARTIAL_SETTLEMENT,
                explanation=(
                    "The settlement amount is lower than the expected transaction "
                    "amount, indicating a partial settlement."
                ),
                evidence=[
                    f"Expected amount: {exception.expected_amount.amount} paise",
                    f"Actual amount: {exception.actual_amount.amount} paise"
                    if exception.actual_amount is not None
                    else "Actual settlement amount is unavailable.",
                ],
                recommendation=InvestigationRecommendation.ACCEPT_SETTLEMENT,
                confidence=0.95,
                requires_human_review=False,
            )

        if exception.category == ExceptionCategory.AMOUNT_MISMATCH:
            return InvestigationResult(
                exception_id=exception.exception_id,
                root_cause=RootCauseCategory.FEE_DEDUCTION,
                explanation=(
                    "The settlement amount is lower than the expected transaction "
                    "amount, which is consistent with a fee deduction."
                ),
                evidence=[
                    f"Expected amount: {exception.expected_amount.amount} paise",
                    f"Actual amount: {exception.actual_amount.amount} paise"
                    if exception.actual_amount is not None
                    else "Actual settlement amount is unavailable.",
                    f"Difference: {exception.difference.amount} paise"
                    if exception.difference is not None
                    else "Difference is unavailable.",
                ],
                recommendation=InvestigationRecommendation.ACCEPT_SETTLEMENT,
                confidence=0.85,
                requires_human_review=False,
            )

        if exception.category == ExceptionCategory.DUPLICATE_SETTLEMENT:
            return InvestigationResult(
                exception_id=exception.exception_id,
                root_cause=RootCauseCategory.DUPLICATE_SETTLEMENT,
                explanation=(
                    "Multiple settlement records are associated with the same "
                    "transaction and require review before resolution."
                ),
                evidence=[
                    "The reconciliation engine identified multiple settlement "
                    "records for the transaction."
                ],
                recommendation=InvestigationRecommendation.ESCALATE,
                confidence=0.99,
                requires_human_review=True,
            )

        return InvestigationResult(
            exception_id=exception.exception_id,
            root_cause=RootCauseCategory.UNKNOWN,
            explanation=(
                "The available deterministic exception information is insufficient "
                "to establish a reliable root cause."
            ),
            evidence=[
                f"Exception category: {exception.category.value}",
                "Additional investigation is required.",
            ],
            recommendation=InvestigationRecommendation.ESCALATE,
            confidence=0.25,
            requires_human_review=True,
        )
