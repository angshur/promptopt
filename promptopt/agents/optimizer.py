from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import OptimizationState, ScoredVariant


class OptimizerAgent:
    """Selects the best-scoring variant and signals whether to continue."""

    def select(
        self,
        variants: list["ScoredVariant"],
        state: "OptimizationState",
    ) -> tuple["ScoredVariant", bool]:
        raise NotImplementedError(
            "OptimizerAgent.select() is not implemented yet. "
            "Session 4 task: implement convergence logic and best selection."
        )
