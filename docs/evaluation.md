# Evaluation

## Purpose

ReconAI evaluates reconciliation performance by comparing predicted reconciliation outcomes against known ground-truth outcomes from a controlled synthetic dataset.

The evaluation layer is separate from the reconciliation engine so that reconciliation produces results while evaluation measures how accurately those results reflect the expected outcomes.

---

## Ground Truth

Evaluation ground truth is represented by the `GroundTruth` domain model.

Each transaction has:

- `transaction_id`
- `expected_status`
- `has_exception`

### Supported Expected Statuses

- `matched`
- `partial_match`
- `mismatch`
- `missing_settlement`
- `duplicate`

A `matched` transaction is expected to have no exception. Every other supported status represents an exception.

The current synthetic evaluation ground truth is generated from the known transaction and settlement relationships in the controlled synthetic dataset.

> **Evaluation Limitation:** Because the current ground-truth generator derives expected outcomes from synthetic transaction/settlement relationships, it is suitable for controlled evaluation of the current reconciliation scenarios but should not be presented as independently labeled production data.

---

## Metrics

### Status Accuracy

Status accuracy measures the proportion of transactions for which the predicted reconciliation status exactly matches the expected status.

```text
status_accuracy = correct_status_predictions / total_transactions
```

A prediction is correct only when the predicted status and ground-truth status are identical.

### Exception Precision

Exception precision measures how many predicted exceptions are actually exceptions.

```text
exception_precision = true_positive_exceptions / predicted_exceptions
```

A predicted exception is any reconciliation result whose status is not `matched`.

### Exception Recall

Exception recall measures how many actual exceptions are detected by reconciliation.

```text
exception_recall = true_positive_exceptions / actual_exceptions
```

An actual exception is any ground-truth record whose `has_exception` value is `true`.

### Zero-Denominator Handling

The evaluation implementation returns `0.0` when a metric has no denominator.

This applies to:

- **Status Accuracy:** When the evaluation dataset is empty
- **Exception Precision:** When no exceptions are predicted
- **Exception Recall:** When no actual exceptions exist

This keeps evaluation deterministic and avoids undefined numerical results.

---

## Dataset Alignment

- Ground-truth records and reconciliation results must contain the same number of transactions.
- The evaluation service rejects mismatched dataset lengths instead of silently comparing incomplete or misaligned datasets.
- The current implementation preserves transaction identity in both inputs, but the evaluation contract currently validates dataset length rather than independently matching records by `transaction_id`.

---

## Evaluation Implementation

The `EvaluationMetrics` service compares:

```text
GroundTruth[] + ReconciliationResult[]
                │
                ▼
        EvaluationMetrics
                │
                ▼
      EvaluationMetricsResult
```

### `EvaluationMetricsResult` Fields

- Total transaction count
- Correct status predictions
- Status accuracy
- Actual exception count
- Predicted exception count
- True-positive exception count
- Exception precision
- Exception recall

---

## Current Test Coverage

The evaluation metrics unit/integration tests cover:

- Status accuracy calculation
- Exception precision calculation
- Exception recall calculation
- Datasets containing no exceptions
- Empty datasets
- Rejection of mismatched dataset lengths

> All evaluation tests are deterministic and use controlled domain objects rather than external services.

---

## Future Evaluation Extensions

The evaluation layer can be extended with:

- Per-status precision and recall
- Confusion matrices
- False-positive cost analysis
- Exception-category accuracy
- Investigation recommendation accuracy
- Agent resolution accuracy
- Throughput measurements
- Held-out synthetic test datasets
- Before/after operational metrics

_These metrics should be added only when the underlying data and evaluation methodology support them._
