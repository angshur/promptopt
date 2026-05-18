# promptopt

Automated prompt optimization for LLM applications. Give it a prompt, examples, and a scoring function — a multi-agent system iteratively generates improved variants and converges on the best version.

```python
from promptopt import PromptOptimizer, llm_judge

optimizer = PromptOptimizer(
    prompt="Summarize this article in 2 sentences: {text}",
    examples=[
        {"inputs": {"text": "..."}, "ideal": "Short, accurate summary."},
    ],
    metric=llm_judge(criteria="concise, accurate, under 30 words"),
    model="claude-sonnet-4-6",
    iterations=10,
)
result = optimizer.run()
print(result.best_prompt)
```

## Why promptopt

- **No restructuring** — drop-in for any existing prompt, unlike DSPy
- **Model-agnostic** — works with Claude, GPT-4o, Gemini, or any litellm-compatible model
- **Version history** — every run and variant saved locally to SQLite
- **Lightweight** — two runtime dependencies (`litellm`, `click`), no infrastructure required

## Install

```bash
pip install promptopt
```

Requires Python 3.11+.

## Usage

### Python SDK

```python
from promptopt import PromptOptimizer, exact_match, llm_judge

# Exact match scoring (deterministic)
optimizer = PromptOptimizer(
    prompt="Classify the sentiment of: {text}",
    examples=[
        {"inputs": {"text": "Great product!"}, "ideal": "positive"},
        {"inputs": {"text": "Terrible experience."}, "ideal": "negative"},
    ],
    metric=exact_match,
    model="gpt-4o",
    iterations=10,
    num_variants=3,
)
result = optimizer.run()

print(result.best_prompt)   # optimized prompt string
print(result.score)         # best average score (0.0–1.0)
print(result.run_id)        # UUID for this run (stored in SQLite)
```

### CLI

```bash
promptopt run --config config.json
promptopt run --config config.yaml --verbose
```

**config.json**
```json
{
  "prompt": "Summarize this article: {text}",
  "examples": [
    {"inputs": {"text": "..."}, "ideal": "Short summary."}
  ],
  "metric": "llm_judge:concise and accurate",
  "model": "claude-sonnet-4-6",
  "iterations": 10,
  "num_variants": 3
}
```

Metric values: `"exact_match"`, `"llm_judge:<criteria>"`, or `{"type": "llm_judge", "criteria": "..."}`.

## How it works

```
PromptOptimizer.run()
  └── OrchestratorAgent
        ├── VariantGeneratorAgent  — generates N prompt variants via LLM
        ├── EvaluatorAgent         — scores each variant against examples
        └── OptimizerAgent         — selects best variant, checks convergence
```

Agents communicate through a shared `OptimizationState` object — no direct calls between agents. The loop runs until `max_iterations` or score improvement falls below `convergence_threshold` (default `0.01`).

## Metrics

| Metric | Description |
|---|---|
| `exact_match` | `1.0` if output equals ideal, `0.0` otherwise |
| `llm_judge(criteria=...)` | LLM scores output against criteria, returns `0.0–1.0` |

You can also pass any `Callable[[str, str], float]` as `metric`.

## `PromptOptimizer` parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `prompt` | `str` | — | Starting prompt (use `{variable}` placeholders) |
| `examples` | `list[dict]` | — | List of `{"inputs": {...}, "ideal": "..."}` |
| `metric` | `Callable` | — | Scoring function `(output, ideal) -> float` |
| `model` | `str` | `"claude-sonnet-4-6"` | Any litellm-compatible model string |
| `iterations` | `int` | `10` | Max optimization iterations |
| `num_variants` | `int` | `3` | Variants generated per iteration |
| `convergence_threshold` | `float` | `0.01` | Stop early if score delta falls below this |

## Development

```bash
git clone https://github.com/angshur/promptopt
cd promptopt
pip install -e ".[dev]"
pytest
```

## License

MIT
