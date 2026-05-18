from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import OptimizationState


class VariantGeneratorAgent:
    """Uses meta-prompting to generate N improved prompt variants from the current state."""

    def generate(self, state: "OptimizationState") -> list[str]:
        raise NotImplementedError(
            "VariantGeneratorAgent.generate() is not implemented yet. "
            "Session 2 task: implement via litellm meta-prompting."
        )
