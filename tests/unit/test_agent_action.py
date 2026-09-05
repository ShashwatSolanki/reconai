from datetime import UTC, datetime

import pytest

from app.domain.agent_decision import AgentDecision
from app.domain.audit_event import AuditEvent
from app.domain.exception import ExceptionCategory, ExceptionSeverity, FinancialException
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


def build_decision(
    action: str,
    requires_human_review: bool = False,
) -> AgentDecision:
    return AgentDecision(
        action=action,
        requires_human_review=requires_human_review,
        reason="Test decision.",
    )


def test_executor_accepts_resolve_action() -> None:
    from app.services.agent_action import AgentActionService

    service = AgentActionService()

    result = service.execute(
        context=build_context(),
        decision=build_decision("resolve"),
    )

    assert result.action == "resolve"
    assert result.executed is True
    assert result.requires_human_review is False


def test_executor_does_not_execute_escalation() -> None:
    from app.services.agent_action import AgentActionService

    service = AgentActionService()

    result = service.execute(
        context=build_context(),
        decision=build_decision("escalate", requires_human_review=True),
    )

    assert result.action == "escalate"
    assert result.executed is False
    assert result.requires_human_review is True


def test_executor_rejects_unknown_action() -> None:
    from app.services.agent_action import AgentActionService

    service = AgentActionService()

    with pytest.raises(ValueError, match="Unsupported agent action"):
        service.execute(
            context=build_context(),
            decision=build_decision("refund"),
        )


def test_executor_never_executes_critical_exception() -> None:
    from app.services.agent_action import AgentActionService

    service = AgentActionService()

    result = service.execute(
        context=build_context(ExceptionSeverity.CRITICAL),
        decision=build_decision("resolve"),
    )

    assert result.action == "escalate"
    assert result.executed is False
    assert result.requires_human_review is True


def test_executor_does_not_execute_when_human_review_is_required() -> None:
    from app.services.agent_action import AgentActionService

    service = AgentActionService()

    result = service.execute(
        context=build_context(),
        decision=build_decision("resolve", requires_human_review=True),
    )

    assert result.action == "escalate"
    assert result.executed is False
    assert result.requires_human_review is True


def test_executor_emits_audit_event_for_resolve() -> None:
    from app.services.agent_action import AgentActionService

    timestamp = datetime(2026, 9, 5, 10, 0, tzinfo=UTC)
    service = AgentActionService(
        clock=lambda: timestamp,
        event_id_factory=lambda: "audit_0001",
    )

    result = service.execute(
        context=build_context(),
        decision=build_decision("resolve"),
    )

    assert isinstance(result.audit_event, AuditEvent)
    assert result.audit_event.event_id == "audit_0001"
    assert result.audit_event.exception_id == "exc_0001"
    assert result.audit_event.action == "resolve"
    assert result.audit_event.actor == "agent"
    assert result.audit_event.executed is True
    assert result.audit_event.timestamp == timestamp


def test_executor_emits_audit_event_for_escalation() -> None:
    from app.services.agent_action import AgentActionService

    timestamp = datetime(2026, 9, 5, 10, 0, tzinfo=UTC)
    service = AgentActionService(
        clock=lambda: timestamp,
        event_id_factory=lambda: "audit_0002",
    )

    result = service.execute(
        context=build_context(),
        decision=build_decision("escalate", requires_human_review=True),
    )

    assert result.audit_event.event_id == "audit_0002"
    assert result.audit_event.exception_id == "exc_0001"
    assert result.audit_event.action == "escalate"
    assert result.audit_event.actor == "agent"
    assert result.audit_event.executed is False
    assert result.audit_event.timestamp == timestamp