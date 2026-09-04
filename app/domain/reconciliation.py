from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.domain.money import Money


class ReconciliationStatus(StrEnum):
    MATCHED = "matched"
    PARTIAL_MATCH = "partial_match"
    MISMATCH = "mismatch"
    MISSING_SETTLEMENT = "MISSING_SETTLEMENT"
    DUPLICATE = "duplicate"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    """Immutable result produced by the reconciliation engine."""

    transaction_id: str
    settlement_id: str | None
    status: ReconciliationStatus
    expected_amount: Money
    actual_amount: Money | None
    difference: Money | None
    reason: str

    def __post_init__(self) -> None:
        if not self.transaction_id.strip():
            raise ValueError("transaction_id cannot be empty.")

        if not self.reason.strip():
            raise ValueError("reason cannot be empty.")