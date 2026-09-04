from datetime import UTC, datetime

import pytest

from app.domain.money import Money
from app.domain.settlement import Settlement, SettlementStatus


def test_settlement_can_be_created() -> None:
    settlement = Settlement(
        settlement_id="set_001",
        merchant_id="merchant_001",
        amount=Money(98000),
        settlement_time=datetime(2026, 9, 4, 12, 30, tzinfo=UTC),
        reference_id="settle_ref_001",
        transaction_reference="pay_abc",
        status=SettlementStatus.SETTLED,
    )

    assert settlement.settlement_id == "set_001"
    assert settlement.merchant_id == "merchant_001"
    assert settlement.amount == Money(98000)
    assert settlement.reference_id == "settle_ref_001"
    assert settlement.transaction_reference == "pay_abc"
    assert settlement.status == SettlementStatus.SETTLED


def test_settlement_supports_partial_settlement() -> None:
    settlement = Settlement(
        settlement_id="set_002",
        merchant_id="merchant_001",
        amount=Money(80000),
        settlement_time=datetime(2026, 9, 4, 12, 30, tzinfo=UTC),
        reference_id="settle_ref_002",
        transaction_reference="pay_xyz",
        status=SettlementStatus.PARTIALLY_SETTLED,
    )

    assert settlement.status == SettlementStatus.PARTIALLY_SETTLED


def test_settlement_requires_non_empty_settlement_id() -> None:
    with pytest.raises(ValueError, match="settlement_id"):
        Settlement(
            settlement_id="",
            merchant_id="merchant_001",
            amount=Money(1000),
            settlement_time=datetime(2026, 9, 4, tzinfo=UTC),
            reference_id="settle_ref_001",
            transaction_reference="pay_abc",
            status=SettlementStatus.SETTLED,
        )


def test_settlement_requires_non_empty_merchant_id() -> None:
    with pytest.raises(ValueError, match="merchant_id"):
        Settlement(
            settlement_id="set_001",
            merchant_id="",
            amount=Money(1000),
            settlement_time=datetime(2026, 9, 4, tzinfo=UTC),
            reference_id="settle_ref_001",
            transaction_reference="pay_abc",
            status=SettlementStatus.SETTLED,
        )


def test_settlement_requires_non_empty_reference_id() -> None:
    with pytest.raises(ValueError, match="reference_id"):
        Settlement(
            settlement_id="set_001",
            merchant_id="merchant_001",
            amount=Money(1000),
            settlement_time=datetime(2026, 9, 4, tzinfo=UTC),
            reference_id="",
            transaction_reference="pay_abc",
            status=SettlementStatus.SETTLED,
        )


def test_settlement_requires_non_empty_transaction_reference() -> None:
    with pytest.raises(ValueError, match="transaction_reference"):
        Settlement(
            settlement_id="set_001",
            merchant_id="merchant_001",
            amount=Money(1000),
            settlement_time=datetime(2026, 9, 4, tzinfo=UTC),
            reference_id="settle_ref_001",
            transaction_reference="",
            status=SettlementStatus.SETTLED,
        )


def test_settlement_requires_timezone_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone"):
        Settlement(
            settlement_id="set_001",
            merchant_id="merchant_001",
            amount=Money(1000),
            settlement_time=datetime(2026, 9, 4),
            reference_id="settle_ref_001",
            transaction_reference="pay_abc",
            status=SettlementStatus.SETTLED,
        )


def test_settlement_is_immutable() -> None:
    settlement = Settlement(
        settlement_id="set_001",
        merchant_id="merchant_001",
        amount=Money(1000),
        settlement_time=datetime(2026, 9, 4, tzinfo=UTC),
        reference_id="settle_ref_001",
        transaction_reference="pay_abc",
        status=SettlementStatus.SETTLED,
    )

    with pytest.raises(AttributeError):
        settlement.settlement_id = "set_002"