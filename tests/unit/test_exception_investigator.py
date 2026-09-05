from datetime import UTC, datetime

import pytest

from app.domain.exception import (
    ExceptionCategory,
    ExceptionSeverity,
    FinancialException,
)
from app.domain.investigation_context import InvestigationContext
from app.domain.money import Money
from app.domain.settlement import Settlement, SettlementStatus
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus
from app.services.exception_investigator import ExceptionInvestigator


def make_context(
    *,
    category: ExceptionCategory = ExceptionCategory.AMOUNT_MISMATCH,
    settlement_amount: int = 9700,
    settlement_reference: str = "set_ref_001",
    transaction_reference: str = "txn_ref_001",
) -> InvestigationContext:
    transaction = Transaction(
        transaction_id="txn_001",
        merchant_id="merchant_001",
        amount=Money(10000),
        transaction_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        payment_method=PaymentMethod.UPI,
        reference_id=transaction_reference,
        status=TransactionStatus.SUCCESS,
    )

    settlement = Settlement(
        settlement_id="set_001",
        merchant_id="merchant_001",
        amount=Money(settlement_amount),
        settlement_time=datetime(2026, 9, 2, 10, 0, tzinfo=UTC),
        reference_id=settlement_reference,
        transaction_reference=transaction_reference,
        status=SettlementStatus.SETTLED,
    )

    exception = FinancialException(
        exception_id="exc_txn_001",
        transaction_id="txn_001",
        settlement_id="set_001",
        category=category,
        severity=ExceptionSeverity.MEDIUM,
        expected_amount=Money(10000),
        actual_amount=Money(settlement_amount),
        difference=Money(10000 - settlement_amount),
        description="Settlement amount differs from transaction amount.",
    )

    return InvestigationContext(
        exception=exception,
        transaction=transaction,
        settlement=settlement,
    )


def test_investigates_fee_deduction_from_amount_difference() -> None:
    context = make_context(settlement_amount=9700)

    result = ExceptionInvestigator().investigate(context)

    assert result.exception_id == "exc_txn_001"
    assert result.root_cause.value == "fee_deduction"
    assert result.recommendation.value == "accept_settlement"
    assert result.confidence >= 0.8
    assert result.requires_human_review is False
    assert result.evidence
    assert any("10000" in item for item in result.evidence)
    assert any("9700" in item for item in result.evidence)


def test_investigates_partial_settlement() -> None:
    context = make_context(
        category=ExceptionCategory.PARTIAL_SETTLEMENT,
        settlement_amount=6000,
    )

    result = ExceptionInvestigator().investigate(context)

    assert result.root_cause.value == "partial_settlement"
    assert result.recommendation.value == "retry_reconciliation"
    assert result.requires_human_review is False


def test_investigates_duplicate_settlement() -> None:
    context = make_context(
        category=ExceptionCategory.DUPLICATE_SETTLEMENT,
    )

    result = ExceptionInvestigator().investigate(context)

    assert result.root_cause.value == "duplicate_settlement"
    assert result.recommendation.value == "escalate"
    assert result.requires_human_review is True


def test_reference_mismatch_requires_human_review() -> None:
    context = make_context(
        category=ExceptionCategory.REFERENCE_MISMATCH,
        settlement_reference="different_reference",
        transaction_reference="txn_ref_001",
    )

    result = ExceptionInvestigator().investigate(context)

    assert result.root_cause.value == "reference_mismatch"
    assert result.recommendation.value == "escalate"
    assert result.requires_human_review is True


def test_missing_settlement_requires_human_review() -> None:
    context = make_context(
        category=ExceptionCategory.MISSING_SETTLEMENT,
    )

    context = InvestigationContext(
        exception=context.exception,
        transaction=context.transaction,
        settlement=None,
    )

    result = ExceptionInvestigator().investigate(context)

    assert result.root_cause.value == "unknown"
    assert result.recommendation.value == "escalate"
    assert result.requires_human_review is True


def test_investigation_result_has_explanation_and_evidence() -> None:
    context = make_context()

    result = ExceptionInvestigator().investigate(context)

    assert result.explanation.strip()
    assert len(result.evidence) >= 2


@pytest.mark.parametrize(
    "settlement_amount",
    [9999, 9900, 9500],
)
def test_low_settlement_amounts_are_investigated(
    settlement_amount: int,
) -> None:
    context = make_context(settlement_amount=settlement_amount)

    result = ExceptionInvestigator().investigate(context)

    assert result.explanation.strip()
    assert result.evidence
    assert 0.0 <= result.confidence <= 1.0
