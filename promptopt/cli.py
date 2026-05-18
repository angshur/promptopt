from __future__ import annotations

import importlib
import json
from pathlib import Path

import click

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


@click.group()
def cli() -> None:
    """promptopt — automated prompt optimization."""


@cli.command()
@click.option("--config", required=True, type=click.Path(exists=True), help="Path to YAML or JSON config file.")
@click.option("--verbose", is_flag=True, default=False)
def run(config: str, verbose: bool) -> None:
    """Run prompt optimization from a config file."""
    import logging
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    cfg = _load_config(Path(config))
    _validate_config(cfg)

    metric_fn = _resolve_metric(cfg["metric"])

    from promptopt import PromptOptimizer
    optimizer = PromptOptimizer(
        prompt=cfg["prompt"],
        examples=cfg["examples"],
        metric=metric_fn,
        model=cfg.get("model", "claude-sonnet-4-6"),
        iterations=cfg.get("iterations", 10),
        num_variants=cfg.get("num_variants", 3),
    )

    click.echo(f"Starting optimization — {cfg.get('iterations', 10)} max iterations, {cfg.get('num_variants', 3)} variants each.")
    result = optimizer.run()

    click.echo("\n--- Result ---")
    click.echo(f"Best score : {result.score:.4f}")
    click.echo(f"Run ID     : {result.run_id}")
    click.echo(f"\nBest prompt:\n{result.best_prompt}")


def _load_config(path: Path) -> dict:
    text = path.read_text()
    if path.suffix in (".yaml", ".yml"):
        if not _HAS_YAML:
            raise click.ClickException("PyYAML is required for YAML config files: pip install pyyaml")
        import yaml
        return yaml.safe_load(text)
    return json.loads(text)


def _validate_config(cfg: dict) -> None:
    required = ("prompt", "examples", "metric")
    missing = [k for k in required if k not in cfg]
    if missing:
        raise click.ClickException(f"Config is missing required keys: {missing}")


def _resolve_metric(metric_cfg: str | dict):
    """Resolve a metric from config.

    String form: "exact_match" or "llm_judge:concise and accurate"
    Dict form:   {"type": "llm_judge", "criteria": "concise and accurate"}
    """
    from promptopt import exact_match, llm_judge

    if isinstance(metric_cfg, str):
        if metric_cfg == "exact_match":
            return exact_match
        if metric_cfg.startswith("llm_judge:"):
            criteria = metric_cfg.split(":", 1)[1].strip()
            return llm_judge(criteria=criteria)
        raise click.ClickException(f"Unknown metric: {metric_cfg}")

    if isinstance(metric_cfg, dict):
        mtype = metric_cfg.get("type")
        if mtype == "exact_match":
            return exact_match
        if mtype == "llm_judge":
            return llm_judge(criteria=metric_cfg.get("criteria", "accuracy"))
        raise click.ClickException(f"Unknown metric type: {mtype}")

    raise click.ClickException(f"Invalid metric config: {metric_cfg}")
