from __future__ import annotations

from dataclasses import dataclass

from app.domain.agent_decision import AgentAction, AgentDecision
from app.domain.exception import ExceptionSeverity
from app.domain.investigation_context import InvestigationContext


@dataclass(frozen=True, slots=True)
class AgentActionResult:
    """Outcome of attempting to execute an agent decision."""

    action: str
    executed: bool
    requires_human_review: bool
    reason: str


class AgentActionService:
    """Execute only actions that pass the financial safety boundary."""

    def execute(
        self,
        context: InvestigationContext,
        decision: AgentDecision,
    ) -> AgentActionResult:
        """Execute a bounded agent action or escalate it safely."""

        if decision.action not in {action.value for action in AgentAction}:
            raise ValueError(f"Unsupported agent action: {decision.action}")

        if context.exception.severity == ExceptionSeverity.CRITICAL:
            return AgentActionResult(
                action=AgentAction.ESCALATE.value,
                executed=False,
                requires_human_review=True,
                reason="Critical exceptions cannot be automatically executed.",
            )

        if decision.requires_human_review:
            return AgentActionResult(
                action=AgentAction.ESCALATE.value,
                executed=False,
                requires_human_review=True,
                reason="Human review is required before execution.",
            )

        if decision.action == AgentAction.ESCALATE.value:
            return AgentActionResult(
                action=AgentAction.ESCALATE.value,
                executed=False,
                requires_human_review=True,
                reason="Escalation actions are routed to human review.",
            )

        return AgentActionResult(
            action=AgentAction.RESOLVE.value,
            executed=True,
            requires_human_review=False,
            reason="Resolve action passed the execution safety boundary.",
        )