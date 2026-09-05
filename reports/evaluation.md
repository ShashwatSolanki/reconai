# ReconAI Evaluation Report

## Methodology

This report contains measured results from ReconAI's deterministic
evaluation pipeline.

- Dataset: **Controlled synthetic dataset**
- Seed: `42`
- Record count: `100`

The evaluation ground truth is generated from known transaction and
settlement relationships in the controlled synthetic dataset. These
results must not be interpreted as independently labeled production
performance.

## Dataset

| Metric | Value |
|---|---:|
| Transactions | 100 |
| Settlements | 100 |

## Reconciliation Outcomes

| Status | Count |
|---|---:|
| Matched | 96 |
| Partial match | 1 |
| Mismatch | 1 |
| Missing settlement | 1 |
| Duplicate | 1 |

## Evaluation Metrics

| Metric | Result |
|---|---:|
| Status accuracy | 100.00% |
| Exception precision | 100.00% |
| Exception recall | 100.00% |

### Metric Counts

- Correct status predictions: `100`
- Actual exceptions: `4`
- Predicted exceptions: `4`
- True-positive exceptions: `4`

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
