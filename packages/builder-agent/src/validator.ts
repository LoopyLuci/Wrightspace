import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import { tmpdir } from "node:os";
import path from "node:path";
import { buildProjectFiles } from "../../builder-export/dist/src/index.js";
import type { AgentProjectState, AgentValidationResult } from "./types";

interface ProjectBuildResult {
  typecheckPassed: boolean;
  buildPassed: boolean;
  details: string[];
}

async function writeProjectFiles(rootDir: string, files: Record<string, string>): Promise<void> {
  for (const [relativePath, content] of Object.entries(files)) {
    const filePath = path.join(rootDir, relativePath);
    await mkdir(path.dirname(filePath), { recursive: true });
    await writeFile(filePath, content, "utf8");
  }
}

function runCommand(command: string, args: string[], cwd: string): { ok: boolean; output: string } {
  const result = spawnSync(command, args, {
    cwd,
    encoding: "utf8",
    shell: process.platform === "win32"
  });

  return {
    ok: result.status === 0,
    output: `${result.stdout ?? ""}${result.stderr ?? ""}`.trim()
  };
}

export async function validateEmittedProjectBuild(projectState: AgentProjectState): Promise<ProjectBuildResult> {
  const files = buildProjectFiles(projectState.code);
  const tempDir = await mkdtemp(path.join(tmpdir(), "webbuilder-agent-"));

  try {
    await writeProjectFiles(tempDir, files);
    const install = runCommand("npm", ["install"], tempDir);
    if (!install.ok) {
      return { typecheckPassed: false, buildPassed: false, details: [install.output] };
    }

    const typecheck = runCommand("npx", ["tsc", "--noEmit", "-p", "tsconfig.json"], tempDir);
    const build = runCommand("npm", ["run", "build"], tempDir);

    return {
      typecheckPassed: typecheck.ok,
      buildPassed: build.ok,
      details: [typecheck.output, build.output].filter(Boolean)
    };
  } finally {
    await rm(tempDir, { recursive: true, force: true });
  }
}

function checkSingleElement(prompt: string, state: AgentProjectState): AgentValidationResult {
  const promptLabelMatch = prompt.match(/says?\s+(["']?)([^"'.!?]+)\1/i);
  const expectedLabel = promptLabelMatch?.[2]?.trim() || "Subscribe";
  const hasButton = JSON.stringify(state.ir).includes('"tag":"button"') || JSON.stringify(state.ir).includes('"tag": "button"');
  const hasLabel = state.code.includes(expectedLabel) || JSON.stringify(state.ir).includes(expectedLabel);

  return {
    passed: hasButton && hasLabel,
    benchmarkPassed: hasButton && hasLabel,
    message: hasButton && hasLabel ? "CTA button inserted successfully." : "Expected CTA button was not found in the final state."
  };
}

function checkAudit(initialState: AgentProjectState, finalState: AgentProjectState): AgentValidationResult {
  const code = finalState.code;
  const fixedExternalLinks = !/target="_blank"(?![^>]*rel="[^"]*noreferrer)/.test(code);
  const fixedFormLabels = !/<input[^>]+placeholder=/.test(code) || /<input[^>]+aria-label=/.test(code) || /<label/.test(code);
  const fixedButtonSemantics = !/role="button"/.test(code) && /<button/.test(code);
  const fixedImageAlt = !/<img\b(?![^>]*\balt=)[^>]*>/.test(code);
  const fixedButtonLabel = !/<button\b[^>]*>\s*<\/button>/.test(code);
  const mutated = initialState.code !== finalState.code;
  const unresolvedIssues = finalState.issues.length;

  const passed =
    mutated
    && fixedExternalLinks
    && fixedFormLabels
    && fixedButtonSemantics
    && fixedImageAlt
    && fixedButtonLabel
    && unresolvedIssues === 0;

  return {
    passed,
    benchmarkPassed: passed,
    message: passed
      ? "Security and accessibility issues were auto-fixed successfully."
      : "Audit auto-fix did not fully resolve required security/accessibility rules.",
    details: {
      unresolvedIssues,
      fixedExternalLinks,
      fixedFormLabels,
      fixedButtonSemantics,
      fixedImageAlt,
      fixedButtonLabel
    }
  };
}

export async function validateBenchmarkRun(input: {
  prompt: string;
  benchmarkId?: string;
  initialState: AgentProjectState;
  finalState: AgentProjectState;
}): Promise<AgentValidationResult> {
  let benchmarkResult: AgentValidationResult = {
    passed: true,
    benchmarkPassed: true,
    message: "Benchmark checks passed."
  };

  if (input.benchmarkId === "single-element-creation") {
    benchmarkResult = checkSingleElement(input.prompt, input.finalState);
  } else if (input.benchmarkId === "security-accessibility-audit") {
    benchmarkResult = checkAudit(input.initialState, input.finalState);
  }

  const buildResult = await validateEmittedProjectBuild(input.finalState);

  return {
    passed: benchmarkResult.passed && buildResult.typecheckPassed && buildResult.buildPassed,
    partial: benchmarkResult.partial,
    benchmarkPassed: benchmarkResult.benchmarkPassed,
    typecheckPassed: buildResult.typecheckPassed,
    buildPassed: buildResult.buildPassed,
    message: benchmarkResult.message,
    details: {
      benchmark: benchmarkResult.details,
      build: buildResult.details
    }
  };
}