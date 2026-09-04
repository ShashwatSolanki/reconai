import pytest

from app.domain.exception import ExceptionCategory, ExceptionSeverity, FinancialException
from app.domain.money import Money


def test_financial_exception_can_be_created() -> None:
    exception = FinancialException(
        exception_id="exc_001",
        transaction_id="pay_001",
        settlement_id="set_001",
        category=ExceptionCategory.AMOUNT_MISMATCH,
        severity=ExceptionSeverity.MEDIUM,
        expected_amount=Money(100000),
        actual_amount=Money(98000),
        difference=Money(2000),
        description="Settlement amount is lower than transaction amount.",
    )

    assert exception.exception_id == "exc_001"
    assert exception.transaction_id == "pay_001"
    assert exception.settlement_id == "set_001"
    assert exception.category == ExceptionCategory.AMOUNT_MISMATCH
    assert exception.severity == ExceptionSeverity.MEDIUM
    assert exception.difference == Money(2000)


def test_financial_exception_can_have_no_settlement() -> None:
    exception = FinancialException(
        exception_id="exc_002",
        transaction_id="pay_002",
        settlement_id=None,
        category=ExceptionCategory.MISSING_SETTLEMENT,
        severity=ExceptionSeverity.HIGH,
        expected_amount=Money(50000),
        actual_amount=None,
        difference=None,
        description="No settlement record was found.",
    )

    assert exception.settlement_id is None
    assert exception.category == ExceptionCategory.MISSING_SETTLEMENT


def test_financial_exception_supports_duplicate_category() -> None:
    exception = FinancialException(
        exception_id="exc_003",
        transaction_id="pay_003",
        settlement_id="set_003",
        category=ExceptionCategory.DUPLICATE_SETTLEMENT,
        severity=ExceptionSeverity.HIGH,
        expected_amount=Money(100000),
        actual_amount=Money(100000),
        difference=Money(0),
        description="Multiple settlement records reference the same transaction.",
    )

    assert exception.category == ExceptionCategory.DUPLICATE_SETTLEMENT


def test_financial_exception_requires_exception_id() -> None:
    with pytest.raises(ValueError, match="exception_id"):
        FinancialException(
            exception_id="",
            transaction_id="pay_001",
            settlement_id=None,
            category=ExceptionCategory.MISSING_SETTLEMENT,
            severity=ExceptionSeverity.HIGH,
            expected_amount=Money(1000),
            actual_amount=None,
            difference=None,
            description="Missing settlement.",
        )


def test_financial_exception_requires_description() -> None:
    with pytest.raises(ValueError, match="description"):
        FinancialException(
            exception_id="exc_001",
            transaction_id="pay_001",
            settlement_id=None,
            category=ExceptionCategory.MISSING_SETTLEMENT,
            severity=ExceptionSeverity.HIGH,
            expected_amount=Money(1000),
            actual_amount=None,
            difference=None,
            description="",
        )


def test_financial_exception_is_immutable() -> None:
    exception = FinancialException(
        exception_id="exc_001",
        transaction_id="pay_001",
        settlement_id=None,
        category=ExceptionCategory.MISSING_SETTLEMENT,
        severity=ExceptionSeverity.HIGH,
        expected_amount=Money(1000),
        actual_amount=None,
        difference=None,
        description="Missing settlement.",
    )

    with pytest.raises(AttributeError):
        exception.severity = ExceptionSeverity.LOW