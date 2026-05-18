from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import OptimizationResult

logger = logging.getLogger(__name__)

_DB_PATH = Path.home() / ".promptopt" / "runs.db"


def _connect() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY,
            original_prompt TEXT NOT NULL,
            model TEXT NOT NULL,
            max_iterations INTEGER NOT NULL,
            num_variants INTEGER NOT NULL,
            best_prompt TEXT,
            best_score REAL,
            created_at TEXT NOT NULL,
            completed_at TEXT
        );

        CREATE TABLE IF NOT EXISTS iterations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL REFERENCES runs(id),
            iteration_num INTEGER NOT NULL,
            best_prompt TEXT NOT NULL,
            best_score REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            iteration_id INTEGER NOT NULL REFERENCES iterations(id),
            prompt TEXT NOT NULL,
            avg_score REAL NOT NULL,
            example_scores TEXT NOT NULL
        );
    """)
    conn.commit()


def init_db() -> None:
    with _connect() as conn:
        _ensure_schema(conn)


def save_run(result: "OptimizationResult", original_prompt: str, model: str, max_iterations: int, num_variants: int) -> None:
    with _connect() as conn:
        _ensure_schema(conn)
        now = datetime.now(timezone.utc).isoformat()

        conn.execute(
            """
            INSERT INTO runs (id, original_prompt, model, max_iterations, num_variants,
                              best_prompt, best_score, created_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (result.run_id, original_prompt, model, max_iterations, num_variants,
             result.best_prompt, result.score, now, now),
        )

        for iter_result in result.history:
            cursor = conn.execute(
                """
                INSERT INTO iterations (run_id, iteration_num, best_prompt, best_score)
                VALUES (?, ?, ?, ?)
                """,
                (result.run_id, iter_result.iteration,
                 iter_result.best_variant.prompt, iter_result.best_variant.avg_score),
            )
            iteration_id = cursor.lastrowid
            for variant in iter_result.variants:
                conn.execute(
                    """
                    INSERT INTO variants (iteration_id, prompt, avg_score, example_scores)
                    VALUES (?, ?, ?, ?)
                    """,
                    (iteration_id, variant.prompt, variant.avg_score,
                     json.dumps(variant.example_scores)),
                )

        conn.commit()
        logger.debug("Run %s saved to %s", result.run_id, _DB_PATH)
