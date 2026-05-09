import benchmarkAudit from "../../../benchmarks/agentic-builder/security-accessibility-audit.json";
import benchmarkMultiPage from "../../../benchmarks/agentic-builder/multi-page-scaffold.json";
import benchmarkResponsive from "../../../benchmarks/agentic-builder/responsive-refactor.json";
import benchmarkSingle from "../../../benchmarks/agentic-builder/single-element-creation.json";
import { describe, expect, it } from "vitest";
import { runAgentLoop } from "../src/loop";
import { validateBenchmarkRun } from "../src/validator";

describe("builder agent benchmark integration", () => {
  it(
    "passes the single-element benchmark with real emitted-project validation",
    async () => {
      const result = await runAgentLoop({
        prompt: "Create a blue button that says Subscribe.",
        projectId: benchmarkSingle.startingProjectState.projectId,
        initialCode: benchmarkSingle.startingProjectState.files["src/app/page.tsx"],
        benchmarkId: "single-element-creation",
        validate: validateBenchmarkRun
      });

      expect(result.ok).toBe(true);
      expect(result.validation.typecheckPassed).toBe(true);
      expect(result.validation.buildPassed).toBe(true);
      expect(result.finalState.code).toContain("Subscribe");
      expect(result.stepLog.some((entry) => entry.phase === "act" && typeof entry.durationMs === "number")).toBe(true);
      expect(result.stepLog.some((entry) => typeof entry.tokenCount === "number")).toBe(true);
    },
    240000
  );

  it(
    "passes the multi-page scaffold benchmark with real emitted-project validation",
    async () => {
      const result = await runAgentLoop({
        prompt: benchmarkMultiPage.prompt,
        projectId: benchmarkMultiPage.startingProjectState.projectId,
        initialCode: (benchmarkMultiPage.startingProjectState.files as Record<string, string | undefined>)["src/app/page.tsx"] ?? "",
        benchmarkId: "multi-page-scaffold",
        validate: validateBenchmarkRun
      });

      expect(result.ok).toBe(true);
      expect(result.validation.typecheckPassed).toBe(true);
      expect(result.validation.buildPassed).toBe(true);
      expect(result.finalState.code).toContain("Pricing");
      expect(result.finalState.code).toContain("Contact");
      expect(result.stepLog.some((entry) => entry.phase === "act" && typeof entry.durationMs === "number")).toBe(true);
      expect(result.stepLog.some((entry) => typeof entry.tokenCount === "number")).toBe(true);
    },
    240000
  );

  it(
    "passes the responsive refactor benchmark with real emitted-project validation",
    async () => {
      const result = await runAgentLoop({
        prompt: benchmarkResponsive.prompt,
        projectId: benchmarkResponsive.startingProjectState.projectId,
        initialCode: benchmarkResponsive.startingProjectState.files["src/app/page.tsx"],
        benchmarkId: "responsive-refactor",
        validate: validateBenchmarkRun
      });

      expect(result.ok).toBe(true);
      expect(result.validation.typecheckPassed).toBe(true);
      expect(result.validation.buildPassed).toBe(true);
      expect(result.finalState.code).toContain("gridTemplateColumns");
      expect(result.finalState.code).toContain("Product preview");
      expect(result.stepLog.some((entry) => entry.phase === "act" && typeof entry.durationMs === "number")).toBe(true);
      expect(result.stepLog.some((entry) => typeof entry.tokenCount === "number")).toBe(true);
    },
    240000
  );

  it(
    "passes the audit benchmark in detect-and-auto-fix mode",
    async () => {
      const result = await runAgentLoop({
        prompt: benchmarkAudit.prompt,
        projectId: benchmarkAudit.startingProjectState.projectId,
        initialCode: benchmarkAudit.startingProjectState.files["src/app/page.tsx"],
        benchmarkId: "security-accessibility-audit",
        validate: validateBenchmarkRun
      });

      expect(result.ok).toBe(true);
      expect(result.validation.passed).toBe(true);
      expect(result.validation.typecheckPassed).toBe(true);
      expect(result.validation.buildPassed).toBe(true);
      expect(result.finalState.issues.length).toBe(0);
      expect(result.finalState.code).toContain("rel=\"noreferrer\"");
      expect(result.finalState.code).toContain("aria-label");
      expect(result.finalState.code).toContain("<button");
      expect(result.stepLog.some((entry) => entry.phase === "act" && typeof entry.durationMs === "number")).toBe(true);
      expect(result.stepLog.some((entry) => typeof entry.tokenCount === "number")).toBe(true);
    },
    240000
  );
});
