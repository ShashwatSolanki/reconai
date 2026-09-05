from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.agent_decision import AgentAction, AgentDecision
from app.domain.audit_event import AuditEvent
from app.domain.exception import ExceptionSeverity
from app.domain.investigation_context import InvestigationContext


@dataclass(frozen=True, slots=True)
class AgentActionResult:
    """Outcome of attempting to execute an agent decision."""

    action: str
    executed: bool
    requires_human_review: bool
    reason: str
    audit_event: AuditEvent


class AgentActionService:
    """Execute only actions that pass the financial safety boundary."""

    def __init__(
        self,
        clock: Callable[[], datetime] | None = None,
        event_id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._clock = clock or (lambda: datetime.now(UTC))
        self._event_id_factory = event_id_factory or (lambda: str(uuid4()))

    def execute(
        self,
        context: InvestigationContext,
        decision: AgentDecision,
    ) -> AgentActionResult:
        """Execute a bounded agent action or escalate it safely."""

        if decision.action not in {action.value for action in AgentAction}:
            raise ValueError(f"Unsupported agent action: {decision.action}")

        if context.exception.severity == ExceptionSeverity.CRITICAL:
            return self._result(
                context=context,
                action=AgentAction.ESCALATE.value,
                executed=False,
                requires_human_review=True,
                reason="Critical exceptions cannot be automatically executed.",
            )

        if decision.requires_human_review:
            return self._result(
                context=context,
                action=AgentAction.ESCALATE.value,
                executed=False,
                requires_human_review=True,
                reason="Human review is required before execution.",
            )

        if decision.action == AgentAction.ESCALATE.value:
            return self._result(
                context=context,
                action=AgentAction.ESCALATE.value,
                executed=False,
                requires_human_review=True,
                reason="Escalation actions are routed to human review.",
            )

        return self._result(
            context=context,
            action=AgentAction.RESOLVE.value,
            executed=True,
            requires_human_review=False,
            reason="Resolve action passed the execution safety boundary.",
        )

    def _result(
        self,
        context: InvestigationContext,
        action: str,
        executed: bool,
        requires_human_review: bool,
        reason: str,
    ) -> AgentActionResult:
        audit_event = AuditEvent(
            event_id=self._event_id_factory(),
            exception_id=context.exception.exception_id,
            action=action,
            actor="agent",
            reason=reason,
            executed=executed,
            timestamp=self._clock(),
        )

        return AgentActionResult(
            action=action,
            executed=executed,
            requires_human_review=requires_human_review,
            reason=reason,
            audit_event=audit_event,
        )