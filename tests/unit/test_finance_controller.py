from __future__ import annotations

from collections.abc import Callable, Iterator

from app.domain.exception import ExceptionCategory
from app.domain.exception_investigation import InvestigationResult
from app.domain.investigation_context import InvestigationContext
from app.services.finance_controller import FinanceController
from app.services.investigation_service import InvestigationService
from app.services.reconai_service import ReconAIService


class RecordingMockProvider(InvestigationService):
    """Deterministic provider that records only controller investigation calls."""

    def __init__(self) -> None:
        self.contexts: list[InvestigationContext] = []

    def investigate(self, context: InvestigationContext) -> InvestigationResult:
        self.contexts.append(context)
        return super().investigate(context)


def sequence_timer(values: Iterator[float]) -> Callable[[], float]:
    def timer() -> float:
        return next(values)

    return timer


def test_controller_processes_all_records_and_investigates_only_exceptions() -> None:
    provider = RecordingMockProvider()
    controller = FinanceController(
        ReconAIService(investigation_provider=provider),
        seed=42,
        record_count=100,
        timer=sequence_timer(iter([10.0, 12.0])),
    )

    result = controller.run()

    assert result.total_records == 100
    assert result.matched_records == 96
    assert result.exception_records == 4
    assert result.matched_records + result.exception_records == result.total_records
    assert result.investigated_records == 4
    assert len(provider.contexts) == 4
    assert result.processing_time_seconds == 2.0
    assert result.throughput_records_per_second == 50.0


def test_controller_records_resolve_escalate_and_exception_breakdown() -> None:
    controller = FinanceController(
        ReconAIService(investigation_provider=InvestigationService()),
        seed=42,
        record_count=100,
    )

    result = controller.run()

    assert result.resolved_records == 1
    assert result.escalated_records == 3
    assert result.unresolved_records == 0
    assert result.resolved_records + result.escalated_records == result.exception_records
    assert result.exception_breakdown == {
        ExceptionCategory.AMOUNT_MISMATCH: 1,
        ExceptionCategory.MISSING_SETTLEMENT: 1,
        ExceptionCategory.DUPLICATE_SETTLEMENT: 1,
        ExceptionCategory.PARTIAL_SETTLEMENT: 1,
        ExceptionCategory.REFERENCE_MISMATCH: 0,
        ExceptionCategory.UNKNOWN: 0,
    }
    assert all(
        outcome.action.audit_event.exception_id == outcome.exception.exception_id
        for outcome in result.exception_outcomes
    )


def test_controller_returns_verified_evaluation_metrics() -> None:
    controller = FinanceController(
        ReconAIService(investigation_provider=InvestigationService()),
        seed=42,
        record_count=100,
    )

    result = controller.run()

    assert result.match_rate == 0.96
    assert result.status_accuracy == 1.0
    assert result.exception_precision == 1.0
    assert result.exception_recall == 1.0
    assert result.average_investigation_confidence > 0.0
