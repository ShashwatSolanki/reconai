from datetime import UTC, datetime

import pytest

from app.domain.audit_event import AuditEvent


def test_audit_event_stores_agent_action_details() -> None:
    timestamp = datetime(2026, 9, 5, 10, 0, tzinfo=UTC)

    event = AuditEvent(
        event_id="audit_0001",
        exception_id="exc_0001",
        action="resolve",
        actor="agent",
        reason="Investigation passed all automatic-resolution guardrails.",
        executed=True,
        timestamp=timestamp,
    )

    assert event.event_id == "audit_0001"
    assert event.exception_id == "exc_0001"
    assert event.action == "resolve"
    assert event.actor == "agent"
    assert event.reason == "Investigation passed all automatic-resolution guardrails."
    assert event.executed is True
    assert event.timestamp == timestamp


def test_audit_event_is_immutable() -> None:
    event = AuditEvent(
        event_id="audit_0001",
        exception_id="exc_0001",
        action="resolve",
        actor="agent",
        reason="Automatic resolution approved.",
        executed=True,
        timestamp=datetime(2026, 9, 5, 10, 0, tzinfo=UTC),
    )

    with pytest.raises(AttributeError):
        event.action = "escalate"  # type: ignore[misc]


def test_audit_event_requires_timezone_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="timestamp must include timezone"):
        AuditEvent(
            event_id="audit_0001",
            exception_id="exc_0001",
            action="resolve",
            actor="agent",
            reason="Automatic resolution approved.",
            executed=True,
            timestamp=datetime(2026, 9, 5, 10, 0),
        )


def test_audit_event_rejects_empty_identifiers() -> None:
    timestamp = datetime(2026, 9, 5, 10, 0, tzinfo=UTC)

    with pytest.raises(ValueError, match="event_id"):
        AuditEvent(
            event_id="",
            exception_id="exc_0001",
            action="resolve",
            actor="agent",
            reason="Automatic resolution approved.",
            executed=True,
            timestamp=timestamp,
        )

    with pytest.raises(ValueError, match="exception_id"):
        AuditEvent(
            event_id="audit_0001",
            exception_id="",
            action="resolve",
            actor="agent",
            reason="Automatic resolution approved.",
            executed=True,
            timestamp=timestamp,
        )


def test_audit_event_rejects_empty_action_actor_or_reason() -> None:
    timestamp = datetime(2026, 9, 5, 10, 0, tzinfo=UTC)

    with pytest.raises(ValueError, match="action"):
        AuditEvent(
            event_id="audit_0001",
            exception_id="exc_0001",
            action="",
            actor="agent",
            reason="Automatic resolution approved.",
            executed=True,
            timestamp=timestamp,
        )

    with pytest.raises(ValueError, match="actor"):
        AuditEvent(
            event_id="audit_0001",
            exception_id="exc_0001",
            action="resolve",
            actor="",
            reason="Automatic resolution approved.",
            executed=True,
            timestamp=timestamp,
        )

    with pytest.raises(ValueError, match="reason"):
        AuditEvent(
            event_id="audit_0001",
            exception_id="exc_0001",
            action="resolve",
            actor="agent",
            reason="",
            executed=True,
            timestamp=timestamp,
        )