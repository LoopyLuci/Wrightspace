# Benchmarks

This directory holds benchmark scenarios used to evaluate Phase 2 agentic builder behavior.

Current benchmark suite:

- `agentic-builder/single-element-creation.json`
- `agentic-builder/multi-page-scaffold.json`
- `agentic-builder/responsive-refactor.json`
- `agentic-builder/security-accessibility-audit.json`

Each benchmark defines:

- a natural-language prompt
- an expected outcome description
- a minimal starting project state

These scenarios are intentionally small and explicit so they can be used both for manual review and for future automated agent-loop evaluation.