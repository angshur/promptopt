"""Golden test cases from eval-spec.md.

These tests exercise the real LLM-backed agents and require API keys.
Marked xfail until the relevant agent is implemented.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Feature 1: VariantGeneratorAgent
# ---------------------------------------------------------------------------

@pytest.mark.xfail(reason="VariantGeneratorAgent not implemented — session 2 task")
def test_golden_variant_generator_improves_brevity():
    """Case 1: Input 'Summarize: {text}' + 5 failed long outputs → variant instructs brevity."""
    from promptopt.core import Example, OptimizationState
    from promptopt.evaluators.exact_match import exact_match
    from promptopt.agents.variant_generator import VariantGeneratorAgent
    import uuid

    state = OptimizationState(
        original_prompt="Summarize: {text}",
        current_prompt="Summarize: {text}",
        examples=[Example(inputs={"text": "Long article..."}, ideal="Short summary.")],
        metric=exact_match,
        model="claude-sonnet-4-6",
        max_iterations=5,
        num_variants=3,
        convergence_threshold=0.01,
        run_id=str(uuid.uuid4()),
    )
    agent = VariantGeneratorAgent()
    variants = agent.generate(state)

    brevity_keywords = ["sentence", "words", "brief", "concise", "short"]
    assert any(
        any(kw in v.lower() for kw in brevity_keywords)
        for v in variants
    ), "Expected at least one variant to instruct brevity"


@pytest.mark.xfail(reason="VariantGeneratorAgent not implemented — session 2 task")
def test_golden_variant_generator_preserves_placeholders():
    """Case 2: Prompt with {user_name} and {context} → all 3 variants preserve both."""
    from promptopt.core import Example, OptimizationState
    from promptopt.evaluators.exact_match import exact_match
    from promptopt.agents.variant_generator import VariantGeneratorAgent
    import uuid

    state = OptimizationState(
        original_prompt="Hello {user_name}, here is your {context}:",
        current_prompt="Hello {user_name}, here is your {context}:",
        examples=[Example(inputs={"user_name": "Alice", "context": "report"}, ideal="Hello Alice, here is your report:")],
        metric=exact_match,
        model="claude-sonnet-4-6",
        max_iterations=3,
        num_variants=3,
        convergence_threshold=0.01,
        run_id=str(uuid.uuid4()),
    )
    agent = VariantGeneratorAgent()
    variants = agent.generate(state)

    assert len(variants) == 3
    for v in variants:
        assert "{user_name}" in v, f"Placeholder {{user_name}} missing in variant: {v}"
        assert "{context}" in v, f"Placeholder {{context}} missing in variant: {v}"


# ---------------------------------------------------------------------------
# Feature 2: EvaluatorAgent — llm_judge
# ---------------------------------------------------------------------------

@pytest.mark.xfail(reason="llm_judge not implemented — session 3 task")
def test_golden_llm_judge_clear_pass():
    """Case 1: Output identical to ideal → score ≥ 0.9."""
    from promptopt.evaluators.llm_judge import llm_judge

    judge = llm_judge(criteria="matches ideal output")
    score = judge("The sky is blue.", "The sky is blue.")
    assert score >= 0.9


@pytest.mark.xfail(reason="llm_judge not implemented — session 3 task")
def test_golden_llm_judge_clear_fail():
    """Case 2: Empty output → score ≤ 0.1."""
    from promptopt.evaluators.llm_judge import llm_judge

    judge = llm_judge(criteria="accurate and complete")
    score = judge("", "The sky is blue.")
    assert score <= 0.1


@pytest.mark.xfail(reason="llm_judge not implemented — session 3 task")
def test_golden_llm_judge_criteria_specificity():
    """Case 3: 50-word output fails 'under 20 words' but passes 'factually accurate'."""
    from promptopt.evaluators.llm_judge import llm_judge

    long_output = " ".join(["word"] * 50)
    ideal = "Short answer."

    brevity_judge = llm_judge(criteria="under 20 words")
    accuracy_judge = llm_judge(criteria="factually accurate")

    assert brevity_judge(long_output, ideal) <= 0.4
    assert accuracy_judge(long_output, ideal) >= 0.6


# ---------------------------------------------------------------------------
# Feature 3: OrchestratorAgent convergence
# ---------------------------------------------------------------------------

def test_golden_orchestrator_early_stopping():
    """Case 1: Plateau at 0.95 for 3 iterations → stops before max_iterations."""
    from promptopt.core import Example, OptimizationState, ScoredVariant
    from promptopt.evaluators.exact_match import exact_match
    from promptopt.orchestrator import OrchestratorAgent
    import uuid

    class _HighScoreVariantGen:
        def generate(self, state):
            return ["great prompt"]

    class _HighScoreEval:
        def evaluate(self, variant, state):
            return ScoredVariant(prompt=variant, example_scores=[0.95], avg_score=0.95)

    class _SimpleOpt:
        def select(self, variants, state):
            best = max(variants, key=lambda v: v.avg_score)
            return best, True

    state = OptimizationState(
        original_prompt="Q: {q}",
        current_prompt="Q: {q}",
        examples=[Example(inputs={"q": "2+2?"}, ideal="4")],
        metric=exact_match,
        model="claude-sonnet-4-6",
        max_iterations=15,
        num_variants=1,
        convergence_threshold=0.01,
        run_id=str(uuid.uuid4()),
    )
    orch = OrchestratorAgent(
        variant_generator=_HighScoreVariantGen(),
        evaluator=_HighScoreEval(),
        optimizer=_SimpleOpt(),
    )
    result = orch.run(state)
    assert len(result.history) < 15, "Should have stopped early due to plateau"


def test_golden_orchestrator_best_selection_not_last():
    """Case 2: Best score in iteration 3; iterations 4–10 regress → result is from iter 3."""
    from promptopt.core import Example, OptimizationState, ScoredVariant
    from promptopt.evaluators.exact_match import exact_match
    from promptopt.orchestrator import OrchestratorAgent
    import uuid

    scores = [0.3, 0.5, 0.95, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]
    prompts = [f"prompt_{i}" for i in range(10)]
    call_idx = [0]

    class _SequencedGen:
        def generate(self, state):
            p = prompts[call_idx[0] % len(prompts)]
            call_idx[0] += 1
            return [p]

    class _SequencedEval:
        def __init__(self):
            self._n = 0
        def evaluate(self, variant, state):
            s = scores[self._n % len(scores)]
            self._n += 1
            return ScoredVariant(prompt=variant, example_scores=[s], avg_score=s)

    class _SimpleOpt:
        def select(self, variants, state):
            best = max(variants, key=lambda v: v.avg_score)
            return best, True

    state = OptimizationState(
        original_prompt="Q: {q}",
        current_prompt="Q: {q}",
        examples=[Example(inputs={"q": "2+2?"}, ideal="4")],
        metric=exact_match,
        model="claude-sonnet-4-6",
        max_iterations=10,
        num_variants=1,
        convergence_threshold=0.001,
        run_id=str(uuid.uuid4()),
    )
    orch = OrchestratorAgent(
        variant_generator=_SequencedGen(),
        evaluator=_SequencedEval(),
        optimizer=_SimpleOpt(),
    )
    result = orch.run(state)
    assert result.score == pytest.approx(0.95)
