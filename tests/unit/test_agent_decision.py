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


def build_context(
    severity: ExceptionSeverity = ExceptionSeverity.MEDIUM,
) -> InvestigationContext:
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
        severity=severity,
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


def build_investigation(
    *,
    recommendation: InvestigationRecommendation,
    confidence: float,
    requires_human_review: bool,
) -> InvestigationResult:
    return InvestigationResult(
        exception_id="exc_0001",
        root_cause=RootCauseCategory.FEE_DEDUCTION,
        explanation="Settlement difference is consistent with a fee deduction.",
        evidence=[
            "Transaction amount: 100000 paise",
            "Settlement amount: 98000 paise",
            "Difference: 2000 paise",
        ],
        recommendation=recommendation,
        confidence=confidence,
        requires_human_review=requires_human_review,
    )


def test_agent_resolves_high_confidence_safe_recommendation() -> None:
    from app.services.agent_decision import AgentDecisionService

    service = AgentDecisionService()

    decision = service.decide(
        context=build_context(),
        investigation=build_investigation(
            recommendation=InvestigationRecommendation.ACCEPT_SETTLEMENT,
            confidence=0.95,
            requires_human_review=False,
        ),
    )

    assert decision.action == "resolve"
    assert decision.requires_human_review is False


def test_agent_escalates_low_confidence_investigation() -> None:
    from app.services.agent_decision import AgentDecisionService

    service = AgentDecisionService()

    decision = service.decide(
        context=build_context(),
        investigation=build_investigation(
            recommendation=InvestigationRecommendation.ACCEPT_SETTLEMENT,
            confidence=0.60,
            requires_human_review=False,
        ),
    )

    assert decision.action == "escalate"
    assert decision.requires_human_review is True


def test_agent_escalates_when_investigation_requires_human_review() -> None:
    from app.services.agent_decision import AgentDecisionService

    service = AgentDecisionService()

    decision = service.decide(
        context=build_context(),
        investigation=build_investigation(
            recommendation=InvestigationRecommendation.ESCALATE,
            confidence=0.99,
            requires_human_review=True,
        ),
    )

    assert decision.action == "escalate"
    assert decision.requires_human_review is True


def test_agent_escalates_critical_exceptions() -> None:
    from app.services.agent_decision import AgentDecisionService

    service = AgentDecisionService()

    decision = service.decide(
        context=build_context(severity=ExceptionSeverity.CRITICAL),
        investigation=build_investigation(
            recommendation=InvestigationRecommendation.ACCEPT_SETTLEMENT,
            confidence=0.99,
            requires_human_review=False,
        ),
    )

    assert decision.action == "escalate"
    assert decision.requires_human_review is True


def test_agent_never_resolves_an_escalation_recommendation() -> None:
    from app.services.agent_decision import AgentDecisionService

    service = AgentDecisionService()

    investigation = build_investigation(
        recommendation=InvestigationRecommendation.ESCALATE,
        confidence=1.0,
        requires_human_review=True,
    )

    decision = service.decide(
        context=build_context(),
        investigation=investigation,
    )

    assert decision.action == "escalate"
    assert decision.requires_human_review is True