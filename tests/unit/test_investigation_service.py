from app.domain.exception import (
    ExceptionCategory,
    ExceptionSeverity,
    FinancialException,
)
from app.domain.exception_investigation import (
    InvestigationRecommendation,
    RootCauseCategory,
)
from app.domain.money import Money
from app.services.investigation_service import InvestigationService


def build_exception(
    category: ExceptionCategory,
    difference: int | None = 2000,
) -> FinancialException:
    return FinancialException(
        exception_id="exc_0001",
        transaction_id="pay_0001",
        settlement_id="set_0001",
        category=category,
        severity=ExceptionSeverity.MEDIUM,
        expected_amount=Money(100000),
        actual_amount=Money(
            100000 if difference is None else 100000 - difference
        ),
        difference=None if difference is None else Money(difference),
        description="Settlement amount differs from transaction amount.",
    )


def test_investigation_service_identifies_fee_deduction() -> None:
    exception = build_exception(ExceptionCategory.AMOUNT_MISMATCH, 2000)

    result = InvestigationService().investigate(exception)

    assert result.exception_id == "exc_0001"
    assert result.root_cause == RootCauseCategory.FEE_DEDUCTION
    assert result.recommendation == InvestigationRecommendation.ACCEPT_SETTLEMENT
    assert result.confidence > 0.0
    assert result.evidence


def test_investigation_service_identifies_missing_settlement() -> None:
    exception = build_exception(ExceptionCategory.MISSING_SETTLEMENT, None)

    result = InvestigationService().investigate(exception)

    assert result.root_cause == RootCauseCategory.UNKNOWN
    assert result.recommendation == InvestigationRecommendation.ESCALATE
    assert result.requires_human_review is True


def test_investigation_service_identifies_duplicate_settlement() -> None:
    exception = build_exception(ExceptionCategory.DUPLICATE_SETTLEMENT, None)

    result = InvestigationService().investigate(exception)

    assert result.root_cause == RootCauseCategory.DUPLICATE_SETTLEMENT
    assert result.recommendation == InvestigationRecommendation.ESCALATE
    assert result.requires_human_review is True


def test_investigation_service_identifies_partial_settlement() -> None:
    exception = build_exception(ExceptionCategory.PARTIAL_SETTLEMENT, 2000)

    result = InvestigationService().investigate(exception)

    assert result.root_cause == RootCauseCategory.PARTIAL_SETTLEMENT
    assert result.recommendation == InvestigationRecommendation.ACCEPT_SETTLEMENT
    assert result.requires_human_review is False


def test_investigation_service_escalates_unknown_exception() -> None:
    exception = build_exception(ExceptionCategory.UNKNOWN, None)

    result = InvestigationService().investigate(exception)

    assert result.root_cause == RootCauseCategory.UNKNOWN
    assert result.recommendation == InvestigationRecommendation.ESCALATE
    assert result.requires_human_review is True