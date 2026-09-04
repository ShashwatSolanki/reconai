from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BatchReconciliationSummary:
    """Aggregate counts produced from a batch reconciliation run."""

    total_transactions: int
    matched: int
    partial_matches: int
    mismatches: int
    missing_settlements: int
    duplicates: int
