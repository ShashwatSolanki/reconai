from __future__ import annotations

from app.domain.transaction import Transaction


class TransactionRepository:
    """In-memory repository for payment transactions."""

    def __init__(self) -> None:
        self._transactions: dict[str, Transaction] = {}

    def save(self, transaction: Transaction) -> None:
        """Store a transaction by its unique transaction ID."""
        if transaction.transaction_id in self._transactions:
            raise ValueError(
                f"Transaction already exists: {transaction.transaction_id}"
            )

        self._transactions[transaction.transaction_id] = transaction

    def get(self, transaction_id: str) -> Transaction | None:
        """Return a transaction by ID, or None when it does not exist."""
        return self._transactions.get(transaction_id)

    def get_by_merchant(self, merchant_id: str) -> list[Transaction]:
        """Return all transactions associated with a merchant."""
        return [
            transaction
            for transaction in self._transactions.values()
            if transaction.merchant_id == merchant_id
        ]
