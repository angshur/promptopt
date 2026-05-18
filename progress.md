# progress.md

## Done

- [x] Scaffold package structure: `promptopt/`, `agents/`, `evaluators/`, `tests/`, `evals/`
- [x] `OptimizationState`, `OptimizationResult`, `Example`, `ScoredVariant`, `IterationResult` dataclasses (fully typed)
- [x] SQLite schema: `runs`, `iterations`, `variants` tables — `storage.py` with `init_db()` and `save_run()`
- [x] `exact_match` evaluator — fully implemented
- [x] `EvaluatorAgent.evaluate()` — fully implemented (renders prompt, calls LLM via litellm, scores, clamps, handles exceptions)
- [x] `OrchestratorAgent` — full loop with plateau detection, early stop, best-across-all-iterations tracking
- [x] `VariantGeneratorAgent`, `OptimizerAgent`, `llm_judge` — stubbed with correct interfaces
- [x] `PromptOptimizer` user-facing class with target API from spec.md
- [x] CLI: `promptopt run --config config.yaml` skeleton
- [x] 14 tests passing, 5 xfail (pending agent implementations)
- [x] `pip install -e .[dev]` works with Python 3.11

## Next (ordered)

1. **Implement VariantGeneratorAgent** — meta-prompting via litellm: takes current prompt + iteration history → generates N improved variants. Validate placeholder preservation. (session 2)
2. **Implement OptimizerAgent** — select highest avg score; return continue=False if delta < threshold (session 3 — can fold into session 2 if time allows, it's short)
3. **Implement llm_judge evaluator** — litellm call with structured output (score float + rationale string). Clamp to [0,1]. Use Haiku as default judge model. (session 3)
4. **End-to-end test** — run full optimization loop on a real summarization prompt with 5 examples. Confirm scores improve across iterations.
5. **Unxfail golden tests** — make evals/test_golden.py pass for VariantGenerator and llm_judge cases.
6. **CLI completion** — test `promptopt run --config config.yaml` end-to-end with a real YAML example.
7. **Package for PyPI** — README, classifiers, check PyPI name availability.
8. **Publish** — PyPI + GitHub repo.

## Blocked

(nothing blocked)

## Session log

| Date | What happened |
|---|---|
| 2026-05-17 | Project initialized. All coordination files written. |
| 2026-05-17 | Session 1 complete. Full package scaffold built. 14 tests pass, 5 xfail pending agent implementations. |
