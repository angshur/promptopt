"""Tests for core data models, exact_match evaluator, and OrchestratorAgent loop."""
from __future__ import annotations

import uuid

import pytest

from promptopt.core import (
    Example,
    IterationResult,
    OptimizationResult,
    OptimizationState,
    ScoredVariant,
)
from promptopt.evaluators.exact_match import exact_match
from promptopt.orchestrator import OrchestratorAgent


# ---------------------------------------------------------------------------
# exact_match
# ---------------------------------------------------------------------------

def test_exact_match_identical():
    assert exact_match("hello", "hello") == 1.0


def test_exact_match_different():
    assert exact_match("hello", "world") == 0.0


def test_exact_match_strips_whitespace():
    assert exact_match("  hello  ", "hello") == 1.0


def test_exact_match_case_sensitive():
    assert exact_match("Hello", "hello") == 0.0


# ---------------------------------------------------------------------------
# OptimizationState
# ---------------------------------------------------------------------------

def _make_state(**kwargs) -> OptimizationState:
    defaults = dict(
        original_prompt="Answer: {question}",
        current_prompt="Answer: {question}",
        examples=[Example(inputs={"question": "2+2?"}, ideal="4")],
        metric=exact_match,
        model="claude-sonnet-4-6",
        max_iterations=5,
        num_variants=3,
        convergence_threshold=0.01,
        run_id=str(uuid.uuid4()),
    )
    defaults.update(kwargs)
    return OptimizationState(**defaults)


def test_optimization_state_creates():
    state = _make_state()
    assert state.current_prompt == "Answer: {question}"
    assert len(state.examples) == 1
    assert state.history == []


def test_optimization_state_original_prompt_is_immutable_by_convention():
    state = _make_state()
    original = state.original_prompt
    state.current_prompt = "modified"
    assert state.original_prompt == original


# ---------------------------------------------------------------------------
# OrchestratorAgent loop — tested with test doubles
# ---------------------------------------------------------------------------

class _FixedVariantGenerator:
    """Returns a fixed list of variants regardless of state."""
    def __init__(self, variants: list[str]) -> None:
        self._variants = variants

    def generate(self, state: OptimizationState) -> list[str]:
        return self._variants


class _FixedEvaluator:
    """Returns a fixed score for each variant (cycles through scores list)."""
    def __init__(self, scores_per_variant: list[float]) -> None:
        self._scores = scores_per_variant
        self._call_count = 0

    def evaluate(self, variant: str, state: OptimizationState) -> ScoredVariant:
        score = self._scores[self._call_count % len(self._scores)]
        self._call_count += 1
        return ScoredVariant(prompt=variant, example_scores=[score], avg_score=score)


class _SimpleOptimizer:
    """Picks highest-scoring variant; always signals continue."""
    def select(self, variants: list[ScoredVariant], state: OptimizationState) -> tuple[ScoredVariant, bool]:
        best = max(variants, key=lambda v: v.avg_score)
        return best, True


def test_orchestrator_runs_correct_number_of_iterations():
    state = _make_state(max_iterations=4)
    orch = OrchestratorAgent(
        variant_generator=_FixedVariantGenerator(["v1", "v2"]),
        evaluator=_FixedEvaluator([0.5, 0.6]),
        optimizer=_SimpleOptimizer(),
    )
    result = orch.run(state)
    assert len(result.history) == 4


def test_orchestrator_returns_best_across_all_iterations():
    """Best prompt comes from iteration 2, not the final iteration."""
    scores = [0.3, 0.9, 0.4, 0.4, 0.4, 0.4]  # iter 1: 0.3/0.9, iter 2: 0.4/0.4, ...
    state = _make_state(max_iterations=3)
    orch = OrchestratorAgent(
        variant_generator=_FixedVariantGenerator(["low", "high"]),
        evaluator=_FixedEvaluator(scores),
        optimizer=_SimpleOptimizer(),
    )
    result = orch.run(state)
    assert result.score == pytest.approx(0.9)
    assert result.best_prompt == "high"


def test_orchestrator_history_is_ordered():
    state = _make_state(max_iterations=3)
    orch = OrchestratorAgent(
        variant_generator=_FixedVariantGenerator(["v1"]),
        evaluator=_FixedEvaluator([0.5]),
        optimizer=_SimpleOptimizer(),
    )
    result = orch.run(state)
    for i, iter_result in enumerate(result.history, start=1):
        assert iter_result.iteration == i


def test_orchestrator_stops_early_on_plateau():
    """Plateau for 3 consecutive iterations triggers early stop."""
    state = _make_state(max_iterations=10, convergence_threshold=0.01)
    orch = OrchestratorAgent(
        variant_generator=_FixedVariantGenerator(["v1"]),
        evaluator=_FixedEvaluator([0.95]),  # constant score = plateau
        optimizer=_SimpleOptimizer(),
    )
    result = orch.run(state)
    # Must complete at least 2 before plateau kicks in; plateau triggers at 3 consecutive
    assert len(result.history) < 10


def test_orchestrator_fallback_to_original_on_all_zero_scores():
    """If all variants score 0.0 from the start, return original prompt."""
    state = _make_state(max_iterations=5)
    orch = OrchestratorAgent(
        variant_generator=_FixedVariantGenerator(["v1"]),
        evaluator=_FixedEvaluator([0.0]),
        optimizer=_SimpleOptimizer(),
    )
    result = orch.run(state)
    # With all-zero scores, orchestrator stops after MIN_ITERATIONS and returns original
    assert result.score == 0.0


# ---------------------------------------------------------------------------
# SQLite storage
# ---------------------------------------------------------------------------

def test_storage_init_creates_db(tmp_path, monkeypatch):
    db_path = tmp_path / ".promptopt" / "runs.db"
    monkeypatch.setattr("promptopt.storage._DB_PATH", db_path)
    from promptopt import storage
    storage.init_db()
    assert db_path.exists()
