from __future__ import annotations

from pathlib import Path

from app.domain.reconciliation import ReconciliationStatus
from app.services.evaluation_runner import EvaluationRunResult


class EvaluationReportGenerator:
    """Generate a reproducible Markdown report from an evaluation run."""

    def write(self, result: EvaluationRunResult, path: Path) -> None:
        """Write measured evaluation results to a Markdown file."""
        metrics = result.metrics
        status_counts = {
            status: sum(
                reconciliation.status == status
                for reconciliation in result.reconciliation_results
            )
            for status in ReconciliationStatus
        }

        report = f"""# ReconAI Evaluation Report

## Methodology

This report contains measured results from ReconAI's deterministic
evaluation pipeline.

- Dataset: **Controlled synthetic dataset**
- Seed: `{result.seed}`
- Record count: `{result.record_count}`

The evaluation ground truth is generated from known transaction and
settlement relationships in the controlled synthetic dataset. These
results must not be interpreted as independently labeled production
performance.

## Dataset

| Metric | Value |
|---|---:|
| Transactions | {result.total_transactions} |
| Settlements | {result.total_settlements} |

## Reconciliation Outcomes

| Status | Count |
|---|---:|
| Matched | {status_counts[ReconciliationStatus.MATCHED]} |
| Partial match | {status_counts[ReconciliationStatus.PARTIAL_MATCH]} |
| Mismatch | {status_counts[ReconciliationStatus.MISMATCH]} |
| Missing settlement | {status_counts[ReconciliationStatus.MISSING_SETTLEMENT]} |
| Duplicate | {status_counts[ReconciliationStatus.DUPLICATE]} |

## Evaluation Metrics

| Metric | Result |
|---|---:|
| Status accuracy | {metrics.status_accuracy:.2%} |
| Exception precision | {metrics.exception_precision:.2%} |
| Exception recall | {metrics.exception_recall:.2%} |

### Metric Counts

- Correct status predictions: `{metrics.correct_status_predictions}`
- Actual exceptions: `{metrics.actual_exceptions}`
- Predicted exceptions: `{metrics.predicted_exceptions}`
- True-positive exceptions: `{metrics.true_positive_exceptions}`

## Interpretation

The reported metrics describe performance on the controlled synthetic
evaluation dataset only. The dataset contains deliberately injected
reconciliation scenarios and is intended to validate deterministic
reconciliation behavior and evaluation correctness.

It should not be used as evidence of production accuracy.

## Reproducibility

The evaluation is deterministic when run with the same seed and record
count. Re-running the pipeline with the same configuration produces the
same ground truth, reconciliation results, and metrics.
"""

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report)
