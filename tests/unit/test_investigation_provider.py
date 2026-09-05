from datetime import UTC, datetime

from app.domain.exception import (
    ExceptionCategory,
    ExceptionSeverity,
    FinancialException,
)
from app.domain.exception_investigation import (
    InvestigationRecommendation,
    InvestigationResult,
    RootCauseCategory,
)
from app.domain.investigation_context import InvestigationContext
from app.domain.money import Money
from app.domain.settlement import Settlement, SettlementStatus
from app.domain.transaction import PaymentMethod, Transaction, TransactionStatus
from app.services.investigation_provider import InvestigationProvider


def build_context() -> InvestigationContext:
    transaction = Transaction(
        transaction_id="pay_0001",
        merchant_id="merchant_001",
        amount=Money(100000),
        transaction_time=datetime(2026, 9, 1, 10, 0, tzinfo=UTC),
        payment_method=PaymentMethod.UPI,
        reference_id="ref_0001",
        status=TransactionStatus.SUCCESS,
    )

    settlement = Settlement(
        settlement_id="set_0001",
        merchant_id="merchant_001",
        amount=Money(98000),
        settlement_time=datetime(2026, 9, 2, 10, 0, tzinfo=UTC),
        reference_id="settle_ref_0001",
        transaction_reference="pay_0001",
        status=SettlementStatus.SETTLED,
    )

    exception = FinancialException(
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

    return InvestigationContext(
        exception=exception,
        transaction=transaction,
        settlement=settlement,
    )


class FakeInvestigationProvider(InvestigationProvider):
    def investigate(self, context: InvestigationContext) -> InvestigationResult:
        return InvestigationResult(
            exception_id=context.exception.exception_id,
            root_cause=RootCauseCategory.UNKNOWN,
            explanation="Fake provider result.",
            evidence=["Fake provider evidence."],
            recommendation=InvestigationRecommendation.ESCALATE,
            confidence=0.10,
            requires_human_review=True,
        )


def test_investigation_provider_defines_provider_contract() -> None:
    assert hasattr(InvestigationProvider, "investigate")


def test_fake_provider_implements_investigation_contract() -> None:
    context = build_context()
    provider = FakeInvestigationProvider()

    result = provider.investigate(context)

    assert result.exception_id == context.exception.exception_id
    assert result.root_cause == RootCauseCategory.UNKNOWN
    assert result.recommendation == InvestigationRecommendation.ESCALATE
    assert result.requires_human_review is True