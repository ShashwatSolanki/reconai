from datetime import UTC, datetime

from app.domain.exception import (
    ExceptionCategory,
    ExceptionSeverity,
    FinancialException,
)
from app.domain.exception_investigation import (
    InvestigationRecommendation,
    RootCauseCategory,
)
from app.domain.investigation_context import InvestigationContext
from app.domain.money import Money
from app.domain.settlement import Settlement, SettlementStatus
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus
from app.services.investigation_service import InvestigationService


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


def build_exception(
    category: ExceptionCategory,
    difference: int | None = 2000,
) -> FinancialException:
    actual_amount = (
        None
        if difference is None
        else Money(100000 - difference)
    )

    return FinancialException(
        exception_id="exc_0001",
        transaction_id="pay_0001",
        settlement_id=None if category == ExceptionCategory.MISSING_SETTLEMENT else "set_0001",
        category=category,
        severity=ExceptionSeverity.MEDIUM,
        expected_amount=Money(100000),
        actual_amount=actual_amount,
        difference=None if difference is None else Money(difference),
        description="Settlement amount differs from transaction amount.",
    )


def build_context(
    category: ExceptionCategory,
    settlement: Settlement | None,
    difference: int | None = 2000,
) -> InvestigationContext:
    return InvestigationContext(
        exception=build_exception(category, difference),
        transaction=build_transaction(),
        settlement=settlement,
    )


def test_investigation_service_identifies_fee_deduction_from_evidence() -> None:
    context = build_context(
        ExceptionCategory.AMOUNT_MISMATCH,
        build_settlement(98000),
    )

    result = InvestigationService().investigate(context)

    assert result.exception_id == "exc_0001"
    assert result.root_cause == RootCauseCategory.FEE_DEDUCTION
    assert result.recommendation == InvestigationRecommendation.ACCEPT_SETTLEMENT
    assert result.confidence > 0.0
    assert result.evidence


def test_investigation_service_does_not_call_every_mismatch_a_fee() -> None:
    context = build_context(
        ExceptionCategory.AMOUNT_MISMATCH,
        build_settlement(50000),
        difference=50000,
    )

    result = InvestigationService().investigate(context)

    assert result.root_cause == RootCauseCategory.UNKNOWN
    assert result.recommendation == InvestigationRecommendation.ESCALATE
    assert result.requires_human_review is True


def test_investigation_service_identifies_missing_settlement() -> None:
    context = build_context(
        ExceptionCategory.MISSING_SETTLEMENT,
        settlement=None,
        difference=None,
    )

    result = InvestigationService().investigate(context)

    assert result.root_cause == RootCauseCategory.UNKNOWN
    assert result.recommendation == InvestigationRecommendation.ESCALATE
    assert result.requires_human_review is True


def test_investigation_service_identifies_duplicate_settlement() -> None:
    context = build_context(
        ExceptionCategory.DUPLICATE_SETTLEMENT,
        build_settlement(),
        difference=None,
    )

    result = InvestigationService().investigate(context)

    assert result.root_cause == RootCauseCategory.DUPLICATE_SETTLEMENT
    assert result.recommendation == InvestigationRecommendation.ESCALATE
    assert result.requires_human_review is True


def test_investigation_service_identifies_partial_settlement() -> None:
    context = build_context(
        ExceptionCategory.PARTIAL_SETTLEMENT,
        build_settlement(98000),
    )

    result = InvestigationService().investigate(context)

    assert result.root_cause == RootCauseCategory.PARTIAL_SETTLEMENT
    assert result.recommendation == InvestigationRecommendation.ACCEPT_SETTLEMENT
    assert result.requires_human_review is False


def test_investigation_service_escalates_unknown_exception() -> None:
    context = build_context(
        ExceptionCategory.UNKNOWN,
        build_settlement(),
        difference=None,
    )

    result = InvestigationService().investigate(context)

    assert result.root_cause == RootCauseCategory.UNKNOWN
    assert result.recommendation == InvestigationRecommendation.ESCALATE
    assert result.requires_human_review is True