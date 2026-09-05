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
from app.services.persisted_reconciliation import PersistedReconciliationService
from app.services.reconciliation_engine import ReconciliationEngine


def make_transaction(transaction_id: str = "txn_001") -> Transaction:
    return Transaction(
        transaction_id=transaction_id,
        merchant_id="merchant_001",
        amount=Money(10_000),
        transaction_time=datetime(2026, 1, 1, tzinfo=UTC),
        payment_method=PaymentMethod.UPI,
        reference_id=f"ref_{transaction_id}",
        status=TransactionStatus.SUCCESS,
    )


def make_settlement(
    settlement_id: str = "stl_001",
    transaction_reference: str = "txn_001",
) -> Settlement:
    return Settlement(
        settlement_id=settlement_id,
        merchant_id="merchant_001",
        amount=Money(10_000),
        settlement_time=datetime(2026, 1, 2, tzinfo=UTC),
        reference_id=f"settlement_ref_{settlement_id}",
        transaction_reference=transaction_reference,
        status=SettlementStatus.SETTLED,
    )


def test_reconcile_persisted_merchant_records() -> None:
    engine = create_engine("sqlite:///:memory:")
    create_schema(engine)

    with Session(engine) as session:
        transaction_repository = SqlAlchemyTransactionRepository(session)
        settlement_repository = SqlAlchemySettlementRepository(session)

        transaction_repository.save(make_transaction())
        settlement_repository.save(make_settlement())

        reconciliation_service = BatchReconciliationService(
            engine=ReconciliationEngine(),
        )
        service = PersistedReconciliationService(
            transaction_repository=transaction_repository,
            settlement_repository=settlement_repository,
            reconciliation_service=reconciliation_service,
        )

        results = service.reconcile_merchant("merchant_001")

        assert len(results) == 1
        assert results[0].transaction_id == "txn_001"
        assert results[0].settlement_id == "stl_001"
        assert results[0].status.value == "matched"


def test_reconcile_merchant_ignores_records_from_other_merchants() -> None:
    engine = create_engine("sqlite:///:memory:")
    create_schema(engine)

    with Session(engine) as session:
        transaction_repository = SqlAlchemyTransactionRepository(session)
        settlement_repository = SqlAlchemySettlementRepository(session)

        transaction_repository.save(make_transaction("txn_001"))

        other_transaction = Transaction(
            transaction_id="txn_002",
            merchant_id="merchant_002",
            amount=Money(20_000),
            transaction_time=datetime(2026, 1, 1, tzinfo=UTC),
            payment_method=PaymentMethod.CARD,
            reference_id="ref_txn_002",
            status=TransactionStatus.SUCCESS,
        )
        transaction_repository.save(other_transaction)

        settlement_repository.save(make_settlement())
        settlement_repository.save(
            make_settlement(
                settlement_id="stl_002",
                transaction_reference="txn_002",
            )
        )

        reconciliation_service = BatchReconciliationService(
            engine=ReconciliationEngine(),
        )
        service = PersistedReconciliationService(
            transaction_repository=transaction_repository,
            settlement_repository=settlement_repository,
            reconciliation_service=reconciliation_service,
        )

        results = service.reconcile_merchant("merchant_001")

        assert len(results) == 1
        assert results[0].transaction_id == "txn_001"