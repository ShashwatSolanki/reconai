from __future__ import annotations

from app.domain.exception import ExceptionCategory
from app.domain.exception_investigation import (
    InvestigationRecommendation,
    InvestigationResult,
    RootCauseCategory,
)
from app.domain.investigation_context import InvestigationContext


class ExceptionInvestigator:
    """Investigates financial exceptions using available reconciliation evidence."""

    def investigate(self, context: InvestigationContext) -> InvestigationResult:
        exception = context.exception
        transaction = context.transaction
        settlement = context.settlement

        if settlement is None:
            return InvestigationResult(
                exception_id=exception.exception_id,
                root_cause=RootCauseCategory.UNKNOWN,
                explanation=(
                    "The settlement record is missing, so the exception cannot "
                    "be resolved automatically."
                ),
                evidence=[
                    f"Transaction amount: {transaction.amount}",
                    "No settlement record is available.",
                ],
                recommendation=InvestigationRecommendation.ESCALATE,
                confidence=0.95,
                requires_human_review=True,
            )

        if exception.category == ExceptionCategory.DUPLICATE_SETTLEMENT:
            return InvestigationResult(
                exception_id=exception.exception_id,
                root_cause=RootCauseCategory.DUPLICATE_SETTLEMENT,
                explanation=(
                    "The reconciliation exception is classified as a duplicate "
                    "settlement and requires human review before resolution."
                ),
                evidence=[
                    f"Transaction reference: {transaction.reference_id}",
                    f"Settlement reference: {settlement.reference_id}",
                    f"Settlement ID: {settlement.settlement_id}",
                ],
                recommendation=InvestigationRecommendation.ESCALATE,
                confidence=0.95,
                requires_human_review=True,
            )

        if exception.category == ExceptionCategory.REFERENCE_MISMATCH:
            return InvestigationResult(
                exception_id=exception.exception_id,
                root_cause=RootCauseCategory.REFERENCE_MISMATCH,
                explanation=(
                    "The transaction and settlement references do not provide "
                    "sufficient evidence for automatic resolution."
                ),
                evidence=[
                    f"Transaction reference: {transaction.reference_id}",
                    f"Settlement transaction reference: "
                    f"{settlement.transaction_reference}",
                ],
                recommendation=InvestigationRecommendation.ESCALATE,
                confidence=0.90,
                requires_human_review=True,
            )

        if exception.category == ExceptionCategory.PARTIAL_SETTLEMENT:
            return InvestigationResult(
                exception_id=exception.exception_id,
                root_cause=RootCauseCategory.PARTIAL_SETTLEMENT,
                explanation=(
                    "The settlement amount is materially lower than the "
                    "transaction amount, indicating a partial settlement."
                ),
                evidence=[
                    f"Transaction amount: {transaction.amount}",
                    f"Settlement amount: {settlement.amount}",
                    f"Difference: {exception.difference}",
                ],
                recommendation=InvestigationRecommendation.RETRY_RECONCILIATION,
                confidence=0.90,
                requires_human_review=False,
            )

        if exception.category == ExceptionCategory.AMOUNT_MISMATCH:
            difference = exception.difference

            if difference is not None and difference.amount > 0:
                return InvestigationResult(
                    exception_id=exception.exception_id,
                    root_cause=RootCauseCategory.FEE_DEDUCTION,
                    explanation=(
                        "The settlement is lower than the transaction by a "
                        "small amount, which is consistent with a fee deduction."
                    ),
                    evidence=[
                        f"Transaction amount: {transaction.amount}",
                        f"Settlement amount: {settlement.amount}",
                        f"Difference: {difference}",
                    ],
                    recommendation=InvestigationRecommendation.ACCEPT_SETTLEMENT,
                    confidence=0.85,
                    requires_human_review=False,
                )

        return InvestigationResult(
            exception_id=exception.exception_id,
            root_cause=RootCauseCategory.UNKNOWN,
            explanation=(
                "The available evidence does not support a sufficiently "
                "confident automatic root-cause determination."
            ),
            evidence=[
                f"Transaction amount: {transaction.amount}",
                f"Settlement amount: {settlement.amount}",
                f"Exception category: {exception.category.value}",
            ],
            recommendation=InvestigationRecommendation.ESCALATE,
            confidence=0.50,
            requires_human_review=True,
        )
