from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import litellm

if TYPE_CHECKING:
    from ..core import OptimizationState, ScoredVariant

logger = logging.getLogger(__name__)


class EvaluatorAgent:
    """Renders each example against a prompt variant, runs the LLM, scores the output."""

    def evaluate(self, variant: str, state: "OptimizationState") -> "ScoredVariant":
        from ..core import ScoredVariant

        scores: list[float] = []
        for example in state.examples:
            try:
                rendered = variant.format(**example.inputs)
                response = litellm.completion(
                    model=state.model,
                    messages=[{"role": "user", "content": rendered}],
                )
                actual_output = response.choices[0].message.content or ""
                score = float(state.metric(actual_output, example.ideal))
                scores.append(max(0.0, min(1.0, score)))
            except Exception as exc:
                logger.warning("Evaluation failed for example: %s — scoring as 0.0", exc)
                scores.append(0.0)

        avg = sum(scores) / len(scores) if scores else 0.0
        return ScoredVariant(prompt=variant, example_scores=scores, avg_score=avg)
