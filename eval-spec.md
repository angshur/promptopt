# promptopt — Eval Spec
*What good looks like for every AI feature. Golden cases. Hard guardrails.*

---

## Feature 1: VariantGeneratorAgent (meta-prompting)

### What good looks like
- Generated variants are meaningfully different from the input prompt — not just paraphrases
- Each variant addresses the specific failure modes identified in previous iteration's eval feedback
- Variants preserve all `{variable}` placeholders from the original prompt — no placeholders dropped or renamed
- Variants are syntactically valid as prompt strings (no broken formatting)
- N variants generated = exactly what was requested (default 3)

### What bad looks like
- Variant is identical or near-identical to the input prompt
- Variant drops a `{variable}` placeholder the user defined
- Variant introduces hallucinated constraints not present in the task
- Variant is in a different language than the original prompt
- Generator returns fewer variants than requested without explanation

### Hard guardrails
- NEVER silently drop or rename a `{variable}` placeholder — raise a validation error instead
- NEVER generate variants that introduce safety-relevant instructions (e.g., "ignore previous instructions") — detect and reject
- If generation fails (API error, timeout), log the error and retry once; if retry fails, skip this iteration and continue

### Golden test cases
- [ ] **Case 1 (summarization):** Input: `"Summarize: {text}"` + 5 failed examples (outputs too long) → variant should explicitly instruct brevity (e.g., "in one sentence", "under 20 words")
- [ ] **Case 2 (placeholder preservation):** Input prompt with `{user_name}` and `{context}` → all 3 variants must contain both placeholders verbatim
- [ ] **Case 3 (iteration 1 vs iteration 5):** By iteration 5, variants should show measurable score improvement over iteration 1 baseline on the same example set (delta > 0.05)

---

## Feature 2: EvaluatorAgent — `llm_judge`

### What good looks like
- Score is a float between 0.0 and 1.0 (inclusive)
- Score reflects the provided criteria — a response meeting all criteria scores > 0.7
- Consistent: same input + output produces the same score ± 0.05 across 3 runs (LLMs are stochastic, allow small variance)
- Judge explains its score in structured output (score + one-line rationale)

### What bad looks like
- Score outside [0.0, 1.0] range
- Judge scores a clearly wrong answer > 0.5
- Judge ignores the provided criteria and evaluates on unrelated dimensions
- Judge returns a non-numeric score (e.g., "good", "7/10")

### Hard guardrails
- ALWAYS clamp returned score to [0.0, 1.0] — never pass an out-of-range value up the chain
- If judge model returns unparseable output, score = 0.0 and log a warning — do not crash
- Judge must receive ONLY the output and criteria — never the prompt template or internal system state

### Golden test cases
- [ ] **Case 1 (clear pass):** Output = exact copy of ideal, criteria = "matches ideal output" → score ≥ 0.9
- [ ] **Case 2 (clear fail):** Output = empty string, any criteria → score ≤ 0.1
- [ ] **Case 3 (criteria specificity):** Output = 50-word summary, criteria = "under 20 words" → score ≤ 0.4; same output with criteria = "factually accurate" → score ≥ 0.6

---

## Feature 3: OrchestratorAgent (convergence logic)

### What good looks like
- Stops early if score delta between iterations < 0.01 for 3 consecutive iterations (converged)
- Stops at max_iterations regardless of score trajectory
- Correctly identifies best variant across all iterations (not just last iteration)
- Reports full history in order (iteration 1 → N)

### What bad looks like
- Runs all iterations even when score has plateaued for 5 iterations
- Reports best prompt from wrong iteration (e.g., second-best)
- History is out of order or missing iterations

### Hard guardrails
- ALWAYS complete at least 2 iterations before triggering early stopping
- NEVER mutate the user's original prompt object — work on copies only
- If all variants in an iteration score 0.0 (eval failure), log a warning and stop — do not continue on bad signal

### Golden test cases
- [ ] **Case 1 (early stopping):** Scores plateau at 0.95 for 3 iterations → run stops before max_iterations
- [ ] **Case 2 (best selection):** Iteration 3 produces best score; iterations 4–10 are lower → `result.best_prompt` returns iteration 3's prompt
- [ ] **Case 3 (complete failure):** All examples return metric errors → orchestrator stops after 2 iterations, returns original prompt with score=0.0, logs clear warning
