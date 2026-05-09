import { validatePageIR } from "../../builder-ir/dist/src/validator.js";
import { createInitialProjectState, executeStep } from "./executor";
import { createPlan } from "./planner";
import { createSnapshot, restoreSnapshot } from "./rollback";
import type { AgentLoopOptions, AgentLoopResult, AgentProjectState, AgentValidationResult } from "./types";

function defaultValidation(finalState: AgentProjectState): AgentValidationResult {
  validatePageIR(finalState.ir);
  return {
    passed: true,
    benchmarkPassed: true,
    message: "IR validation passed."
  };
}

export async function runAgentLoop(options: AgentLoopOptions): Promise<AgentLoopResult> {
  const stepLog: AgentLoopResult["stepLog"] = [];
  const initialState = createInitialProjectState({
    projectId: options.projectId,
    initialCode: options.initialCode,
    initialIrSnapshot: options.initialIrSnapshot
  });

  const planningStartedAt = Date.now();
  const planResult = await createPlan(options.prompt, {
    benchmarkId: options.benchmarkId,
    irSnapshot: options.initialIrSnapshot
  });
  const plan = planResult.steps;
  const planningDurationMs = Date.now() - planningStartedAt;
  const totalPlanTokens = planResult.tokenCount ?? 0;
  const defaultStepTokenCount = plan.length > 0 ? Math.max(0, Math.round(totalPlanTokens / plan.length)) : 0;

  stepLog.push({
    phase: "plan",
    status: "success",
    message: `Planned ${plan.length} step${plan.length === 1 ? "" : "s"}.`,
    details: {
      source: planResult.source,
      plan
    },
    durationMs: planningDurationMs,
    tokenCount: totalPlanTokens
  });

  let currentState = initialState;
  let lastCleanSnapshot = createSnapshot(initialState);

  try {
    for (const step of plan) {
      const stepStartedAt = Date.now();
      currentState = executeStep(currentState, step);
      const actDurationMs = Date.now() - stepStartedAt;

      const stepTokenCount =
        typeof step.metadata?.tokenCount === "number" ? step.metadata.tokenCount : defaultStepTokenCount;

      const validateStartedAt = Date.now();
      validatePageIR(currentState.ir);
      const validateDurationMs = Date.now() - validateStartedAt;
      lastCleanSnapshot = createSnapshot(currentState);

      stepLog.push({
        phase: "act",
        status: step.mode === "report" ? "partial" : "success",
        message: step.mode === "report" ? "Analyzed current page and recorded issues." : "Applied planned step.",
        stepDescription: step.description,
        details: step.mode === "report" ? currentState.issues : step.expectedDiff,
        durationMs: actDurationMs,
        tokenCount: stepTokenCount
      });

      stepLog.push({
        phase: "validate",
        status: "success",
        message: "IR remained valid after step.",
        stepDescription: step.description,
        durationMs: validateDurationMs,
        tokenCount: stepTokenCount
      });
    }

    const validation = options.validate
      ? await options.validate({
          prompt: options.prompt,
          benchmarkId: options.benchmarkId,
          initialState,
          finalState: currentState,
          stepLog
        })
      : defaultValidation(currentState);

    stepLog.push({
      phase: "report",
      status: validation.passed ? "success" : validation.partial ? "partial" : "error",
      message: validation.message,
      details: validation.details,
      tokenCount: totalPlanTokens
    });

    if (!validation.passed && !validation.partial) {
      const rolledBack = restoreSnapshot(currentState.projectId, lastCleanSnapshot);
      stepLog.push({
        phase: "rollback",
        status: "success",
        message: "Restored the last clean snapshot after validation failure."
      });

      return {
        ok: false,
        stepLog,
        finalState: rolledBack,
        validation,
        error: validation.message
      };
    }

    return {
      ok: true,
      stepLog,
      finalState: currentState,
      validation
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    const rolledBack = restoreSnapshot(currentState.projectId, lastCleanSnapshot);

    stepLog.push({
      phase: "rollback",
      status: "success",
      message: "Execution failed and the last clean snapshot was restored.",
      details: message
    });

    return {
      ok: false,
      stepLog,
      finalState: rolledBack,
      validation: {
        passed: false,
        message
      },
      error: message
    };
  }
}