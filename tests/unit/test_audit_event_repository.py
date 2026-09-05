from datetime import UTC, datetime

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