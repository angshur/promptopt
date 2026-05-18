# promptopt — Spec
*What we are building. Acceptance criteria. Scope boundaries.*

---

## What we are building

A Python SDK and CLI that runs an automated prompt optimization loop using a multi-agent architecture. The user provides: an initial prompt (with `{variable}` placeholders), a list of examples (each a dict of variables + expected output), and a metric function (takes actual output + expected output, returns a float 0–1). The system iterates — generating prompt variants via meta-prompting, scoring each variant against all examples, and tracking version history — until it converges or hits a max iteration limit.

The internal architecture mirrors the agent-architecture.md pattern: agents never talk directly — they communicate through structured state objects passed by the orchestrator.

---

## Who it's for

A solo AI engineer at a startup who has already shipped a product and wants to improve a specific prompt that's underperforming. They run `pip install promptopt`, write 10 lines of Python, and get a better prompt with a score history. No account required, no cloud dependency, runs fully local.

---

## Multi-agent architecture (the product's internal design)

```
OrchestratorAgent
    │
    ├── reads: current prompt, examples, iteration history
    ├── decides: continue / stop / adjust strategy
    │
    ├─→ VariantGeneratorAgent
    │       input: current prompt + iteration feedback
    │       output: N candidate prompt variants (default: 3)
    │       method: meta-prompting (LLM rewrites the prompt)
    │
    ├─→ EvaluatorAgent (runs per variant)
    │       input: variant + examples
    │       output: scored results (one score per example, avg score)
    │       methods: exact_match | llm_judge | custom_fn
    │
    └─→ OptimizerAgent
            input: all scored variants from this iteration
            output: best variant + decision (continue / stop)
            method: select highest avg score; stop if delta < threshold
```

Agents pass state through a shared `OptimizationState` dataclass — not files (this is SDK-internal, not the studio file-based system). No agent calls another agent directly; all routing goes through the orchestrator.

---

## Acceptance criteria

- [ ] `pip install promptopt` works from PyPI (or local editable install for v1)
- [ ] User can run optimization in < 15 lines of Python (see usage example below)
- [ ] Optimization loop runs at least 5 iterations by default; configurable up to 20
- [ ] Each iteration generates 3 prompt variants (configurable 1–5)
- [ ] Three built-in evaluators: `exact_match`, `llm_judge`, `custom` (bring your own fn)
- [ ] `result.best_prompt` returns the highest-scoring prompt found
- [ ] `result.history` returns all iterations: prompt variant, per-example scores, avg score
- [ ] All results persisted to SQLite at `~/.promptopt/runs.db` (no setup required)
- [ ] CLI: `promptopt run --config config.yaml` works end-to-end
- [ ] Works with any litellm-compatible model (tested: Claude, GPT-4o)
- [ ] Cold start to first optimization result in < 5 minutes for a new user
- [ ] Failing example: if metric function raises an exception, evaluator catches it, logs it, marks that example as score=0, continues — does not crash the run

---

## Target usage (what the API must look like)

```python
from promptopt import PromptOptimizer, llm_judge

optimizer = PromptOptimizer(
    prompt="Summarize this article in 2 sentences: {text}",
    examples=[
        {"inputs": {"text": "..."}, "ideal": "Short, accurate summary."},
        {"inputs": {"text": "..."}, "ideal": "Another good summary."},
    ],
    metric=llm_judge(criteria="concise, accurate, under 30 words"),
    model="claude-sonnet-4-6",
    iterations=10,
)

result = optimizer.run()
print(result.best_prompt)
print(result.score)      # best avg score
print(result.history)    # all iterations
```

---

## What is out of scope (v1)

1. No web UI or dashboard — SDK and CLI only
2. No team features — no auth, no sharing, no multi-user
3. No streaming optimization — runs synchronously, returns when done
4. No fine-tuning — prompt optimization only, no model weight updates
5. No cloud sync — SQLite is local only; no hub, no remote storage
6. No parallel variant evaluation — variants scored sequentially (parallelism in v2)

---

## Open questions

- [ ] Should `llm_judge` use the same model as the optimizer, or allow a separate cheaper judge model? (e.g., use Haiku for eval, Opus for optimization)
- [ ] Should the CLI support a `--watch` mode that re-runs on file change?
- [ ] Should we support few-shot example injection as a separate optimization strategy alongside meta-prompting?
- [ ] Package name: `promptopt` on PyPI — check availability before publishing
