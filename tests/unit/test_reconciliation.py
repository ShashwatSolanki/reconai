import pytest

from app.domain.money import Money
from app.domain.reconciliation import ReconciliationResult, ReconciliationStatus


def test_reconciliation_result_can_be_created_for_match() -> None:
    result = ReconciliationResult(
        transaction_id="pay_001",
        settlement_id="set_001",
        status=ReconciliationStatus.MATCHED,
        expected_amount=Money(100000),
        actual_amount=Money(100000),
        difference=Money(0),
        reason="Exact amount and reference match.",
    )

    assert result.transaction_id == "pay_001"
    assert result.settlement_id == "set_001"
    assert result.status == ReconciliationStatus.MATCHED
    assert result.expected_amount == Money(100000)
    assert result.actual_amount == Money(100000)
    assert result.difference == Money(0)
    assert result.reason == "Exact amount and reference match."


def test_reconciliation_result_supports_missing_settlement() -> None:
    result = ReconciliationResult(
        transaction_id="pay_002",
        settlement_id=None,
        status=ReconciliationStatus.MISSING_TRANSACTION,
        expected_amount=Money(50000),
        actual_amount=None,
        difference=None,
        reason="No settlement record was found.",
    )

    assert result.settlement_id is None
    assert result.actual_amount is None
    assert result.difference is None
    assert result.status == ReconciliationStatus.MISSING_TRANSACTION


def test_reconciliation_result_supports_amount_mismatch() -> None:
    result = ReconciliationResult(
        transaction_id="pay_003",
        settlement_id="set_003",
        status=ReconciliationStatus.MISMATCH,
        expected_amount=Money(100000),
        actual_amount=Money(98000),
        difference=Money(2000),
        reason="Settlement amount is lower than transaction amount.",
    )

    assert result.status == ReconciliationStatus.MISMATCH
    assert result.difference == Money(2000)


def test_reconciliation_result_requires_transaction_id() -> None:
    with pytest.raises(ValueError, match="transaction_id"):
        ReconciliationResult(
            transaction_id="",
            settlement_id="set_001",
            status=ReconciliationStatus.MATCHED,
            expected_amount=Money(1000),
            actual_amount=Money(1000),
            difference=Money(0),
            reason="Matched.",
        )


def test_reconciliation_result_requires_reason() -> None:
    with pytest.raises(ValueError, match="reason"):
        ReconciliationResult(
            transaction_id="pay_001",
            settlement_id="set_001",
            status=ReconciliationStatus.MATCHED,
            expected_amount=Money(1000),
            actual_amount=Money(1000),
            difference=Money(0),
            reason="",
        )


def test_reconciliation_result_is_immutable() -> None:
    result = ReconciliationResult(
        transaction_id="pay_001",
        settlement_id="set_001",
        status=ReconciliationStatus.MATCHED,
        expected_amount=Money(1000),
        actual_amount=Money(1000),
        difference=Money(0),
        reason="Matched.",
    )

    with pytest.raises(AttributeError):
        result.transaction_id = "pay_002"