from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.domain.money import Money


class SettlementStatus(StrEnum):
    SETTLED = "settled"
    PARTIALLY_SETTLED = "partially_settled"
    FAILED = "failed"
    REVERSED = "reversed"


@dataclass(frozen=True, slots=True)
class Settlement:
    """Immutable settlement record used by the reconciliation system."""

    settlement_id: str
    merchant_id: str
    amount: Money
    settlement_time: datetime
    reference_id: str
    transaction_reference: str
    status: SettlementStatus

    def __post_init__(self) -> None:
        if not self.settlement_id.strip():
            raise ValueError("settlement_id cannot be empty.")

        if not self.merchant_id.strip():
            raise ValueError("merchant_id cannot be empty.")

        if not self.reference_id.strip():
            raise ValueError("reference_id cannot be empty.")

        if not self.transaction_reference.strip():
            raise ValueError("transaction_reference cannot be empty.")

        if self.settlement_time.tzinfo is None:
            raise ValueError("settlement_time must include timezone information.")