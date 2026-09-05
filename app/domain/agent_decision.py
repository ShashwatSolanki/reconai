from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AgentAction(StrEnum):
    """Actions that the agent is permitted to request."""

    RESOLVE = "resolve"
    ESCALATE = "escalate"


@dataclass(frozen=True, slots=True)
class AgentDecision:
    """Deterministic decision produced by the agent guardrail layer."""

    action: str
    requires_human_review: bool
    reason: str

    def __post_init__(self) -> None:
        if self.action not in {action.value for action in AgentAction}:
            raise ValueError(f"Unsupported agent action: {self.action}")

        if not self.reason.strip():
            raise ValueError("reason cannot be empty.")