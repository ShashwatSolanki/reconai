# ReconAI - Finance Controller Evaluation

## Dataset

- Records: `100`
- Seed: `42`
- Data: controlled synthetic records with known ground truth

## Reconciliation

| Metric | Result |
|---|---:|
| Matched | 96 |
| Exceptions | 4 |
| Match rate | 96.00% |

## Exception Handling

| Metric | Result |
|---|---:|
| Investigated | 4 |
| Automatically resolved | 1 |
| Escalated to human review | 3 |
| Without a final outcome | 0 |
| Average investigation confidence | 62.25% |

## Verified Evaluation

| Metric | Result |
|---|---:|
| Status accuracy | 100.00% |
| Exception precision | 100.00% |
| Exception recall | 100.00% |

## Performance

| Metric | Result |
|---|---:|
| Processing time | 0.0021 seconds |
| Throughput | 48213.68 records/second |

## Exception Breakdown

| Category | Count |
|---|---:|
| Amount Mismatch | 1 |
| Missing Settlement | 1 |
| Duplicate Settlement | 1 |
| Partial Settlement | 1 |

## Exceptions Requiring Human Review

| Exception ID | Category | Difference (paise) | Reason | Action |
|---|---|---:|---|---|
| exc_pay_0003 | amount_mismatch | 2000 | Human review is required before execution. | ESCALATED |
| exc_pay_0004 | missing_settlement | N/A | Human review is required before execution. | ESCALATED |
| exc_pay_0005 | duplicate_settlement | N/A | Human review is required before execution. | ESCALATED |

## Limitations

This evaluation uses controlled synthetic data and deterministic ground truth.
It demonstrates pipeline correctness and measured local benchmark behavior, not
production accuracy or production throughput. Escalated exceptions have a final
safe routing outcome, but remain pending human review.
