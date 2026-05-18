from __future__ import annotations

import logging

from .agents import EvaluatorAgent, OptimizerAgent, VariantGeneratorAgent
from .core import IterationResult, OptimizationResult, OptimizationState, ScoredVariant

logger = logging.getLogger(__name__)

_PLATEAU_THRESHOLD = 3
_MIN_ITERATIONS_BEFORE_STOP = 2


class OrchestratorAgent:
    """Runs the prompt optimization loop.

    Communicates with sub-agents only through OptimizationState — no agent
    calls another agent directly.
    """

    def __init__(
        self,
        variant_generator: VariantGeneratorAgent | None = None,
        evaluator: EvaluatorAgent | None = None,
        optimizer: OptimizerAgent | None = None,
    ) -> None:
        self.variant_generator = variant_generator or VariantGeneratorAgent()
        self.evaluator = evaluator or EvaluatorAgent()
        self.optimizer = optimizer or OptimizerAgent()

    def run(self, state: OptimizationState) -> OptimizationResult:
        best_overall: ScoredVariant | None = None
        prev_best_score = -1.0
        consecutive_plateaus = 0

        for i in range(1, state.max_iterations + 1):
            logger.info("Iteration %d/%d — current prompt: %.60s...", i, state.max_iterations, state.current_prompt)

            # 1. Generate variants
            variant_prompts = self.variant_generator.generate(state)

            # 2. Evaluate each variant
            scored_variants: list[ScoredVariant] = [
                self.evaluator.evaluate(v, state) for v in variant_prompts
            ]

            # 3. Guard: all scores zero → bad signal, stop
            if all(sv.avg_score == 0.0 for sv in scored_variants) and i >= _MIN_ITERATIONS_BEFORE_STOP:
                logger.warning(
                    "All variants scored 0.0 in iteration %d — evaluation signal is bad. Stopping.", i
                )
                break

            # 4. Select best + decide whether to continue
            best_variant, should_continue = self.optimizer.select(scored_variants, state)

            # 5. Record iteration
            iteration_result = IterationResult(
                iteration=i,
                variants=scored_variants,
                best_variant=best_variant,
            )
            state.history.append(iteration_result)

            # 6. Track overall best across all iterations
            if best_overall is None or best_variant.avg_score > best_overall.avg_score:
                best_overall = best_variant

            # 7. Plateau detection
            delta = best_variant.avg_score - prev_best_score
            if i >= _MIN_ITERATIONS_BEFORE_STOP and delta < state.convergence_threshold:
                consecutive_plateaus += 1
                logger.debug("Plateau %d/%d (delta=%.4f)", consecutive_plateaus, _PLATEAU_THRESHOLD, delta)
            else:
                consecutive_plateaus = 0
            prev_best_score = best_variant.avg_score

            # 8. Advance state to best prompt
            state.current_prompt = best_variant.prompt

            # 9. Early stopping
            if not should_continue:
                logger.info("OptimizerAgent signalled stop at iteration %d.", i)
                break
            if consecutive_plateaus >= _PLATEAU_THRESHOLD:
                logger.info("Converged after %d iterations (score plateau).", i)
                break

        final_prompt = best_overall.prompt if best_overall else state.original_prompt
        final_score = best_overall.avg_score if best_overall else 0.0

        return OptimizationResult(
            best_prompt=final_prompt,
            score=final_score,
            history=state.history,
            run_id=state.run_id,
        )
