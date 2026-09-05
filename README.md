# ReconAI

ReconAI is an AI Finance Controller for reconciliation. It processes 100 synthetic transactions, matches settlements, investigates only exceptions, safely resolves high-confidence cases, and audits every agent action.

## Architecture

```text
Transactions -> deterministic reconciliation -> exceptions -> AI/mock investigation
             -> agent guardrails -> resolve or escalate -> audit + report
```

The LLM is never used for ordinary matching and cannot modify financial records.

## Verified evaluation

The committed controller run (`seed=42`) measured 100 records, 96 matches, 4 exceptions, 1 safe automatic resolution, and 3 escalations. Status accuracy, exception precision, and exception recall were each 100% on controlled synthetic data. See [the generated report](reports/evaluation.md).

## Run locally

```bash
python scripts/run_controller_evaluation.py
pytest -q
ruff check .
mypy app
```

Use `INVESTIGATION_PROVIDER=mock` for deterministic runs. To use OpenAI, set `INVESTIGATION_PROVIDER=openai`, `OPENAI_API_KEY`, and optionally `OPENAI_MODEL`.

## Safety and limitations

Automatic resolution requires an accept-settlement recommendation, no human-review flag, and at least 90% confidence. All other cases are escalated and audited. This is a synthetic benchmark, not a production accuracy or throughput claim.
