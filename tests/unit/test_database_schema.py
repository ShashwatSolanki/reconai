from sqlalchemy import create_engine, inspect

from app.db.base import Base
from app.db.models import SettlementModel, TransactionModel


def test_database_schema_contains_registered_tables() -> None:
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    assert TransactionModel.__tablename__ in tables
    assert SettlementModel.__tablename__ in tables
