# WebBuilder Monorepo

Phase 1 scaffolding for the next-generation production-grade web builder.

## Workspace

- `packages/builder-client`: Next.js app shell (workspace host)
- `packages/builder-canvas`: Visual canvas package shell
- `packages/builder-ide`: Monaco IDE package shell
- `packages/builder-ir`: IR schema, validators, emitter, reverse parser
- `packages/builder-runtime`: Instrumentation runtime host
- `packages/builder-collab`: Yjs collaboration helpers
- `packages/builder-ai`: AI command bar primitives
- `services/project-service`: Rust Axum project service scaffold

## Quick Start

1. Install dependencies: `pnpm install`
2. Run dev: `pnpm dev`
3. Run tests: `pnpm test`
