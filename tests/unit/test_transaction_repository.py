from datetime import UTC, datetime

import pytest

from app.domain.money import Money
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus
from app.repositories.transaction_repository import TransactionRepository


def make_transaction(transaction_id: str = "pay_0001") -> Transaction:
    return Transaction(
        transaction_id=transaction_id,
        merchant_id="merchant_001",
        amount=Money(10000, "INR"),
        transaction_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        payment_method=PaymentMethod.UPI,
        reference_id=f"ref_{transaction_id}",
        status=TransactionStatus.SUCCESS,
    )


def test_save_and_get_transaction() -> None:
    repository = TransactionRepository()
    transaction = make_transaction()

    repository.save(transaction)

    assert repository.get(transaction.transaction_id) == transaction


def test_get_missing_transaction_returns_none() -> None:
    repository = TransactionRepository()

    assert repository.get("pay_missing") is None


def test_duplicate_transaction_id_is_rejected() -> None:
    repository = TransactionRepository()
    transaction = make_transaction()

    repository.save(transaction)

    with pytest.raises(ValueError, match="Transaction already exists"):
        repository.save(transaction)


def test_get_by_merchant_returns_transactions() -> None:
    repository = TransactionRepository()
    first = make_transaction("pay_0001")
    second = make_transaction("pay_0002")

    repository.save(first)
    repository.save(second)

    transactions = repository.get_by_merchant("merchant_001")

    assert transactions == [first, second]
