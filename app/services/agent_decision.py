from __future__ import annotations

from app.domain.agent_decision import AgentDecision
from app.domain.exception import ExceptionSeverity
from app.domain.exception_investigation import (
    InvestigationRecommendation,
    InvestigationResult,
)
from app.domain.investigation_context import InvestigationContext


class AgentDecisionService:
    """Apply deterministic safety rules to investigation recommendations."""

    MIN_RESOLUTION_CONFIDENCE = 0.90

    def decide(
        self,
        context: InvestigationContext,
        investigation: InvestigationResult,
    ) -> AgentDecision:
        """Choose whether an investigated exception can be safely resolved."""

        if context.exception.severity == ExceptionSeverity.CRITICAL:
            return AgentDecision(
                action="escalate",
                requires_human_review=True,
                reason="Critical exceptions always require human review.",
            )

        if investigation.recommendation != InvestigationRecommendation.ACCEPT_SETTLEMENT:
            return AgentDecision(
                action="escalate",
                requires_human_review=True,
                reason="Investigation did not recommend accepting the settlement.",
            )

        if investigation.requires_human_review:
            return AgentDecision(
                action="escalate",
                requires_human_review=True,
                reason="Investigation explicitly requires human review.",
            )

        if investigation.confidence < self.MIN_RESOLUTION_CONFIDENCE:
            return AgentDecision(
                action="escalate",
                requires_human_review=True,
                reason=(
                    "Investigation confidence is below the minimum threshold "
                    "for automatic resolution."
                ),
            )

        return AgentDecision(
            action="resolve",
            requires_human_review=False,
            reason="Investigation passed all automatic-resolution guardrails.",
        )