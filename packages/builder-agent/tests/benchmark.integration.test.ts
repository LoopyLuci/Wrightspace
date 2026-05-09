import benchmarkAudit from "../../../benchmarks/agentic-builder/security-accessibility-audit.json";
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
    },
    240000
  );

  it(
    "passes the audit benchmark in detect-and-report mode with severity ratings",
    async () => {
      const result = await runAgentLoop({
        prompt: benchmarkAudit.prompt,
        projectId: benchmarkAudit.startingProjectState.projectId,
        initialCode: benchmarkAudit.startingProjectState.files["src/app/page.tsx"],
        benchmarkId: "security-accessibility-audit",
        validate: validateBenchmarkRun
      });

      expect(result.ok).toBe(true);
      expect(result.validation.partial).toBe(true);
      expect(result.validation.typecheckPassed).toBe(true);
      expect(result.validation.buildPassed).toBe(true);
      expect(result.finalState.issues.length).toBeGreaterThan(0);
      expect(result.finalState.issues.every((issue) => issue.severity)).toBe(true);
    },
    240000
  );
});
