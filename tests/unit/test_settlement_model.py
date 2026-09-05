from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.settlement import SettlementModel
from app.domain.money import Money
from app.domain.settlement import Settlement, SettlementStatus


def make_settlement() -> Settlement:
    return Settlement(
        settlement_id="set_0001",
        merchant_id="merchant_001",
        amount=Money(10000, "INR"),
        settlement_time=datetime(2026, 9, 1, 18, 0, tzinfo=UTC),
        reference_id="settle_ref_0001",
        transaction_reference="pay_0001",
        status=SettlementStatus.SETTLED,
    )


def test_settlement_model_maps_domain_fields() -> None:
    settlement = make_settlement()
    model = SettlementModel.from_domain(settlement)

    assert model.settlement_id == settlement.settlement_id
    assert model.merchant_id == settlement.merchant_id
    assert model.amount == settlement.amount.amount
    assert model.currency == settlement.amount.currency
    assert model.settlement_time == settlement.settlement_time
    assert model.reference_id == settlement.reference_id
    assert model.transaction_reference == settlement.transaction_reference
    assert model.status == settlement.status.value


def test_settlement_model_round_trips_to_domain() -> None:
    settlement = make_settlement()
    model = SettlementModel.from_domain(settlement)

    restored = model.to_domain()

    assert restored == settlement


def test_settlement_model_persists_with_sqlite() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    settlement = make_settlement()
    model = SettlementModel.from_domain(settlement)

    with Session(engine) as session:
        session.add(model)
        session.commit()
        persisted = session.get(SettlementModel, settlement.settlement_id)

    assert persisted is not None
    assert persisted.to_domain() == settlement
