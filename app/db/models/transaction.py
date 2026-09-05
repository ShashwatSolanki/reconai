from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.domain.money import Money
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus


class TransactionModel(Base):
    """SQLAlchemy persistence model for payment transactions."""

    __tablename__ = "transactions"

    transaction_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    transaction_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    payment_method: Mapped[str] = mapped_column(String(32), nullable=False)
    reference_id: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)

    @classmethod
    def from_domain(cls, transaction: Transaction) -> TransactionModel:
        """Create a persistence model from a domain transaction."""
        return cls(
            transaction_id=transaction.transaction_id,
            merchant_id=transaction.merchant_id,
            amount=transaction.amount.amount,
            currency=transaction.amount.currency,
            transaction_time=transaction.transaction_time,
            payment_method=transaction.payment_method.value,
            reference_id=transaction.reference_id,
            status=transaction.status.value,
        )

    def to_domain(self) -> Transaction:
        """Convert the persistence model back into the domain entity."""
        transaction_time = self.transaction_time
        if transaction_time.tzinfo is None:
            transaction_time = transaction_time.replace(tzinfo=UTC)

        return Transaction(
            transaction_id=self.transaction_id,
            merchant_id=self.merchant_id,
            amount=Money(self.amount, self.currency),
            transaction_time=transaction_time,
            payment_method=PaymentMethod(self.payment_method),
            reference_id=self.reference_id,
            status=TransactionStatus(self.status),
        )