from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.domain.money import Money


class PaymentMethod(StrEnum):
    CARD = "card"
    UPI = "upi"
    NETBANKING = "netbanking"
    WALLET = "wallet"


class TransactionStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


@dataclass(frozen=True, slots=True)
class Transaction:
    """Immutable payment transaction entering the reconciliation system."""

    transaction_id: str
    merchant_id: str
    amount: Money
    transaction_time: datetime
    payment_method: PaymentMethod
    reference_id: str
    status: TransactionStatus

    def __post_init__(self) -> None:
        if not self.transaction_id.strip():
            raise ValueError("transaction_id cannot be empty.")

        if not self.merchant_id.strip():
            raise ValueError("merchant_id cannot be empty.")

        if not self.reference_id.strip():
            raise ValueError("reference_id cannot be empty.")

        if self.transaction_time.tzinfo is None:
            raise ValueError("transaction_time must include timezone information.")