from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RootCauseCategory(StrEnum):
    FEE_DEDUCTION = "fee_deduction"
    PARTIAL_SETTLEMENT = "partial_settlement"
    DUPLICATE_SETTLEMENT = "duplicate_settlement"
    REFERENCE_MISMATCH = "reference_mismatch"
    UNKNOWN = "unknown"


class InvestigationRecommendation(StrEnum):
    ACCEPT_SETTLEMENT = "accept_settlement"
    RETRY_RECONCILIATION = "retry_reconciliation"
    ESCALATE = "escalate"


@dataclass(frozen=True, slots=True)
class InvestigationResult:
    """Structured result produced by exception investigation."""

    exception_id: str
    root_cause: RootCauseCategory
    explanation: str
    evidence: list[str]
    recommendation: InvestigationRecommendation
    confidence: float
    requires_human_review: bool

    def __post_init__(self) -> None:
        if not self.exception_id.strip():
            raise ValueError("exception_id cannot be empty.")

        if not self.explanation.strip():
            raise ValueError("explanation cannot be empty.")

        if not self.evidence:
            raise ValueError("evidence cannot be empty.")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0.")

        if (
            self.recommendation == InvestigationRecommendation.ESCALATE
            and not self.requires_human_review
        ):
            raise ValueError(
                "Escalation recommendation requires human review."
            )
