# AI Investigation

The provider receives verified reconciliation facts and returns structured root cause, evidence, recommendation, confidence, and a human-review flag. Tests use the deterministic mock provider; OpenAI is optional for demos.

AI cannot alter transactions or settlements. The deterministic guardrail layer resolves only an accept-settlement recommendation at 90% or higher confidence with no human-review requirement. Every other result escalates.
