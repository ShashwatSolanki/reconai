from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.repositories.settlement import SqlAlchemySettlementRepository
from app.db.repositories.transaction import SqlAlchemyTransactionRepository
from app.db.schema import create_schema
from app.domain.money import Money
from app.domain.settlement import Settlement, SettlementStatus
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus
from app.services.batch_reconciliation import BatchReconciliationService
from app.services.reconciliation_engine import ReconciliationEngine


def make_transaction() -> Transaction:
    return Transaction(
        transaction_id="txn_001",
        merchant_id="merchant_001",
        amount=Money(10_000),
        transaction_time=datetime(2026, 1, 1, tzinfo=UTC),
        payment_method=PaymentMethod.UPI,
        reference_id="ref_001",
        status=TransactionStatus.SUCCESS,
    )


def make_settlement() -> Settlement:
    return Settlement(
        settlement_id="stl_001",
        merchant_id="merchant_001",
        amount=Money(10_000),
        settlement_time=datetime(2026, 1, 2, tzinfo=UTC),
        reference_id="settlement_ref_001",
        transaction_reference="txn_001",
        status=SettlementStatus.SETTLED,
    )


def test_persisted_records_can_be_reconciled() -> None:
    engine = create_engine("sqlite:///:memory:")
    create_schema(engine)

    with Session(engine) as session:
        transaction_repository = SqlAlchemyTransactionRepository(session)
        settlement_repository = SqlAlchemySettlementRepository(session)

        transaction = make_transaction()
        settlement = make_settlement()

        transaction_repository.save(transaction)
        settlement_repository.save(settlement)

        persisted_transaction = transaction_repository.get("txn_001")
        persisted_settlement = settlement_repository.get("stl_001")

        assert persisted_transaction == transaction
        assert persisted_settlement == settlement

        reconciliation_service = BatchReconciliationService(
            ReconciliationEngine()
        )

        results = reconciliation_service.reconcile(
            [persisted_transaction],
            [persisted_settlement],
        )

        assert len(results) == 1
        assert results[0].transaction_id == "txn_001"
        assert results[0].settlement_id == "stl_001"
        assert results[0].status.value == "matched"