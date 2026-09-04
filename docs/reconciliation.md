# Reconciliation Engine

## Purpose

The Reconciliation Engine is the deterministic core of ReconAI. Its responsibility is to compare payment transactions against settlement records and produce a structured `ReconciliationResult`.

The engine does not perform:

- Database access
- HTTP handling
- LLM calls
- AI reasoning
- Automatic financial actions

These concerns belong to higher application layers.

---

## Inputs

The engine receives:

- One `Transaction` object
- Zero or more candidate `Settlement` objects
  Transactions and settlements are peer inputs to the reconciliation process.

```
Transaction ───────┐
                   ├──→ ReconciliationEngine ──→ ReconciliationResult
Settlement ────────┘
```

---

## Matching Identity

A settlement is associated with a transaction using the transaction identifier:

```
Settlement.transaction_reference == Transaction.transaction_id
```

The initial implementation intentionally uses explicit identifiers rather than fuzzy matching.

---

## Deterministic Rules

Rules are evaluated in the following order:

### 1. Missing Settlement

If no settlement references the transaction:

```
Transaction exists
Settlement does not exist
        ↓
MISSING_SETTLEMENT
```

The reconciliation status is `MISSING_SETTLEMENT`.

### 2. Duplicate Settlement

If more than one settlement references the same transaction:

```
Transaction
    ↓
Settlement A
Settlement B
    ↓
DUPLICATE
```

The reconciliation status is `DUPLICATE`. The engine must not arbitrarily select one settlement.

### 3. Reference Filtering

Only settlements whose `transaction_reference` matches the transaction being reconciled are considered candidates.

A settlement referencing a different transaction is therefore not considered a match for the current transaction. If no valid candidate remains, the result is `MISSING_SETTLEMENT`.

Settlement.transaction_reference != Transaction.transaction_id
↓
Not considered a candidate
↓
MISSING_SETTLEMENT

The initial implementation intentionally does not expose a separate `REFERENCE_MISMATCH` reconciliation status.

### 4. Exact Match

If the settlement amount equals the transaction amount:

```
transaction.amount == settlement.amount
        ↓
MATCHED
```

The reconciliation status is `MATCHED`. No monetary discrepancy exists.

### 5. Partial Settlement

If the settlement amount is lower than the transaction amount:

```
settlement.amount < transaction.amount
        ↓
PARTIAL_MATCH
```

The reconciliation status is `PARTIAL_MATCH`. The difference represents the unsettled amount:

```
difference = transaction.amount - settlement.amount
```

### 6. Amount Mismatch

If the settlement amount differs from the transaction amount and does not represent a partial settlement:

```
settlement.amount != transaction.amount
        ↓
MISMATCH
```

The reconciliation status is `MISMATCH`. The difference represents the absolute monetary discrepancy:

```
difference = |transaction.amount - settlement.amount|
```

---

## Result Contract

Every reconciliation produces a `ReconciliationResult`.

| Field             | Description                                    |
| :---------------- | :--------------------------------------------- |
| `transaction_id`  | Identifier of the transaction being reconciled |
| `settlement_id`   | Identifier of the settlement, when available   |
| `status`          | Reconciliation status                          |
| `expected_amount` | Expected transaction amount                    |
| `actual_amount`   | Actual settlement amount, when available       |
| `difference`      | Monetary difference, when applicable           |
| `reason`          | Human-readable deterministic explanation       |

Amounts are represented in integer minor units (paise for INR), never floating-point values.

### Example

```json
{
  "transaction_id": "txn_123",
  "settlement_id": "set_456",
  "status": "PARTIAL_MATCH",
  "expected_amount": 100000,
  "actual_amount": 75000,
  "difference": 25000,
  "reason": "Settlement amount is lower than the transaction amount."
}
```

---

## Determinism

Given the same transaction and settlement inputs, the engine must always produce the same reconciliation result.

The engine must not use:

- Randomness
- LLM calls
- External APIs
- Model inference
- Non-deterministic matching logic

Financial comparisons must remain deterministic and reproducible.

---

## AI Boundary

The Reconciliation Engine establishes the deterministic financial baseline. AI investigation operates after reconciliation and may later:

- Investigate the cause of an exception
- Classify ambiguous discrepancies
- Recommend a resolution
- Provide confidence and reasoning

AI must not replace deterministic financial comparisons.

```
Transactions + Settlements
            │
            ▼
┌───────────────────────────┐
│  Reconciliation Engine    │
│  Deterministic Rules      │
└─────────────┬─────────────┘
              │
              ▼
   ReconciliationResult
              │
              ▼
┌───────────────────────────┐
│       AI Investigation    │
│                           │
│ Cause / Classification /  │
│ Recommendation / Reasoning│
└───────────────────────────┘
```

---

## Error Handling

The engine must fail explicitly for invalid domain inputs rather than silently producing an incorrect financial result.

Examples of invalid inputs may include:

- Missing required transaction identifiers
- Missing required settlement identifiers
- Invalid monetary values
- Invalid transaction references
- Other domain-level validation failures

Validation errors should be distinguishable from reconciliation outcomes.

---

## Testing Strategy

The first implementation will use unit tests covering the following scenarios:

- Exact match
- Amount mismatch
- Partial settlement
- Missing settlement
- Duplicate settlement
- Reference filtering resulting in a missing settlement

### Example Test Matrix

| Scenario                                                  | Expected Status      |
| :-------------------------------------------------------- | :------------------- |
| Transaction amount equals settlement amount               | `MATCHED`            |
| Settlement amount is lower than transaction amount        | `PARTIAL_MATCH`      |
| Settlement amount differs and is not a partial settlement | `MISMATCH`           |
| No settlement references the transaction                  | `MISSING_SETTLEMENT` |
| Multiple settlements reference the same transaction       | `DUPLICATE`          |
| Settlement references a different transaction             | `MISSING_SETTLEMENT` |

---

## Summary

The Reconciliation Engine is responsible only for deterministic transaction-to-settlement reconciliation. Its core responsibilities are:

- Identify settlements using explicit transaction references.
- Detect missing and duplicate settlements.
- Validate settlement references.
- Compare transaction and settlement amounts.
- Produce a deterministic `ReconciliationResult`.
- Fail explicitly when domain inputs are invalid.

AI capabilities are intentionally kept outside the core reconciliation engine so that financial comparisons remain predictable, auditable, and reproducible.
