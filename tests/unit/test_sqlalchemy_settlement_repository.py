from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.repositories.settlement import SqlAlchemySettlementRepository
from app.domain.money import Money
from app.domain.settlement import Settlement, SettlementStatus


def make_settlement(settlement_id: str = "stl_001") -> Settlement:
    return Settlement(
        settlement_id=settlement_id,
        merchant_id="merchant_001",
        amount=Money(10_000),
        settlement_time=datetime(2026, 1, 2, tzinfo=UTC),
        reference_id="settlement_ref_001",
        transaction_reference="txn_001",
        status=SettlementStatus.SETTLED,
    )


def make_repository() -> tuple[Engine, Session, SqlAlchemySettlementRepository]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)

    return engine, session, SqlAlchemySettlementRepository(session)


def test_save_and_get_settlement() -> None:
    _, session, repository = make_repository()
    settlement = make_settlement()

    repository.save(settlement)

    assert repository.get("stl_001") == settlement

    session.close()


def test_duplicate_settlement_id_is_rejected() -> None:
    _, session, repository = make_repository()
    settlement = make_settlement()

    repository.save(settlement)

    try:
        repository.save(settlement)
    except ValueError as exc:
        assert "Settlement already exists" in str(exc)
    else:
        raise AssertionError("Expected duplicate settlement to raise ValueError")

    session.close()


def test_get_by_merchant_returns_matching_settlements() -> None:
    _, session, repository = make_repository()

    first = make_settlement("stl_001")
    second = make_settlement("stl_002")

    repository.save(first)
    repository.save(second)

    assert repository.get_by_merchant("merchant_001") == [first, second]
    assert repository.get_by_merchant("merchant_missing") == []

    session.close()