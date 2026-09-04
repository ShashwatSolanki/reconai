from __future__ import annotations

from dataclasses import dataclass

from app.domain.exception import FinancialException
from app.domain.settlement import Settlement
from app.domain.transaction import Transaction


@dataclass(frozen=True, slots=True)
class InvestigationContext:
    """Evidence available to investigate a financial exception."""

    exception: FinancialException
    transaction: Transaction
    settlement: Settlement | None

    def __post_init__(self) -> None:
        if self.exception.transaction_id != self.transaction.transaction_id:
            raise ValueError(
                "Exception transaction_id must match the transaction in context."
            )

        if (
            self.exception.settlement_id is not None
            and self.settlement is not None
            and self.exception.settlement_id != self.settlement.settlement_id
        ):
            raise ValueError(
                "Exception settlement_id must match the settlement in context."
            )
