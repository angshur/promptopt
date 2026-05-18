from typing import Callable


def llm_judge(criteria: str, model: str = "claude-haiku-4-5-20251001") -> Callable[[str, str], float]:
    """Returns a metric function that uses an LLM to score output against criteria.

    Session 3 task: implement via litellm with structured output (score + rationale).
    """
    def _judge(output: str, ideal: str) -> float:
        raise NotImplementedError(
            "llm_judge is not implemented yet. "
            "Session 3 task: implement via litellm with structured output."
        )

    return _judge
