from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.repositories.transaction import SqlAlchemyTransactionRepository
from app.domain.money import Money
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus


def make_transaction(transaction_id: str = "txn_001") -> Transaction:
    return Transaction(
        transaction_id=transaction_id,
        merchant_id="merchant_001",
        amount=Money(10_000),
        transaction_time=datetime(2026, 1, 1, tzinfo=UTC),
        payment_method=PaymentMethod.UPI,
        reference_id="ref_001",
        status=TransactionStatus.SUCCESS,
    )


def make_repository() -> tuple[Engine, Session, SqlAlchemyTransactionRepository]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)

    return engine, session, SqlAlchemyTransactionRepository(session)


def test_save_and_get_transaction() -> None:
    _, session, repository = make_repository()
    transaction = make_transaction()

    repository.save(transaction)

    assert repository.get("txn_001") == transaction

    session.close()


def test_duplicate_transaction_id_is_rejected() -> None:
    _, session, repository = make_repository()
    transaction = make_transaction()

    repository.save(transaction)

    try:
        repository.save(transaction)
    except ValueError as exc:
        assert "Transaction already exists" in str(exc)
    else:
        raise AssertionError("Expected duplicate transaction to raise ValueError")

    session.close()


def test_get_by_merchant_returns_matching_transactions() -> None:
    _, session, repository = make_repository()

    first = make_transaction("txn_001")
    second = make_transaction("txn_002")

    repository.save(first)
    repository.save(second)

    assert repository.get_by_merchant("merchant_001") == [first, second]
    assert repository.get_by_merchant("merchant_missing") == []

    session.close()