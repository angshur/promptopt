def exact_match(output: str, ideal: str) -> float:
    return 1.0 if output.strip() == ideal.strip() else 0.0
