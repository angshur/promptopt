from __future__ import annotations

import uuid
from typing import Callable

from .core import Example, OptimizationResult, OptimizationState
from .evaluators import exact_match, llm_judge
from .orchestrator import OrchestratorAgent
from . import storage

__all__ = ["PromptOptimizer", "exact_match", "llm_judge"]


class PromptOptimizer:
    """User-facing entry point for prompt optimization.

    Example::

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
    """

    def __init__(
        self,
        prompt: str,
        examples: list[dict],
        metric: Callable[[str, str], float],
        model: str = "claude-sonnet-4-6",
        iterations: int = 10,
        num_variants: int = 3,
        convergence_threshold: float = 0.01,
    ) -> None:
        self._prompt = prompt
        self._examples = [Example(inputs=e["inputs"], ideal=e["ideal"]) for e in examples]
        self._metric = metric
        self._model = model
        self._iterations = iterations
        self._num_variants = num_variants
        self._convergence_threshold = convergence_threshold

    def run(self) -> OptimizationResult:
        state = OptimizationState(
            original_prompt=self._prompt,
            current_prompt=self._prompt,
            examples=self._examples,
            metric=self._metric,
            model=self._model,
            max_iterations=self._iterations,
            num_variants=self._num_variants,
            convergence_threshold=self._convergence_threshold,
            run_id=str(uuid.uuid4()),
        )
        orchestrator = OrchestratorAgent()
        result = orchestrator.run(state)
        storage.save_run(
            result,
            original_prompt=self._prompt,
            model=self._model,
            max_iterations=self._iterations,
            num_variants=self._num_variants,
        )
        return result
