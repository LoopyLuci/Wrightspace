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

  it("runs the security audit benchmark in detect-and-report mode", async () => {
    const result = await runAgentLoop({
      prompt: benchmarkAudit.prompt,
      projectId: benchmarkAudit.startingProjectState.projectId,
      initialCode: benchmarkAudit.startingProjectState.files["src/app/page.tsx"],
      benchmarkId: "security-accessibility-audit",
      validate: async ({ initialState, finalState }) => ({
        passed: initialState.code === finalState.code && finalState.issues.length > 0,
        partial: true,
        benchmarkPassed: finalState.issues.length > 0,
        message: "Reported severity-rated issues without mutating source.",
        details: finalState.issues,
        typecheckPassed: true,
        buildPassed: true
      })
    });

    expect(result.ok).toBe(true);
    expect(result.finalState.issues.length).toBeGreaterThan(0);
    expect(result.finalState.issues.every((issue) => issue.severity)).toBe(true);
  });
});