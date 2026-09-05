from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.transaction import TransactionModel
from app.domain.money import Money
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus


def make_transaction() -> Transaction:
    return Transaction(
        transaction_id="pay_0001",
        merchant_id="merchant_001",
        amount=Money(10000, "INR"),
        transaction_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        payment_method=PaymentMethod.UPI,
        reference_id="ref_0001",
        status=TransactionStatus.SUCCESS,
    )


def test_transaction_model_maps_domain_fields() -> None:
    transaction = make_transaction()

    model = TransactionModel.from_domain(transaction)

    assert model.transaction_id == transaction.transaction_id
    assert model.merchant_id == transaction.merchant_id
    assert model.amount == transaction.amount.amount
    assert model.currency == transaction.amount.currency
    assert model.transaction_time == transaction.transaction_time
    assert model.payment_method == transaction.payment_method.value
    assert model.reference_id == transaction.reference_id
    assert model.status == transaction.status.value


def test_transaction_model_round_trips_to_domain() -> None:
    transaction = make_transaction()

    model = TransactionModel.from_domain(transaction)
    restored = model.to_domain()

    assert restored == transaction


def test_transaction_model_persists_with_sqlite() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    transaction = make_transaction()
    model = TransactionModel.from_domain(transaction)

    with Session(engine) as session:
        session.add(model)
        session.commit()

        persisted = session.get(TransactionModel, transaction.transaction_id)

    assert persisted is not None
    assert persisted.to_domain() == transaction