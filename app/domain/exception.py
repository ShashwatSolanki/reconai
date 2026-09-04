from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.domain.money import Money


class ExceptionCategory(StrEnum):
    AMOUNT_MISMATCH = "amount_mismatch"
    MISSING_SETTLEMENT = "missing_settlement"
    DUPLICATE_SETTLEMENT = "duplicate_settlement"
    PARTIAL_SETTLEMENT = "partial_settlement"
    REFERENCE_MISMATCH = "reference_mismatch"
    UNKNOWN = "unknown"


class ExceptionSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class FinancialException:
    """Immutable financial reconciliation exception."""

    exception_id: str
    transaction_id: str
    settlement_id: str | None
    category: ExceptionCategory
    severity: ExceptionSeverity
    expected_amount: Money
    actual_amount: Money | None
    difference: Money | None
    description: str

    def __post_init__(self) -> None:
        if not self.exception_id.strip():
            raise ValueError("exception_id cannot be empty.")

        if not self.transaction_id.strip():
            raise ValueError("transaction_id cannot be empty.")

        if not self.description.strip():
            raise ValueError("description cannot be empty.")