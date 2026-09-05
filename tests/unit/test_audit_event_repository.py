from datetime import UTC, datetime

import pytest

from app.domain.audit_event import AuditEvent


def build_event() -> AuditEvent:
    return AuditEvent(
        event_id="audit_0001",
        exception_id="exc_0001",
        action="resolve",
        actor="agent",
        reason="Investigation passed all automatic-resolution guardrails.",
        executed=True,
        timestamp=datetime(2026, 9, 5, 10, 0, tzinfo=UTC),
    )


def test_repository_can_save_and_retrieve_audit_event() -> None:
    from app.repositories.audit_event_repository import AuditEventRepository

    repository = AuditEventRepository()

    event = build_event()
    repository.save(event)

    assert repository.get("audit_0001") == event


def test_repository_returns_none_for_unknown_event() -> None:
    from app.repositories.audit_event_repository import AuditEventRepository

    repository = AuditEventRepository()

    assert repository.get("does_not_exist") is None


def test_repository_rejects_duplicate_event_id() -> None:
    from app.repositories.audit_event_repository import AuditEventRepository

    repository = AuditEventRepository()

    event = build_event()
    repository.save(event)

    duplicate = AuditEvent(
        event_id=event.event_id,
        exception_id="exc_0002",
        action="escalate",
        actor="agent",
        reason="Duplicate event test.",
        executed=False,
        timestamp=datetime(2026, 9, 5, 11, 0, tzinfo=UTC),
    )

    with pytest.raises(ValueError, match="already exists"):
        repository.save(duplicate)


def test_repository_returns_audit_events_for_exception() -> None:
    from app.repositories.audit_event_repository import AuditEventRepository

    repository = AuditEventRepository()

    first_event = build_event()

    second_event = AuditEvent(
        event_id="audit_0002",
        exception_id=first_event.exception_id,
        action="escalate",
        actor="agent",
        reason="Human review required.",
        executed=False,
        timestamp=datetime(2026, 9, 5, 11, 0, tzinfo=UTC),
    )

    unrelated_event = AuditEvent(
        event_id="audit_0003",
        exception_id="exc_0002",
        action="resolve",
        actor="agent",
        reason="Unrelated exception.",
        executed=True,
        timestamp=datetime(2026, 9, 5, 12, 0, tzinfo=UTC),
    )

    repository.save(first_event)
    repository.save(second_event)
    repository.save(unrelated_event)

    events = repository.get_by_exception(first_event.exception_id)

    assert events == [first_event, second_event]