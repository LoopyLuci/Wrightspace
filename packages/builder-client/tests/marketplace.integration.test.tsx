// @vitest-environment jsdom

import { render, screen, waitFor, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import * as Y from "yjs";
import { afterEach, describe, expect, it, vi } from "vitest";
import { WorkspaceShell } from "../app/workspace-shell";
import type { RegistryEntry, BlockPackage } from "@builder/marketplace/schema";
import * as registryClient from "@builder/marketplace/registry-client";

// ---------------------------------------------------------------------------
// Shared Y.Doc store — hoisted so mock factory can reference it
// ---------------------------------------------------------------------------

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const sharedDocs = vi.hoisted(() => new Map<string, any>());

// ---------------------------------------------------------------------------
// Standard workspace shell mocks
// ---------------------------------------------------------------------------

vi.mock("@builder/collab", () => ({
  useYjsDoc: (projectId: string) => {
    if (!sharedDocs.has(projectId)) {
      const doc = new Y.Doc();
      doc.getMap("workspace");
      doc.getText(`source:${projectId}:app/page.tsx`);
      sharedDocs.set(projectId, doc);
    }
    return sharedDocs.get(projectId) as Y.Doc;
  },
  useSharedObject: (doc: Y.Doc, key: string) => doc.getMap(key),
  useAwareness: () => ({ connected: true, states: [] as unknown[] }),
}));

vi.mock("@builder/ide", () => ({
  IdeShell: () => <div>IDE Mock</div>,
}));

vi.mock("@builder/agent", () => ({
  runAgentLoop: vi.fn().mockResolvedValue({
    ok: true,
    validation: { passed: true, message: "done" },
    finalState: { projectId: "p", code: "", ir: null, issues: [] },
    stepLog: [],
  }),
}));

// ---------------------------------------------------------------------------
// Marketplace registry-client mock
// ---------------------------------------------------------------------------

vi.mock("@builder/marketplace/registry-client", () => ({
  searchBlocks: vi.fn(),
  getBlock: vi.fn(),
}));

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const makeEntry = (overrides: Partial<RegistryEntry> = {}): RegistryEntry => ({
  id: "block-abc123",
  name: "Hero Section",
  description: "A bold hero with headline and CTA",
  version: "1.0.0",
  author: "acme",
  license: "MIT",
  framework: ["next-react"],
  trust: "verified",
  keywords: ["hero", "landing"],
  category: "marketing",
  createdAt: "2026-01-01T00:00:00Z",
  updatedAt: "2026-01-01T00:00:00Z",
  dependencies: [],
  signature: "abc123sig",
  ...overrides,
});

const makePackage = (entry: RegistryEntry): BlockPackage => ({
  metadata: {
    id: entry.id,
    name: entry.name,
    description: entry.description,
    version: entry.version,
    author: entry.author,
    license: entry.license,
    framework: entry.framework,
    trust: entry.trust,
    keywords: entry.keywords,
    category: entry.category,
    createdAt: entry.createdAt,
    updatedAt: entry.updatedAt,
    dependencies: entry.dependencies,
  },
  irNode: {
    id: "hero-node",
    type: "element",
    tag: "section",
    styles: {},
    props: {},
    children: [],
  },
  signature: entry.signature,
});

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

afterEach(() => {
  cleanup();
  sharedDocs.clear();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  vi.mocked(registryClient.searchBlocks).mockReset();
  vi.mocked(registryClient.getBlock).mockReset();
});

describe("Marketplace search panel", () => {
  it("opens when Marketplace button is clicked and shows search input", async () => {
    const user = userEvent.setup();
    vi.mocked(registryClient.searchBlocks).mockResolvedValue([]);

    render(<WorkspaceShell projectId="mkt-project" />);

    expect(screen.queryByLabelText("Marketplace")).toBeNull();

    await user.click(screen.getByRole("button", { name: "Marketplace" }));

    expect(screen.getByLabelText("Marketplace")).toBeTruthy();
    expect(screen.getByLabelText("Search blocks")).toBeTruthy();
  });

  it("calls searchBlocks after debounce and renders results", async () => {
    const user = userEvent.setup();
    const entry = makeEntry();
    vi.mocked(registryClient.searchBlocks).mockResolvedValue([entry]);

    render(<WorkspaceShell projectId="mkt-project" />);
    await user.click(screen.getByRole("button", { name: "Marketplace" }));

    await user.type(screen.getByLabelText("Search blocks"), "hero");

    // Wait for debounce + async search to complete
    await waitFor(
      () => expect(registryClient.searchBlocks).toHaveBeenCalledWith(
        "http://localhost:4001",
        expect.objectContaining({ q: "hero" })
      ),
      { timeout: 1000 }
    );

    await waitFor(() => expect(screen.getByText("Hero Section")).toBeTruthy());
    expect(screen.getByText("v1.0.0")).toBeTruthy();
    // trust badge rendered in result card (distinct from filter chip area)
    expect(screen.getAllByText("verified").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByRole("button", { name: "Import Hero Section" })).toBeTruthy();
  });

  it("closes when the Close button is clicked", async () => {
    const user = userEvent.setup();
    vi.mocked(registryClient.searchBlocks).mockResolvedValue([]);

    render(<WorkspaceShell projectId="mkt-project" />);
    await user.click(screen.getByRole("button", { name: "Marketplace" }));
    expect(screen.getByLabelText("Marketplace")).toBeTruthy();

    await user.click(screen.getByRole("button", { name: "Close marketplace" }));
    expect(screen.queryByLabelText("Marketplace")).toBeNull();
  });
});

describe("Marketplace import flow", () => {
  it("imports a block and shows success toast when signature is valid", async () => {
    const user = userEvent.setup();
    const entry = makeEntry();
    const pkg = makePackage(entry);
    const projectId = "mkt-import-project";

    // Pre-seed the workspace with a valid IR so the insert path succeeds
    const preDoc = new Y.Doc();
    const preWorkspace = preDoc.getMap("workspace");
    preWorkspace.set("ir", JSON.stringify({
      id: "page-id",
      name: "Page",
      route: "/",
      meta: {},
      root: { id: "root", type: "element", tag: "main", styles: {}, props: {}, children: [] },
    }));
    sharedDocs.set(projectId, preDoc);

    vi.mocked(registryClient.searchBlocks).mockResolvedValue([entry]);
    vi.mocked(registryClient.getBlock).mockResolvedValue(pkg);

    const fetchSpy = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ valid: true }), {
        status: 200,
        headers: { "content-type": "application/json" },
      })
    );
    vi.stubGlobal("fetch", fetchSpy);

    render(<WorkspaceShell projectId={projectId} />);
    await user.click(screen.getByRole("button", { name: "Marketplace" }));

    // Wait for initial search to fire (panel opens → debounce → searchBlocks)
    await waitFor(() => expect(registryClient.searchBlocks).toHaveBeenCalled(), { timeout: 1000 });
    await waitFor(() => screen.getByRole("button", { name: "Import Hero Section" }));

    await user.click(screen.getByRole("button", { name: "Import Hero Section" }));

    await waitFor(() => expect(registryClient.getBlock).toHaveBeenCalledWith("http://localhost:4001", entry.id));
    await waitFor(() =>
      expect(fetchSpy).toHaveBeenCalledWith(
        "/api/marketplace/verify",
        expect.objectContaining({ method: "POST" })
      )
    );
    await waitFor(() => screen.getByText("Imported Hero Section v1.0.0"));
  });

  it("shows error toast and aborts when signature verification fails", async () => {
    const user = userEvent.setup();
    const entry = makeEntry();
    const pkg = makePackage(entry);

    vi.mocked(registryClient.searchBlocks).mockResolvedValue([entry]);
    vi.mocked(registryClient.getBlock).mockResolvedValue(pkg);

    const fetchSpy = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ valid: false }), {
        status: 200,
        headers: { "content-type": "application/json" },
      })
    );
    vi.stubGlobal("fetch", fetchSpy);

    render(<WorkspaceShell projectId="mkt-project" />);
    await user.click(screen.getByRole("button", { name: "Marketplace" }));

    await waitFor(() => expect(registryClient.searchBlocks).toHaveBeenCalled(), { timeout: 1000 });
    await waitFor(() => screen.getByRole("button", { name: "Import Hero Section" }));

    await user.click(screen.getByRole("button", { name: "Import Hero Section" }));

    await waitFor(() =>
      screen.getByText("Block signature invalid — import aborted")
    );
  });
});
