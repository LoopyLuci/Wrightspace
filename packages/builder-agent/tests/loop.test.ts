import benchmarkAudit from "../../../benchmarks/agentic-builder/security-accessibility-audit.json";
import benchmarkSingle from "../../../benchmarks/agentic-builder/single-element-creation.json";
import { describe, expect, it } from "vitest";
import { runAgentLoop } from "../src/loop.js";

describe("builder agent loop", () => {
  it("runs the single-element benchmark and produces a step log", async () => {
    const result = await runAgentLoop({
      prompt: "Create a blue button that says Subscribe.",
      projectId: benchmarkSingle.startingProjectState.projectId,
      initialCode: benchmarkSingle.startingProjectState.files["src/app/page.tsx"],
      benchmarkId: "single-element-creation",
      validate: async ({ finalState }) => ({
        passed: finalState.code.includes("Subscribe"),
        benchmarkPassed: finalState.code.includes("Subscribe"),
        message: "Inserted CTA button for benchmark validation.",
        typecheckPassed: true,
        buildPassed: true
      })
    });

    expect(result.ok).toBe(true);
    expect(result.finalState.code).toContain("Subscribe");
    expect(result.stepLog.length).toBeGreaterThan(0);
  });

  it("runs the security audit benchmark in auto-fix mode", async () => {
    const result = await runAgentLoop({
      prompt: benchmarkAudit.prompt,
      projectId: benchmarkAudit.startingProjectState.projectId,
      initialCode: benchmarkAudit.startingProjectState.files["src/app/page.tsx"],
      benchmarkId: "security-accessibility-audit",
      validate: async ({ initialState, finalState }) => ({
        passed: initialState.code !== finalState.code && finalState.issues.length === 0,
        benchmarkPassed: initialState.code !== finalState.code && finalState.issues.length === 0,
        message: "Auto-fixed benchmark issues without redesigning the page.",
        details: finalState.issues,
        typecheckPassed: true,
        buildPassed: true
      })
    });

    expect(result.ok).toBe(true);
    expect(result.finalState.issues.length).toBe(0);
    expect(result.finalState.code).toContain("rel=\"noreferrer\"");
  });

  it("continues after a failed step when continueOnError is enabled", async () => {
    const brokenIrSnapshot = JSON.stringify({
      id: "broken-page",
      name: "Page",
      route: "/",
      meta: {},
      state: [],
      root: {
        id: "broken-root",
        type: "text",
        content: "Not an element root",
        styles: {}
      }
    });

    const result = await runAgentLoop({
      prompt: "Create a blue button that says Subscribe.",
      projectId: "continue-on-error-project",
      initialIrSnapshot: brokenIrSnapshot,
      benchmarkId: "single-element-creation",
      continueOnError: true,
      validate: async ({ finalState }) => ({
        passed: finalState.ir.id === "broken-page",
        benchmarkPassed: true,
        message: "Validation passed after recovery.",
        typecheckPassed: true,
        buildPassed: true
      })
    });

    expect(result.ok).toBe(true);
    expect(result.stepLog.some((entry) => entry.phase === "act" && entry.status === "skipped")).toBe(true);
    expect(result.stepLog.some((entry) => entry.phase === "rollback" && entry.message.includes("Restored last clean snapshot"))).toBe(true);
  });

  it("halts after a failed step when continueOnError is disabled", async () => {
    const brokenIrSnapshot = JSON.stringify({
      id: "broken-page",
      name: "Page",
      route: "/",
      meta: {},
      state: [],
      root: {
        id: "broken-root",
        type: "text",
        content: "Not an element root",
        styles: {}
      }
    });

    const result = await runAgentLoop({
      prompt: "Create a blue button that says Subscribe.",
      projectId: "halt-on-error-project",
      initialIrSnapshot: brokenIrSnapshot,
      benchmarkId: "single-element-creation",
      continueOnError: false,
      validate: async () => ({
        passed: true,
        benchmarkPassed: true,
        message: "Validation passed.",
        typecheckPassed: true,
        buildPassed: true
      })
    });

    expect(result.ok).toBe(false);
    expect(result.stepLog.some((entry) => entry.phase === "act" && entry.status === "skipped")).toBe(true);
    expect(result.stepLog.some((entry) => entry.phase === "report" && entry.status === "partial")).toBe(true);
  });
});