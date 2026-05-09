# Framework Parity Contract

This document is the source of truth for emitter and parser authors implementing multi-framework support.

## Scope

The parity contract covers the core node set and related behavior for framework targets:
- next-react
- vite-react

All framework adapters must preserve the same canonical IR semantics for core nodes.

## Core Node Set

### Element Node
- Required fields: id, type=element, tag, styles, props, children
- Optional fields: name, locked, customCode, events, accessibility
- Behavior:
  - Emitters must preserve id via data-builder-id on the emitted JSX element.
  - Parse must round-trip data-builder-id back to ElementNode.id.
  - Unknown props must be preserved in props.
  - Event handlers must map to JSX event props and back to events[].
- Fallbacks:
  - If target framework cannot represent a prop/event directly, preserve as literal prop text where possible.

### Text Node
- Required fields: id, type=text, content, styles
- Behavior:
  - Emitters wrap text in a stable JSX host with data-builder-id for deterministic parsing.
  - content supports string literals and binding objects.
  - Parse must preserve binding expressions semantically.
- Fallbacks:
  - Unsupported expression forms may be stringified but must preserve semantic intent.

### Styles Contract
- Styles are canonicalized in ResponsiveStyles.
- Emitters map canonical styles to framework CSS utility classes (Tailwind-first mapping).
- Parsers map known utility classes back into canonical style keys.
- Unknown classes must be preserved as className in props.
- Semantic equivalence, not class-token identity, is required for style parity.

### Props Contract
- Props are framework-agnostic key/value pairs on element/component nodes.
- Emitters must preserve scalar and object values where representable.
- Parsers must preserve literals and binding expressions.
- data-builder-id is reserved and must not be duplicated into props.

### Children Contract
- Parent-child order is stable and significant.
- Emitters and parsers must preserve child ordering.
- Empty children arrays are valid and must remain empty.

### Events Contract
- Event handlers live in events[] with { name, handler, preventDefault? }.
- Emitters map events[] to JSX handler attributes.
- Parsers map JSX handler attributes back to events[].
- Unknown/advanced handlers should be preserved as code strings.

### Slot Mapping Contract
- Slot nodes and component slots are part of the canonical core contract even if not fully emitted by all framework adapters in this increment.
- Emitters without native slot support must degrade to explicit placeholder regions while preserving slot identity metadata.
- Parsers must reconstruct slot identity and fallback children where emitted markers exist.

Implementation notes for next-react and vite-react:
- Component slots are emitted as named region wrappers with data-builder-slot markers.
- Slot nodes are emitted with data-builder-node="slot" and data-builder-slot-name markers.
- Slot fallback content is emitted as the slot node body and parsed back into SlotNode.fallback.

Known limitations:
- Slot regions are represented through explicit marker wrappers rather than framework-native slot APIs.
- Arbitrary manual edits that remove marker wrappers can break slot reconstruction.

### State Variable Contract
- Page/state variables are canonical declarations with { name, type, initialValue, persist? }.
- If a target adapter cannot emit state directly in this increment, it must preserve state in IR and avoid destructive parse behavior.
- Future adapters must map this contract to native framework state primitives.

Implementation notes for next-react and vite-react:
- State variables are emitted as React useState declarations.
- Each emitted state declaration includes a builder state owner marker comment.
- Parsers recover state from useState declarations and owner markers, restoring component state arrays.

Known limitations:
- State reconstruction depends on preserved declaration format and owner marker comments.
- Complex custom initializers beyond JSON-literals are preserved as raw text semantics where exact type inference is not guaranteed.

## Custom Code Regions

Emitters must preserve builder regions:
- imports
- variables
- functions
- effects

Parsers must extract and restore these regions onto root.customCode without mutating region payload text.

## Fidelity Threshold

Round-trip quality gates are:
- Structural equality for core nodes across IR -> emit -> parse -> IR
- Semantic equivalence for styles
  - Utility class ordering may differ
  - Canonical style meaning must remain identical

Required parity checks:
- Same node types and ids
- Same tree shape and ordering
- Same props/event/binding semantics
- Same custom code region payloads

## Framework-Specific MVP Rules

### next-react
- Uses app/page.tsx entry for page component.
- Uses app/layout.tsx shell.

### vite-react
- Uses src/main.tsx + ReactDOM.createRoot entry.
- Uses src/App.tsx page component.
- Uses src/index.css and includes Tailwind directives.
- Single-page output for MVP.
