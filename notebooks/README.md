# Notebooks — Eval, Security, and Agents

This directory contains working notebooks from Days 85–95 of the 120-day ML Engineer journey.

## Structure

- `day85_redteam.ipynb` — Basic security red teaming
- `day86_advanced_redteam.ipynb` — Advanced attacks (Base64, extraction, toxicity, context swamping)
- `day87_judge_baseline.ipynb` — LLM-as-a-Judge foundation
- `day88_batch_eval.ipynb` — Batch evaluation across 20-case golden set
- `day91_socratic_agent.ipynb` — Single-tool agent (Socratic tutoring)
- `day92_multitool_agent.ipynb` — Multi-tool agent with intent routing
- `day93_stateful_agent.ipynb` — Stateful agent with persistent memory
- `day94_resilient_agent.ipynb` — Production resilience (retries, graceful degradation)
- `day95_observability.ipynb` — Agent observability and tracing

## Artifacts (`artifacts/`)

JSON files with measured results from each notebook. See individual notebooks for the code that generated them.

## Security Note

All notebooks use environment variables loaded from **Colab Secrets** for API keys. No secrets are hardcoded. All artifacts are outputs only — no credentials.

## What These Demonstrate

- **Security:** 7 adversarial attack vectors tested, all defended
- **Quality:** LLM-as-a-Judge evaluated across 20 cases (4.65/5 helpfulness, 0 weak cases)
- **CI/CD:** Judge integrated into gate; deliberately verified to block regressions
- **Agents:** Single-tool → multi-tool → stateful → resilient → observable
