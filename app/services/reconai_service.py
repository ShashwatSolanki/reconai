from __future__ import annotations

from typing import Any

from app.domain.exception import (
    ExceptionCategory,
    ExceptionSeverity,
    FinancialException,
)
from app.domain.investigation_context import InvestigationContext
from app.domain.reconciliation import ReconciliationResult, ReconciliationStatus
from app.domain.settlement import Settlement
from app.domain.transaction import Transaction
from app.services.agent_action import AgentActionResult, AgentActionService
from app.services.agent_decision import AgentDecisionService
from app.services.investigation_service import InvestigationService


class ReconAIService:
    """Coordinate the end-to-end reconciliation exception workflow."""

    def __init__(self) -> None:
        self._investigator = InvestigationService()
        self._decision_service = AgentDecisionService()
        self._action_service = AgentActionService()

        self.exceptions: dict[str, FinancialException] = {}
        self.contexts: dict[str, InvestigationContext] = {}
        self.investigations: dict[str, Any] = {}
        self.actions: dict[str, AgentActionResult] = {}
        self.latest_reconciliation_summary: dict[str, int] = {
            "total_transactions": 0,
            "matched": 0,
            "partial_matches": 0,
            "mismatches": 0,
            "missing_settlements": 0,
            "duplicates": 0,
        }
    def register_exception(
        self,
        result: ReconciliationResult,
        transaction: Transaction,
        settlement: Settlement | None,
    ) -> FinancialException | None:
        """Register an exception when reconciliation does not match."""

        if result.status == ReconciliationStatus.MATCHED:
            return None

        category_map = {
            ReconciliationStatus.PARTIAL_MATCH: ExceptionCategory.PARTIAL_SETTLEMENT,
            ReconciliationStatus.MISMATCH: ExceptionCategory.AMOUNT_MISMATCH,
            ReconciliationStatus.MISSING_SETTLEMENT: (
                ExceptionCategory.MISSING_SETTLEMENT
            ),
            ReconciliationStatus.DUPLICATE: ExceptionCategory.DUPLICATE_SETTLEMENT,
            ReconciliationStatus.UNRESOLVED: ExceptionCategory.UNKNOWN,
        }

        category = category_map[result.status]

        exception = FinancialException(
            exception_id=f"exc_{transaction.transaction_id}",
            transaction_id=transaction.transaction_id,
            settlement_id=settlement.settlement_id if settlement else None,
            category=category,
            severity=self._severity_for(category),
            expected_amount=result.expected_amount,
            actual_amount=result.actual_amount,
            difference=result.difference,
            description=result.reason,
        )

        context = InvestigationContext(
            exception=exception,
            transaction=transaction,
            settlement=settlement,
        )

        self.exceptions[exception.exception_id] = exception
        self.contexts[exception.exception_id] = context

        return exception

    def investigate(self, exception_id: str) -> dict[str, Any]:
        """Investigate an exception and apply the agent safety boundary."""

        context = self.contexts.get(exception_id)

        if context is None:
            raise KeyError(f"Exception not found: {exception_id}")

        investigation = self._investigator.investigate(context)
        decision = self._decision_service.decide(context, investigation)
        action = self._action_service.execute(context, decision)

        self.investigations[exception_id] = investigation
        self.actions[exception_id] = action

        return {
            "exception": context.exception,
            "investigation": investigation,
            "decision": decision,
            "action": action,
            "audit_event": action.audit_event,
        }

    @staticmethod
    def _severity_for(category: ExceptionCategory) -> ExceptionSeverity:
        if category == ExceptionCategory.DUPLICATE_SETTLEMENT:
            return ExceptionSeverity.HIGH

        if category in {
            ExceptionCategory.AMOUNT_MISMATCH,
            ExceptionCategory.PARTIAL_SETTLEMENT,
        }:
            return ExceptionSeverity.MEDIUM

        return ExceptionSeverity.HIGH

    def record_reconciliation_summary(
        self,
        *,
        total_transactions: int,
        matched: int,
        partial_matches: int,
        mismatches: int,
        missing_settlements: int,
        duplicates: int,
    ) -> None:
        self.latest_reconciliation_summary = {
            "total_transactions": total_transactions,
            "matched": matched,
            "partial_matches": partial_matches,
            "mismatches": mismatches,
            "missing_settlements": missing_settlements,
            "duplicates": duplicates,
        }