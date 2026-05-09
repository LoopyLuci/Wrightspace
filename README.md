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

## AI Component Generation API

`project-service` exposes a component-generation endpoint used by the AI command bar.

- Endpoint: `POST /api/ai/generate-component`
- Default local URL: `http://127.0.0.1:4001/api/ai/generate-component`
- Content-Type: `application/json`

Request body:

```json
{
	"prompt": "Build a hero section with headline and CTA",
	"designTokens": {
		"colors": {
			"primary": "#0f172a"
		}
	}
}
```

- `prompt` (string, required): natural-language instruction for component generation.
- `designTokens` (object, optional): arbitrary design token payload forwarded to the model.

Successful response (`200`):

```json
{
	"irNode": {
		"id": "ai-generated-section",
		"type": "element",
		"tag": "section",
		"styles": {},
		"props": {},
		"children": []
	}
}
```

Error responses:

- `400`: invalid request (for example, empty `prompt`).
- `422`: generated payload failed IR validation.
- `502`: upstream AI request failed.

### Environment Variables

`services/project-service`:

- `AI_API_KEY` (preferred) or `OPENAI_API_KEY`: API key used for model calls.
- `AI_BASE_URL` (preferred) or `OPENAI_BASE_URL`: base URL for chat completions (default: `https://api.openai.com`).
- `AI_MODEL`: model name (default: `gpt-4o-mini`).

`packages/builder-ai` / browser runtime:

- `NEXT_PUBLIC_BUILDER_AI_ENDPOINT`: override API endpoint used by the command bar.
	- Default: `http://127.0.0.1:4001/api/ai/generate-component`
