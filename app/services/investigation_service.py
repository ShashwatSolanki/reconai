from __future__ import annotations

from app.domain.exception import ExceptionCategory
from app.domain.exception_investigation import (
    InvestigationRecommendation,
    InvestigationResult,
    RootCauseCategory,
)
from app.domain.investigation_context import InvestigationContext
from app.services.investigation_provider import InvestigationProvider


class InvestigationService(InvestigationProvider):
    """Deterministic investigation provider for tests and offline operation."""

    def investigate(self, context: InvestigationContext) -> InvestigationResult:
        """Produce a structured investigation result from exception context."""

        exception = context.exception

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
                    f"Actual amount: {context.settlement.amount.amount} paise"
                    if context.settlement is not None
                    else "Actual settlement amount is unavailable.",
                ],
                recommendation=InvestigationRecommendation.ACCEPT_SETTLEMENT,
                confidence=0.95,
                requires_human_review=False,
            )

        if exception.category == ExceptionCategory.AMOUNT_MISMATCH:
            return self._investigate_amount_mismatch(context)

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
                "The available evidence is insufficient to establish a reliable "
                "root cause."
            ),
            evidence=[
                f"Exception category: {exception.category.value}",
                "Additional investigation is required.",
            ],
            recommendation=InvestigationRecommendation.ESCALATE,
            confidence=0.25,
            requires_human_review=True,
        )

    def _investigate_amount_mismatch(
        self,
        context: InvestigationContext,
    ) -> InvestigationResult:
        """Investigate an amount mismatch using the settlement evidence."""

        exception = context.exception
        settlement = context.settlement

        if settlement is None:
            return InvestigationResult(
                exception_id=exception.exception_id,
                root_cause=RootCauseCategory.UNKNOWN,
                explanation=(
                    "The settlement record is unavailable, so the amount mismatch "
                    "cannot be reliably classified."
                ),
                evidence=[
                    f"Expected amount: {exception.expected_amount.amount} paise",
                    "Settlement record is unavailable.",
                ],
                recommendation=InvestigationRecommendation.ESCALATE,
                confidence=0.20,
                requires_human_review=True,
            )

        difference = exception.difference.amount if exception.difference else 0
        expected = context.transaction.amount.amount
        actual = settlement.amount.amount

        # A small settlement deduction is a candidate fee. We deliberately
        # avoid treating large unexplained differences as fees.
        if actual < expected and difference <= expected // 20:
            return InvestigationResult(
                exception_id=exception.exception_id,
                root_cause=RootCauseCategory.FEE_DEDUCTION,
                explanation=(
                    "The settlement is slightly lower than the transaction amount. "
                    "The size of the difference is consistent with a fee deduction."
                ),
                evidence=[
                    f"Transaction amount: {expected} paise",
                    f"Settlement amount: {actual} paise",
                    f"Difference: {difference} paise",
                    "Difference is within the configured small-deduction threshold.",
                ],
                recommendation=InvestigationRecommendation.ACCEPT_SETTLEMENT,
                confidence=0.85,
                requires_human_review=False,
            )

        return InvestigationResult(
            exception_id=exception.exception_id,
            root_cause=RootCauseCategory.UNKNOWN,
            explanation=(
                "The amount difference is too large to reliably classify as a "
                "standard fee deduction."
            ),
            evidence=[
                f"Transaction amount: {expected} paise",
                f"Settlement amount: {actual} paise",
                f"Difference: {difference} paise",
            ],
            recommendation=InvestigationRecommendation.ESCALATE,
            confidence=0.30,
            requires_human_review=True,
        )
