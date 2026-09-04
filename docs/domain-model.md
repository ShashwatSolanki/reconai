# ReconAI Domain Model

## Purpose

The domain layer defines the core financial concepts used by ReconAI without
depending on databases, HTTP frameworks, LLM providers, or UI concerns.

The domain model is intentionally framework-independent so that business rules
can be tested independently and reused by different application layers.

## Current Domain Flow

## Current Domain Flow

````text
Transaction ───────┐
                   ├──→ Reconciliation Engine ──→ ReconciliationResult
Settlement ────────┘
                                      │
                                      ▼
                              FinancialException
                                      │
                                      ▼
                              Resolution / Escalation
                                      │
                                      ▼
                                  AuditEvent

The reconciliation engine receives Transaction and Settlement as peer inputs. It produces a deterministic ReconciliationResult. When that result represents a discrepancy requiring further action, it can become a FinancialException.

The reconciliation engine itself will operate on domain objects and produce a reconciliation result. It will not perform persistence, HTTP handling, or AI reasoning.```

Domain Objects
Money

Money represents monetary values using integer minor units.

For INR:

₹1 = 100 paise
₹980 = 98000 paise

The system does not use floating-point values for financial amounts.

Properties:

immutable
currency-aware
non-negative
supports addition
supports subtraction with validation

Implementation:

app/domain/money.py
Transaction

Transaction represents a payment transaction entering the reconciliation
system.

Current attributes:

transaction_id
merchant_id
amount
transaction_time
payment_method
reference_id
status

Supported payment methods:

card
UPI
netbanking
wallet

Supported transaction statuses:

success
failed
refunded
partially refunded

Implementation:

app/domain/transaction.py
Settlement

Settlement represents a settlement record received from the settlement
system or banking source.

Current attributes:

settlement_id
merchant_id
amount
settlement_time
reference_id
transaction_reference
status

Supported settlement statuses:

settled
partially settled
failed
reversed

Implementation:

app/domain/settlement.py
ReconciliationResult

ReconciliationResult represents the deterministic outcome of comparing a
transaction against settlement data.

It does not perform reconciliation itself.

Current attributes:

transaction_id
settlement_id
status
expected_amount
actual_amount
difference
reason

Supported reconciliation statuses:

MATCHED
PARTIAL_MATCH
MISMATCH
MISSING_TRANSACTION
DUPLICATE
UNRESOLVED

Implementation:

app/domain/reconciliation.py
Design Principles

1. Deterministic financial logic stays deterministic

Exact matching, amount comparisons, duplicate detection, and reference
validation should be implemented using deterministic code.

The LLM is not the source of truth for whether two financial records match.

2. AI is used where reasoning adds value

AI will later investigate exceptions that require interpretation, such as:

settlement fees
partial settlement
timing differences
unexpected reference mappings
ambiguous discrepancies

The AI should produce structured reasoning and recommendations rather than
directly controlling unrestricted financial operations.

3. Domain objects are immutable

Current domain entities use immutable dataclasses.

This reduces accidental mutation while records are being passed through the
reconciliation pipeline.

4. Domain layer remains infrastructure-independent

The domain layer should not directly depend on:

PostgreSQL
SQLAlchemy
FastAPI
OpenAI
React
external APIs

Those concerns belong to higher-level application layers.

Current Relationship
Money
|
+--------------------+
| |
v v
Transaction Settlement
| |
+---------+----------+
|
v
ReconciliationResult

## FinancialException

`FinancialException` represents a discrepancy identified during financial
reconciliation.

It is intentionally separate from `ReconciliationResult`:

- `ReconciliationResult` describes the deterministic reconciliation outcome.
- `FinancialException` represents an actionable discrepancy requiring
  investigation, resolution, or escalation.

### Exception Categories

The current exception categories are:

| Category               | Meaning                                             |
| ---------------------- | --------------------------------------------------- |
| `AMOUNT_MISMATCH`      | Transaction and settlement amounts differ           |
| `MISSING_SETTLEMENT`   | No settlement record was found                      |
| `DUPLICATE_SETTLEMENT` | Multiple settlements reference the same transaction |
| `PARTIAL_SETTLEMENT`   | Only part of the expected amount was settled        |
| `REFERENCE_MISMATCH`   | Financial records have inconsistent references      |
| `UNKNOWN`              | The discrepancy cannot yet be classified            |

### Exception Severity

Exceptions are assigned a severity:

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

Severity is part of the exception domain model and can later be used by
the agent workflow to determine whether an exception can be automatically
resolved or must be escalated.

### AI Boundary

The exception domain model does not perform AI reasoning.

The deterministic reconciliation layer identifies and structures the
exception. AI investigation will be introduced in a separate application
service/agent layer where it can analyze the discrepancy, determine a
likely root cause, and recommend an action.

This keeps financial state and deterministic rules independent from the
LLM provider.

Future Domain Extensions

The following domain objects are planned:

Exception
Resolution
AuditEvent

These will be introduced only when their behavior and invariants are clearly
defined and tested.

Testing Strategy

Each domain object follows a test-driven development cycle:

Write failing test
↓
Implement minimum behavior
↓
Run focused tests
↓
Run complete test suite
↓
Run Ruff
↓
Run Mypy
↓
Review diff
↓
Commit
↓
Push

Current domain test coverage:

Money: implemented
Transaction: implemented
Settlement: implemented
ReconciliationResult: implemented
Exception: pending
Resolution: pending
AuditEvent: pending
````
