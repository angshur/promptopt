# promptopt
*What it is. Who it's for. What stage it's at.*

---

## What is it?

An open-source Python SDK and CLI for automated prompt optimization. Developers give it a prompt, a set of input/output examples, and a scoring function. A multi-agent system (orchestrator + variant generator + evaluator + optimizer) runs an iterative loop — generating improved prompt variants, scoring them, and converging on the best version. All variants are version-tracked in a local SQLite database.

## Who is it for?

AI engineers and developers building LLM applications who need to systematically improve prompts without vendor lock-in, enterprise pricing, or restructuring their entire codebase around a framework (like DSPy requires).

Primary persona: solo developer or small team (2-5 engineers) at a startup, building on top of Claude, GPT-4o, or Gemini. They've already shipped v1 of their product and are now iterating on prompt quality. They want a `pip install` solution, not an enterprise platform.

## What problem does it solve?

Prompt engineering is manual, intuition-driven, and hard to track. Enterprise tools (Arize, Weights & Biases) require significant setup and cost. DSPy forces you to restructure your app. LLM developers have no lightweight, model-agnostic tool that just takes a prompt and makes it better — with a clean API, version history, and no overhead.

## What stage is it at?

Day 0. Idea validated through market research. No code yet.

## What is it NOT?

- Not an observability or tracing platform (no spans, no traces, no dashboards)
- Not tied to any LLM provider — litellm-compatible, works with any model
- Not a DSPy replacement — no pipeline restructuring required, drop-in for any existing prompt
- Not an enterprise product — open source first, no auth, no multi-tenancy in v1
- Not a UI product in v1 — SDK and CLI only
