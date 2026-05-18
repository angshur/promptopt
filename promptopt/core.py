from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Example:
    inputs: dict[str, str]
    ideal: str


@dataclass
class ScoredVariant:
    prompt: str
    example_scores: list[float]
    avg_score: float


@dataclass
class IterationResult:
    iteration: int
    variants: list[ScoredVariant]
    best_variant: ScoredVariant


@dataclass
class OptimizationState:
    original_prompt: str
    current_prompt: str
    examples: list[Example]
    metric: Callable[[str, str], float]
    model: str
    max_iterations: int
    num_variants: int
    convergence_threshold: float
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    history: list[IterationResult] = field(default_factory=list)


@dataclass
class OptimizationResult:
    best_prompt: str
    score: float
    history: list[IterationResult]
    run_id: str
