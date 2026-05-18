# CLAUDE.md — promptopt Dev Agent

## What you are

Dev Agent for promptopt — an open-source Python SDK for automated prompt optimization using multi-agent architecture.

## What to read before every session

1. ~/Documents/Vercel/startup-studio/you.md
2. ~/Documents/Vercel/startup-studio/domains/builder.md
3. ~/Documents/Vercel/startup-studio/agent-architecture.md
4. core.md
5. spec.md
6. eval-spec.md
7. current-task.md
8. progress.md
9. needs-you.md

## What to do when done

1. Update progress.md (Done / Next / Blocked / Session log)
2. Rewrite current-task.md with the next task
3. Write non-trivial decisions to decisions.md with rationale
4. Write to needs-you.md and STOP if blocked — do not guess

## Architecture rules (read spec.md for full detail)

- The product itself uses a multi-agent architecture internally: OrchestratorAgent → VariantGeneratorAgent + EvaluatorAgent + OptimizerAgent
- Agents communicate through a shared `OptimizationState` dataclass — not through direct calls
- No agent calls another agent directly — all routing through the orchestrator
- This mirrors the studio agent-architecture.md pattern: agents communicate through state, not side channels

## Tech stack

- Language: Python 3.11+
- Package: `promptopt` (pip-installable)
- LLM calls: litellm (model-agnostic — works with Claude, GPT-4o, Gemini)
- Persistence: SQLite via stdlib `sqlite3` (no ORM, no migrations framework)
- CLI: Click
- Testing: pytest
- Type hints: required on all public APIs

## Build rules

- No code before spec — spec.md and eval-spec.md exist and are authoritative
- All public API functions must have type hints
- Write tests before or alongside implementation — not after
- Golden test cases from eval-spec.md must be implemented as actual pytest tests in evals/
- SQLite schema must be defined in one place (not scattered across files)
- Never add dependencies that aren't in requirements.txt — check first
- Weekend-pace: each task must be completable in one Saturday session

## Idea inbox

When the user says "idea: ..." or "I have an idea: ...", create a new file at:

`~/Documents/Vercel/startup-studio/inbox/<kebab-case-name>.md`

Use this structure:
```
# <Idea name>

<One paragraph: what it is, who it's for, what problem it solves.>

---

## The pain
## How it works
## Who it's for
## Riskiest assumption
## Open questions
## Relationship to existing projects
```

Fill in as much as you can from what the user said. Leave sections as bullet-point stubs if there isn't enough to go on. Confirm the file was created and where.

## Rules

- Read ALL coordination files before starting any work
- Update current-task.md and progress.md at end of every session
- Write to decisions.md any time a non-trivial choice is made
- Write to needs-you.md and stop if blocked — do not guess
- Never leave the project in an ambiguous state
