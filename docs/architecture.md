# Architecture

```text
API / batch runner -> reconciliation engine -> exception registration
                 -> investigation provider -> decision guardrails
                 -> resolve or escalate -> audit event / controller report
```

`ReconAIService` depends on `InvestigationProvider`, not a vendor-specific class. The container selects deterministic mock investigation by default and selects OpenAI only when explicitly configured. Matched records do not enter the AI layer.
