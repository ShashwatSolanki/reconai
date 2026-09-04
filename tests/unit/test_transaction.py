from datetime import UTC, datetime

import pytest

from app.domain.money import Money
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus


def test_transaction_can_be_created() -> None:
    transaction = Transaction(
        transaction_id="txn_001",
        merchant_id="merchant_001",
        amount=Money(150000),
        transaction_time=datetime(2026, 9, 4, 10, 30, tzinfo=UTC),
        payment_method=PaymentMethod.UPI,
        reference_id="ref_001",
        status=TransactionStatus.SUCCESS,
    )

    assert transaction.transaction_id == "txn_001"
    assert transaction.merchant_id == "merchant_001"
    assert transaction.amount == Money(150000)
    assert transaction.payment_method == PaymentMethod.UPI
    assert transaction.status == TransactionStatus.SUCCESS


def test_transaction_requires_non_empty_transaction_id() -> None:
    with pytest.raises(ValueError, match="transaction_id"):
        Transaction(
            transaction_id="",
            merchant_id="merchant_001",
            amount=Money(1000),
            transaction_time=datetime(2026, 9, 4, tzinfo=UTC),
            payment_method=PaymentMethod.CARD,
            reference_id="ref_001",
            status=TransactionStatus.SUCCESS,
        )


def test_transaction_requires_non_empty_merchant_id() -> None:
    with pytest.raises(ValueError, match="merchant_id"):
        Transaction(
            transaction_id="txn_001",
            merchant_id="",
            amount=Money(1000),
            transaction_time=datetime(2026, 9, 4, tzinfo=UTC),
            payment_method=PaymentMethod.CARD,
            reference_id="ref_001",
            status=TransactionStatus.SUCCESS,
        )


def test_transaction_requires_non_empty_reference_id() -> None:
    with pytest.raises(ValueError, match="reference_id"):
        Transaction(
            transaction_id="txn_001",
            merchant_id="merchant_001",
            amount=Money(1000),
            transaction_time=datetime(2026, 9, 4, tzinfo=UTC),
            payment_method=PaymentMethod.CARD,
            reference_id="",
            status=TransactionStatus.SUCCESS,
        )


def test_transaction_requires_timezone_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone"):
        Transaction(
            transaction_id="txn_001",
            merchant_id="merchant_001",
            amount=Money(1000),
            transaction_time=datetime(2026, 9, 4),
            payment_method=PaymentMethod.CARD,
            reference_id="ref_001",
            status=TransactionStatus.SUCCESS,
        )


def test_transaction_is_immutable() -> None:
    transaction = Transaction(
        transaction_id="txn_001",
        merchant_id="merchant_001",
        amount=Money(1000),
        transaction_time=datetime(2026, 9, 4, tzinfo=UTC),
        payment_method=PaymentMethod.CARD,
        reference_id="ref_001",
        status=TransactionStatus.SUCCESS,
    )

    with pytest.raises(AttributeError):
        transaction.transaction_id = "txn_002"