import * as Y from "yjs";
import { describe, expect, it } from "vitest";
import { createHeroCode } from "@builder/sync/fixtures";
import {
  EDITOR_ORIGIN,
  SYNC_ORIGIN,
  createSyncManager,
  getSourceText,
  setYText
} from "@builder/sync";

function createWorkspaceDoc(projectId: string) {
  const doc = new Y.Doc();
  doc.getMap("workspace");
  doc.getText(`source:${projectId}:app/page.tsx`);
  return doc;
}

describe("live workspace sync", () => {
  it("keeps the hero fixture aligned across code, IR, and custom regions", () => {
    const projectId = "hero-project";
    const doc = createWorkspaceDoc(projectId);
    const manager = createSyncManager(doc, projectId);
    manager.start();

    const sourceText = getSourceText(doc, projectId);
    setYText(sourceText, createHeroCode(), SYNC_ORIGIN);

    const workspace = doc.getMap("workspace");

    setYText(sourceText, sourceText.toString().replace("Acme Analytics", "Builder Studio"), EDITOR_ORIGIN);
    expect((workspace.get("ir") as string | undefined) ?? "").toContain("Builder Studio");

    const nextIr = JSON.parse(workspace.get("ir") as string) as Record<string, unknown>;
    const root = nextIr.root as Record<string, unknown>;
    const buttonNode = (root.children as Array<Record<string, unknown>>).find((child) => child.id === "cta-button");
    if (buttonNode) {
      buttonNode.styles = {
        ...(buttonNode.styles as Record<string, unknown>),
        backgroundColor: { value: "var(--color-primary-900)" }
      };
    }

    doc.transact(() => {
      workspace.set("ir", JSON.stringify(nextIr, null, 2));
    }, EDITOR_ORIGIN);

    expect(sourceText.toString()).toContain("bg-primary-900");

    const customUpdated = sourceText
      .toString()
      .replace("trackEvent('hero_cta_clicked');", "console.log('cta clicked');\n  trackEvent('hero_cta_clicked');");
    setYText(sourceText, customUpdated, EDITOR_ORIGIN);

    const afterIr = JSON.parse(workspace.get("ir") as string) as Record<string, unknown>;
    const afterRoot = afterIr.root as Record<string, unknown>;
    const afterButton = (afterRoot.children as Array<Record<string, unknown>>).find((child) => child.id === "cta-button");
    if (afterButton) {
      afterButton.styles = {
        ...(afterButton.styles as Record<string, unknown>),
        backgroundColor: { value: "var(--color-primary-900)" }
      };
    }

    doc.transact(() => {
      workspace.set("ir", JSON.stringify(afterIr, null, 2));
    }, SYNC_ORIGIN);

    expect(sourceText.toString()).toContain("console.log('cta clicked')");
  });
});