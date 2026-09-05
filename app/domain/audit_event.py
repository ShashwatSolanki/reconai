from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """Immutable record of an agent action and its outcome."""

    event_id: str
    exception_id: str
    action: str
    actor: str
    reason: str
    executed: bool
    timestamp: datetime

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id cannot be empty.")

        if not self.exception_id.strip():
            raise ValueError("exception_id cannot be empty.")

        if not self.action.strip():
            raise ValueError("action cannot be empty.")

        if not self.actor.strip():
            raise ValueError("actor cannot be empty.")

        if not self.reason.strip():
            raise ValueError("reason cannot be empty.")

        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must include timezone information.")