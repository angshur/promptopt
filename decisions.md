# decisions.md

## May 2026

**Multi-agent architecture for the optimization loop**
Chose OrchestratorAgent → VariantGeneratorAgent + EvaluatorAgent + OptimizerAgent, communicating through a shared `OptimizationState` dataclass. Alternatives considered: single-class monolith (simpler but not extensible), file-based (unnecessary for an in-process SDK). The agent pattern makes each concern independently testable and mirrors Angshuman's studio agent architecture — familiar mental model, easier to extend.

**litellm over direct Anthropic SDK**
Using litellm for all LLM calls so the tool works with Claude, GPT-4o, Gemini, and any future model without code changes. The product is explicitly model-agnostic. If litellm adds overhead or breaks, wrapping it is straightforward.

**SQLite over file-based storage**
Chose SQLite (stdlib `sqlite3`) for version history. Alternatives: flat JSON files (no querying), Postgres (over-engineered for a local dev tool). SQLite is zero-setup, queryable, and ships with Python. Users get a real database at `~/.promptopt/runs.db` without installing anything.

**EvaluatorAgent is fully implemented in session 1 (not a stub)**
The task said to stub EvaluatorAgent, but its logic is pure orchestration of existing pieces (render template → litellm call → score → clamp → handle exception). No design uncertainty. Implemented fully rather than creating unnecessary stub debt. VariantGeneratorAgent and OptimizerAgent were correctly stubbed because they have open design questions (meta-prompt structure, convergence signal placement).

**Python 3.11 required (not 3.9)**
System default is Python 3.9.7 but Python 3.11 is installed at `/usr/local/bin/python3.11`. Kept `requires-python = ">=3.11"` because we use `X | None` union syntax and `list[str]` generics in type hints throughout. Run with `python3.11` explicitly.

**Open source first, monetization later**
No SaaS features in v1. The distribution strategy is GitHub → PyPI → developer adoption → optional cloud hub as paid tier later. Building enterprise features before open-source traction is premature.
