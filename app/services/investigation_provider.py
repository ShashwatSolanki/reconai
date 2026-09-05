from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.exception_investigation import InvestigationResult
from app.domain.investigation_context import InvestigationContext


class InvestigationProvider(ABC):
    """Contract for investigation providers."""

    @abstractmethod
    def investigate(self, context: InvestigationContext) -> InvestigationResult:
        """Investigate an exception using the supplied evidence."""
        raise NotImplementedError
