from sqlalchemy import create_engine, inspect

from app.db.schema import create_schema


def test_create_schema_creates_registered_tables() -> None:
    engine = create_engine("sqlite:///:memory:")

    create_schema(engine)

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    assert "transactions" in tables
    assert "settlements" in tables