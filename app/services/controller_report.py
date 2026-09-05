from __future__ import annotations

from pathlib import Path

from app.domain.controller_evaluation import (
    BatchControllerResult,
    ControllerExceptionOutcome,
)


class ControllerReportGenerator:
    """Render an execution-derived finance controller report for review."""

    def write(self, result: BatchControllerResult, path: Path) -> None:
        """Write the controller evaluation report as Markdown."""

        breakdown = "\n".join(
            f"| {category.value.replace('_', ' ').title()} | {count} |"
            for category, count in result.exception_breakdown.items()
            if count
        )
        escalations = "\n".join(
            self._escalation_row(outcome)
            for outcome in result.exception_outcomes
            if outcome.action.requires_human_review
        )
        escalation_section = (
            "No exceptions require human review."
            if not escalations
            else (
                "| Exception ID | Category | Difference (paise) | Reason | Action |\n"
                "|---|---|---:|---|---|\n"
                f"{escalations}"
            )
        )

        report = f"""# ReconAI - Finance Controller Evaluation

## Dataset

- Records: `{result.total_records}`
- Seed: `{result.seed}`
- Data: controlled synthetic records with known ground truth

## Reconciliation

| Metric | Result |
|---|---:|
| Matched | {result.matched_records} |
| Exceptions | {result.exception_records} |
| Match rate | {result.match_rate:.2%} |

## Exception Handling

| Metric | Result |
|---|---:|
| Investigated | {result.investigated_records} |
| Automatically resolved | {result.resolved_records} |
| Escalated to human review | {result.escalated_records} |
| Without a final outcome | {result.unresolved_records} |
| Average investigation confidence | {result.average_investigation_confidence:.2%} |

## Verified Evaluation

| Metric | Result |
|---|---:|
| Status accuracy | {result.status_accuracy:.2%} |
| Exception precision | {result.exception_precision:.2%} |
| Exception recall | {result.exception_recall:.2%} |

## Performance

| Metric | Result |
|---|---:|
| Processing time | {result.processing_time_seconds:.4f} seconds |
| Throughput | {result.throughput_records_per_second:.2f} records/second |

## Exception Breakdown

| Category | Count |
|---|---:|
{breakdown}

## Exceptions Requiring Human Review

{escalation_section}

## Limitations

This evaluation uses controlled synthetic data and deterministic ground truth.
It demonstrates pipeline correctness and measured local benchmark behavior, not
production accuracy or production throughput. Escalated exceptions have a final
safe routing outcome, but remain pending human review.
"""

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report)

    @staticmethod
    def _escalation_row(outcome: ControllerExceptionOutcome) -> str:
        exception = outcome.exception
        difference = exception.difference.amount if exception.difference else "N/A"
        return (
            f"| {exception.exception_id} | {exception.category.value} | {difference} | "
            f"{outcome.action.reason} | ESCALATED |"
        )
