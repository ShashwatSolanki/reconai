from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.domain.money import Money
from app.domain.settlement import Settlement, SettlementStatus


class SettlementModel(Base):
    """SQLAlchemy persistence model for settlement records."""

    __tablename__ = "settlements"

    settlement_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    settlement_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    reference_id: Mapped[str] = mapped_column(String(128), nullable=False)
    transaction_reference: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)

    @classmethod
    def from_domain(cls, settlement: Settlement) -> SettlementModel:
        """Create a persistence model from a domain settlement."""
        return cls(
            settlement_id=settlement.settlement_id,
            merchant_id=settlement.merchant_id,
            amount=settlement.amount.amount,
            currency=settlement.amount.currency,
            settlement_time=settlement.settlement_time,
            reference_id=settlement.reference_id,
            transaction_reference=settlement.transaction_reference,
            status=settlement.status.value,
        )

    def to_domain(self) -> Settlement:
        """Convert the persistence model back into a domain settlement."""
        settlement_time = self.settlement_time

        if settlement_time.tzinfo is None:
            settlement_time = settlement_time.replace(tzinfo=UTC)

        return Settlement(
            settlement_id=self.settlement_id,
            merchant_id=self.merchant_id,
            amount=Money(self.amount, self.currency),
            settlement_time=settlement_time,
            reference_id=self.reference_id,
            transaction_reference=self.transaction_reference,
            status=SettlementStatus(self.status),
        )