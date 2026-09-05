from __future__ import annotations

from app.domain.audit_event import AuditEvent


class AuditEventRepository:
    """In-memory repository for audit events."""

    def __init__(self) -> None:
        self._events: dict[str, AuditEvent] = {}

    def save(self, event: AuditEvent) -> None:
        """Store an audit event by its unique event ID."""
        if event.event_id in self._events:
            raise ValueError(f"Audit event already exists: {event.event_id}")

        self._events[event.event_id] = event

    def get(self, event_id: str) -> AuditEvent | None:
        """Return an audit event by ID, or None when it does not exist."""
        return self._events.get(event_id)

    def get_by_exception(self, exception_id: str) -> list[AuditEvent]:
        """Return all audit events associated with an exception."""
        return [
            event
            for event in self._events.values()
            if event.exception_id == exception_id
        ]
