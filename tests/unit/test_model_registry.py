from app.db.base import Base
from app.db.models import SettlementModel, TransactionModel


def test_transaction_model_is_registered() -> None:
    assert TransactionModel.__tablename__ == "transactions"
    assert "transactions" in Base.metadata.tables


def test_settlement_model_is_registered() -> None:
    assert SettlementModel.__tablename__ == "settlements"
    assert "settlements" in Base.metadata.tables
