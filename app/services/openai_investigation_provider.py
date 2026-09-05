from __future__ import annotations

import json
from typing import Any

from app.domain.exception_investigation import (
    InvestigationRecommendation,
    InvestigationResult,
    RootCauseCategory,
)
from app.domain.investigation_context import InvestigationContext
from app.services.investigation_provider import InvestigationProvider


class OpenAIInvestigationProvider(InvestigationProvider):
    """Investigation provider backed by an OpenAI-compatible client."""

    def __init__(self, client: Any, model: str) -> None:
        self._client = client
        self._model = model

    def investigate(self, context: InvestigationContext) -> InvestigationResult:
        """Investigate an exception using verified financial evidence."""

        prompt = self._build_prompt(context)

        response = self._client.responses.create(
            model=self._model,
            input=prompt,
        )

        payload = json.loads(response.output_text)

        return InvestigationResult(
            exception_id=context.exception.exception_id,
            root_cause=RootCauseCategory(payload["root_cause"]),
            explanation=payload["explanation"],
            evidence=payload["evidence"],
            recommendation=InvestigationRecommendation(payload["recommendation"]),
            confidence=float(payload["confidence"]),
            requires_human_review=bool(payload["requires_human_review"]),
        )

    def _build_prompt(self, context: InvestigationContext) -> str:
        """Build a prompt containing only verified reconciliation evidence."""

        exception = context.exception
        transaction = context.transaction
        settlement = context.settlement

        settlement_details = (
            "No settlement record is available."
            if settlement is None
            else (
                f"Settlement ID: {settlement.settlement_id}\n"
                f"Settlement amount: {settlement.amount.amount} paise\n"
                f"Settlement status: {settlement.status.value}\n"
                f"Settlement reference: {settlement.reference_id}"
            )
        )

        return (
            "You are a financial reconciliation investigation assistant.\n"
            "Analyze only the verified evidence provided below.\n"
            "Do not invent transactions, fees, policies, or external facts.\n"
            "If the evidence is insufficient, use root_cause='unknown', "
            "recommendation='escalate', and requires_human_review=true.\n\n"
            "Return ONLY valid JSON with these fields:\n"
            "root_cause: one of "
            "fee_deduction, partial_settlement, duplicate_settlement, "
            "reference_mismatch, unknown\n"
            "explanation: string\n"
            "evidence: array of strings\n"
            "recommendation: one of accept_settlement, retry_reconciliation, escalate\n"
            "confidence: number between 0 and 1\n"
            "requires_human_review: boolean\n\n"
            f"Exception ID: {exception.exception_id}\n"
            f"Transaction ID: {transaction.transaction_id}\n"
            f"Merchant ID: {transaction.merchant_id}\n"
            f"Transaction amount: {transaction.amount.amount} paise\n"
            f"Transaction status: {transaction.status.value}\n"
            f"Payment method: {transaction.payment_method.value}\n"
            f"Exception category: {exception.category.value.upper()}\n"
            f"Exception severity: {exception.severity.value}\n"
            f"Exception description: {exception.description}\n"
            f"Expected amount: {exception.expected_amount.amount} paise\n"
            f"Actual amount: "
            f"{exception.actual_amount.amount if exception.actual_amount else 'unavailable'} "
            "paise\n"
            f"Difference: "
            f"{exception.difference.amount if exception.difference else 'unavailable'} "
            "paise\n"
            f"{settlement_details}\n"
        )