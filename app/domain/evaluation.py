from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class GroundTruthStatus(StrEnum):
    """Expected reconciliation outcome used as evaluation ground truth."""

    MATCHED = "matched"
    PARTIAL_MATCH = "partial_match"
    MISMATCH = "mismatch"
    MISSING_SETTLEMENT = "missing_settlement"
    DUPLICATE = "duplicate"


@dataclass(frozen=True, slots=True)
class GroundTruth:
    """Known expected outcome for a transaction in an evaluation dataset."""

    transaction_id: str
    expected_status: GroundTruthStatus
    has_exception: bool

    def __post_init__(self) -> None:
        if not self.transaction_id.strip():
            raise ValueError("transaction_id cannot be empty.")

        if (
            self.expected_status == GroundTruthStatus.MATCHED
            and self.has_exception
        ):
            raise ValueError("A matched transaction cannot have an exception.")

        if (
            self.expected_status != GroundTruthStatus.MATCHED
            and not self.has_exception
        ):
            raise ValueError("A non-matched transaction must have an exception.")