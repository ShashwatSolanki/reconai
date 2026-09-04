from datetime import UTC, datetime

from app.domain.exception import (
    ExceptionCategory,
    ExceptionSeverity,
    FinancialException,
)
from app.domain.investigation_context import InvestigationContext
from app.domain.money import Money
from app.domain.settlement import Settlement, SettlementStatus
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus


def build_transaction() -> Transaction:
    return Transaction(
        transaction_id="pay_0001",
        merchant_id="merchant_001",
        amount=Money(100000),
        transaction_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        payment_method=PaymentMethod.UPI,
        reference_id="ref_0001",
        status=TransactionStatus.SUCCESS,
    )


def build_settlement(amount: int = 98000) -> Settlement:
    return Settlement(
        settlement_id="set_0001",
        merchant_id="merchant_001",
        amount=Money(amount),
        settlement_time=datetime(2026, 9, 2, 10, 0, tzinfo=UTC),
        reference_id="settle_ref_0001",
        transaction_reference="pay_0001",
        status=SettlementStatus.SETTLED,
    )


def build_exception() -> FinancialException:
    return FinancialException(
        exception_id="exc_0001",
        transaction_id="pay_0001",
        settlement_id="set_0001",
        category=ExceptionCategory.AMOUNT_MISMATCH,
        severity=ExceptionSeverity.MEDIUM,
        expected_amount=Money(100000),
        actual_amount=Money(98000),
        difference=Money(2000),
        description="Settlement amount differs from transaction amount.",
    )


def test_investigation_context_contains_transaction_and_settlement_facts() -> None:
    context = InvestigationContext(
        exception=build_exception(),
        transaction=build_transaction(),
        settlement=build_settlement(),
    )

    assert context.exception.exception_id == "exc_0001"
    assert context.transaction.transaction_id == "pay_0001"
    assert context.settlement is not None
    assert context.settlement.amount == Money(98000)


def test_investigation_context_allows_missing_settlement() -> None:
    exception = build_exception()
    exception = FinancialException(
        exception_id=exception.exception_id,
        transaction_id=exception.transaction_id,
        settlement_id=None,
        category=ExceptionCategory.MISSING_SETTLEMENT,
        severity=exception.severity,
        expected_amount=exception.expected_amount,
        actual_amount=None,
        difference=None,
        description="No settlement record was found.",
    )

    context = InvestigationContext(
        exception=exception,
        transaction=build_transaction(),
        settlement=None,
    )

    assert context.settlement is None
    assert context.exception.category == ExceptionCategory.MISSING_SETTLEMENT