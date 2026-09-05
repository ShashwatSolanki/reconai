from datetime import UTC, datetime

import pytest

from app.domain.money import Money
from app.domain.settlement import Settlement, SettlementStatus
from app.repositories.settlement_repository import SettlementRepository


def make_settlement(settlement_id: str = "set_0001") -> Settlement:
    return Settlement(
        settlement_id=settlement_id,
        merchant_id="merchant_001",
        amount=Money(10000, "INR"),
        settlement_time=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        reference_id=f"ref_{settlement_id}",
        transaction_reference="pay_0001",
        status=SettlementStatus.SETTLED,
    )


def test_save_and_get_settlement() -> None:
    repository = SettlementRepository()
    settlement = make_settlement()

    repository.save(settlement)

    assert repository.get(settlement.settlement_id) == settlement


def test_get_missing_settlement_returns_none() -> None:
    repository = SettlementRepository()

    assert repository.get("set_missing") is None


def test_duplicate_settlement_id_is_rejected() -> None:
    repository = SettlementRepository()
    settlement = make_settlement()

    repository.save(settlement)

    with pytest.raises(ValueError, match="Settlement already exists"):
        repository.save(settlement)


def test_get_by_merchant_returns_settlements() -> None:
    repository = SettlementRepository()
    first = make_settlement("set_0001")
    second = make_settlement("set_0002")

    repository.save(first)
    repository.save(second)

    settlements = repository.get_by_merchant("merchant_001")

    assert settlements == [first, second]