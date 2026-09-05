from __future__ import annotations

from dataclasses import dataclass

from app.domain.exception import ExceptionCategory, FinancialException
from app.domain.exception_investigation import InvestigationResult
from app.services.agent_action import AgentActionResult


@dataclass(frozen=True, slots=True)
class ControllerExceptionOutcome:
    """The investigated and audited result for one detected exception."""

    exception: FinancialException
    investigation: InvestigationResult
    action: AgentActionResult


@dataclass(frozen=True, slots=True)
class BatchControllerResult:
    """Measured end-to-end results from the finance-controller batch workflow."""

    seed: int
    total_records: int
    matched_records: int
    exception_records: int
    investigated_records: int
    resolved_records: int
    escalated_records: int
    unresolved_records: int
    status_accuracy: float
    exception_precision: float
    exception_recall: float
    processing_time_seconds: float
    throughput_records_per_second: float
    average_investigation_confidence: float
    exception_breakdown: dict[ExceptionCategory, int]
    exception_outcomes: list[ControllerExceptionOutcome]

    @property
    def match_rate(self) -> float:
        """Return the proportion of all records reconciled as exact matches."""

        return self.matched_records / self.total_records if self.total_records else 0.0
