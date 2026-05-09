import * as Y from "yjs";
import { describe, expect, it } from "vitest";
import { parsePageIR } from "../../builder-ir/dist/src/reverse-parser.js";
import { createHeroCode } from "../src/fixtures";
import {
  CANVAS_ORIGIN,
  EDITOR_ORIGIN,
  SYNC_ORIGIN,
  createSyncManager,
  getSourceText,
  setYText
} from "../src/index";

function createDoc() {
  const doc = new Y.Doc();
  doc.getMap("workspace");
  return doc;
}

function seed(doc: Y.Doc, projectId: string) {
  const sourceText = getSourceText(doc, projectId);
  const workspace = doc.getMap("workspace");
  const code = createHeroCode();
  setYText(sourceText, code, SYNC_ORIGIN);
  workspace.set("code", code);
  workspace.set("ir", JSON.stringify(parsePageIR(code), null, 2));
}

describe("sync manager", () => {
  it("regenerates code from IR changes while preserving custom functions", () => {
    const projectId = "hero-project";
    const doc = createDoc();
    seed(doc, projectId);
    const manager = createSyncManager(doc, projectId);
    manager.start();

    const workspace = doc.getMap("workspace");
    const nextIr = JSON.parse((workspace.get("ir") as string | undefined) ?? "{}") as Record<string, unknown>;
    const root = nextIr.root as Record<string, unknown>;
    root.children = (root.children as Array<Record<string, unknown>>).map((child) =>
      child.id === "heading-uuid" ? { ...child, content: "Builder Live" } : child
    );
    workspace.set("ir", JSON.stringify(nextIr, null, 2));

    const code = getSourceText(doc, projectId).toString();
    expect(code).toContain("Builder Live");
    expect(code).toContain("trackEvent('hero_cta_clicked')");
  });

  it("updates IR when the generated code changes", () => {
    const projectId = "hero-project";
    const doc = createDoc();
    seed(doc, projectId);
    const manager = createSyncManager(doc, projectId);
    manager.start();

    const sourceText = getSourceText(doc, projectId);
    const updatedCode = sourceText.toString().replace("Acme Analytics", "Builder Studio");
    setYText(sourceText, updatedCode, EDITOR_ORIGIN);

    const workspace = doc.getMap("workspace");
    expect((workspace.get("ir") as string | undefined) ?? "").toContain("Builder Studio");
  });

  it("ignores custom region-only edits when updating IR", () => {
    const projectId = "hero-project";
    const doc = createDoc();
    seed(doc, projectId);
    const manager = createSyncManager(doc, projectId);
    manager.start();

    const workspace = doc.getMap("workspace");
    const beforeIr = workspace.get("ir") as string;
    const sourceText = getSourceText(doc, projectId);
    const updatedCode = sourceText.toString().replace("router.push('/signup');", "console.log('custom change');\n  router.push('/signup');");
    setYText(sourceText, updatedCode, EDITOR_ORIGIN);

    expect(workspace.get("ir")).toBe(beforeIr);
  });

  it("queues or suppresses sync based on mode", () => {
    const projectId = "hero-project";
    const doc = createDoc();
    seed(doc, projectId);
    const manager = createSyncManager(doc, projectId);
    manager.start();

    const workspace = doc.getMap("workspace");
    const sourceText = getSourceText(doc, projectId);

    manager.setMode("manual");
    setYText(sourceText, sourceText.toString().replace("Get Started", "Manual Hold"), EDITOR_ORIGIN);
    expect((workspace.get("ir") as string | undefined) ?? "").not.toContain("Manual Hold");
    manager.syncNow();
    expect((workspace.get("ir") as string | undefined) ?? "").toContain("Manual Hold");

    manager.setMode("loose");
    workspace.set("ir", (workspace.get("ir") as string).replace("Manual Hold", "Loose Mode"));
    expect(sourceText.toString()).not.toContain("Loose Mode");
    manager.syncNow();
    expect(sourceText.toString()).toContain("Loose Mode");

    manager.setMode("strict");
    workspace.set("ir", (workspace.get("ir") as string).replace("Loose Mode", "Strict Mode"));
    expect(sourceText.toString()).toContain("Strict Mode");
  });
});