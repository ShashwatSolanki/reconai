# ReconAI

ReconAI is an AI Finance Controller for automated financial reconciliation and exception management.

It processes payment transactions and settlement records, performs deterministic reconciliation, investigates only unresolved exceptions, applies safety guardrails before any automated action, and maintains an audit trail for agent decisions.

## Problem

Financial reconciliation is not only about finding whether two records match. Real-world reconciliation also produces exceptions such as:

- amount mismatches
- partial settlements
- missing settlements
- duplicate settlements
- reference mismatches

ReconAI separates deterministic financial matching from AI-assisted investigation. The reconciliation engine determines what happened at the record level; the AI is used only to investigate exceptions and explain plausible causes from the available evidence.

## Architecture

```text
Transactions + Settlements
          |
          v
Schema validation
          |
          v
Deterministic reconciliation
          |
          +---- MATCHED
          |
          v
      Exceptions
          |
          v
AI / Mock investigation
          |
          v
Agent safety guardrails
          |
       +--+--+
       |     |
    RESOLVE ESCALATE
       |     |
       +--+--+
          |
          v
     Audit trail
          |
          v
 Evaluation report
```

The LLM is never used for ordinary transaction matching and cannot directly modify financial records.

## How it works

1. Transactions and settlements are represented using typed domain models.
2. Financial amounts are stored as integer minor units to avoid floating-point errors.
3. The reconciliation engine deterministically classifies records as matched, partial, mismatched, missing, duplicate, or unresolved.
4. Only exceptions are sent to the investigation provider.
5. The investigation layer can use either a deterministic mock provider or the OpenAI provider.
6. The agent decision layer applies deterministic safety rules to the investigation result.
7. Only sufficiently confident, non-critical cases that meet the resolution policy can be automatically resolved.
8. All other cases are escalated for human review.
9. Agent actions generate audit events.

This creates a clear boundary between AI reasoning and financial control.

## Verified evaluation

The committed controller evaluation uses:

- **100** synthetic records
- **Seed:** `42`
- **96** matched records
- **4** exceptions
- **4** exceptions investigated
- **1** automatic resolution
- **3** escalations
- **0** exceptions without a final routing outcome

On this controlled synthetic dataset:

| Metric                           | Result |
| -------------------------------- | -----: |
| Status accuracy                  |   100% |
| Exception precision              |   100% |
| Exception recall                 |   100% |
| Average investigation confidence | 62.25% |

The four generated exception types are:

- amount mismatch
- missing settlement
- duplicate settlement
- partial settlement

The full generated evaluation is available in [`reports/evaluation.md`](reports/evaluation.md).

These figures are measured on deterministic synthetic data with known ground truth. They are **not production accuracy, production throughput, or real-world financial recovery claims**.

## Safety boundary

Automatic resolution requires all of the following:

- an `accept_settlement` recommendation
- no human-review requirement
- investigation confidence of at least **90%**
- a non-critical exception

Anything outside that policy is escalated instead of automatically resolved.

The AI investigation layer does not directly mutate financial records. The deterministic decision and action layers enforce the final safety boundary.

## Investigation providers

ReconAI supports two investigation providers:

### Deterministic mock

The default provider is deterministic and requires no external API access. It is used for reproducible tests and benchmark evaluation.

```bash
export INVESTIGATION_PROVIDER=mock
```

### OpenAI

The application can use the OpenAI investigation provider when configured:

```bash
export INVESTIGATION_PROVIDER=openai
export OPENAI_API_KEY=your-key
export OPENAI_MODEL=gpt-4.1-mini
```

The API key is provided through the environment and is not stored in the repository.

## Run locally

Run the controller evaluation:

```bash
python scripts/run_controller_evaluation.py
```

Run the test suite:

```bash
pytest -q
```

Run static checks:

```bash
ruff check .
mypy app
```

Verify the working tree:

```bash
git diff --check
```

## Limitations

The current evaluation is intentionally based on controlled synthetic data with deterministic ground truth.

The reported accuracy metrics therefore demonstrate correctness of the implemented reconciliation and exception-routing workflow on the benchmark dataset; they should not be interpreted as production performance.

The benchmark is also run with the deterministic mock investigation provider so that results remain reproducible and do not depend on external API availability or model variability.

## Project status

ReconAI is implemented as a modular application with:

- typed financial domain models
- deterministic reconciliation
- exception classification
- AI-assisted investigation
- deterministic agent guardrails
- audit events
- batch controller evaluation
- reproducible synthetic test data
- automated tests and static checks

The project is intentionally kept as a focused modular system rather than introducing unnecessary distributed infrastructure.
