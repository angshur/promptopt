# Current Task

## Task

Implement `VariantGeneratorAgent` and `OptimizerAgent` — the two remaining stubbed agents.

## Context

Session 1 is done. Package scaffolded, tests pass. The orchestrator loop is complete and tested with test doubles. `EvaluatorAgent` is fully implemented (calls the LLM on each example via litellm). The only missing pieces to make the full loop work are:

1. `VariantGeneratorAgent.generate()` — currently raises `NotImplementedError`
2. `OptimizerAgent.select()` — currently raises `NotImplementedError`

Once these two are done, running `PromptOptimizer.run()` will execute a real end-to-end optimization loop.

## What to build this session

### 1. `VariantGeneratorAgent` (`promptopt/agents/variant_generator.py`)

Uses meta-prompting: asks an LLM to analyze the current prompt + iteration feedback and generate N improved variants.

**Meta-prompt structure:**
```
You are a prompt engineering expert. Your task is to improve the following prompt.

Current prompt:
{current_prompt}

Performance feedback from last iteration:
- Average score: {avg_score:.2f} / 1.0
- Example failures: {failed_examples}  ← examples where score < 0.5

Generate exactly {num_variants} improved prompt variants. Rules:
1. Preserve ALL placeholders exactly as written: {placeholders}
2. Each variant must be meaningfully different — not just a paraphrase
3. Address the failure patterns shown in the feedback
4. Output ONLY a JSON array of strings: ["variant 1", "variant 2", ...]
```

**Validation after generation:**
- Parse JSON response — if malformed, retry once
- Check all `{placeholder}` names from original prompt are present in each variant
- If a variant is missing a placeholder, drop it and log a warning
- If fewer than `num_variants` valid variants remain, pad with the current prompt (not ideal but safe)

**Feedback extraction from state:**
- If `state.history` is empty (iteration 1), feedback = "No prior data — this is the first iteration."
- Otherwise use last `IterationResult`: avg score + list of example indices where score < 0.5

### 2. `OptimizerAgent` (`promptopt/agents/optimizer.py`)

Simple selection: pick the highest avg_score variant. Signal `should_continue=True` always (convergence is handled by the orchestrator's plateau detection, not here).

```python
def select(self, variants, state):
    best = max(variants, key=lambda v: v.avg_score)
    return best, True
```

That's the full implementation — it's 3 lines. The orchestrator handles plateau detection.

## Definition of done

- [ ] `VariantGeneratorAgent.generate()` returns a list of strings (real LLM output, not NotImplementedError)
- [ ] All `{placeholders}` from the original prompt are preserved in every variant
- [ ] `OptimizerAgent.select()` returns `(best_ScoredVariant, True)`
- [ ] End-to-end smoke test: run 3 iterations of `PromptOptimizer` on a trivial prompt with `exact_match` metric — no crash, `result.history` has 3 entries
- [ ] `pytest tests/` still passes (no regressions)
- [ ] Two golden tests in `evals/` unxfailed: `test_golden_variant_generator_preserves_placeholders` and `test_golden_orchestrator_early_stopping`

## When done

- Update progress.md
- Rewrite this file: next task is `llm_judge` evaluator (session 3)
- Write to decisions.md: meta-prompt structure choices (JSON output format, retry logic, padding strategy)
