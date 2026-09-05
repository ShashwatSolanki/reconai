from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.api.main import app
from app.db.repositories.settlement import SqlAlchemySettlementRepository
from app.db.repositories.transaction import SqlAlchemyTransactionRepository
from app.db.schema import create_schema
from app.domain.money import Money
from app.domain.settlement import Settlement, SettlementStatus
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus


def test_persisted_reconciliation_endpoint_reconciles_merchant_records() -> None:
    engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
    create_schema(engine)

    session_factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)

    with session_factory() as session:
        transaction_repository = SqlAlchemyTransactionRepository(session)
        settlement_repository = SqlAlchemySettlementRepository(session)

        transaction_repository.save(
            Transaction(
                transaction_id="txn_api_001",
                merchant_id="merchant_api_001",
                amount=Money(10000),
                transaction_time=datetime(2026, 9, 5, 10, 0, tzinfo=UTC),
                payment_method=PaymentMethod.UPI,
                reference_id="ref_api_001",
                status=TransactionStatus.SUCCESS,
            )
        )

        settlement_repository.save(
            Settlement(
                settlement_id="set_api_001",
                merchant_id="merchant_api_001",
                amount=Money(10000),
                settlement_time=datetime(2026, 9, 5, 12, 0, tzinfo=UTC),
                reference_id="settle_ref_api_001",
                transaction_reference="txn_api_001",
                status=SettlementStatus.SETTLED,
            )
        )

    def override_get_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/reconciliation/merchants/merchant_api_001"
        )

        assert response.status_code == 200

        body = response.json()

        assert body["results"][0]["transaction_id"] == "txn_api_001"
        assert body["results"][0]["settlement_id"] == "set_api_001"
        assert body["results"][0]["status"] == "matched"
        assert body["summary"]["total_transactions"] == 1
        assert body["summary"]["matched"] == 1
    finally:
        app.dependency_overrides.clear()