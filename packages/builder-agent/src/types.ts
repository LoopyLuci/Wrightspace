import type { PageIR } from "../../builder-ir/dist/src/types.js";

export type AgentAction = "create" | "update" | "delete";
export type AgentStepMode = "apply" | "report";
export type AgentSeverity = "low" | "medium" | "high";

export interface AgentIssue {
  code: string;
  severity: AgentSeverity;
  message: string;
  suggestion: string;
}

export interface AgentStep {
  description: string;
  target: string;
  action: AgentAction;
  expectedDiff: string;
  mode?: AgentStepMode;
  metadata?: Record<string, unknown>;
}

export interface AgentProjectState {
  projectId: string;
  code: string;
  ir: PageIR;
  issues: AgentIssue[];
}

export interface AgentSnapshot {
  code: string;
  irSnapshot: string;
  issues: AgentIssue[];
}

export interface AgentLogEntry {
  phase: "plan" | "act" | "validate" | "report" | "rollback";
  status: "success" | "partial" | "error" | "skipped";
  message: string;
  stepDescription?: string;
  details?: unknown;
  durationMs?: number;
  tokenCount?: number;
  stepIndex?: number;
  rollbackSnapshot?: AgentSnapshot;
}

export interface AgentValidationResult {
  passed: boolean;
  partial?: boolean;
  benchmarkPassed?: boolean;
  typecheckPassed?: boolean;
  buildPassed?: boolean;
  message: string;
  details?: unknown;
}

export interface AgentLoopOptions {
  prompt: string;
  projectId: string;
  initialCode?: string;
  initialIrSnapshot?: string | null;
  benchmarkId?: string;
  continueOnError?: boolean;
  validate?: (input: {
    prompt: string;
    benchmarkId?: string;
    initialState: AgentProjectState;
    finalState: AgentProjectState;
    stepLog: AgentLogEntry[];
  }) => Promise<AgentValidationResult> | AgentValidationResult;
}

export interface AgentLoopResult {
  ok: boolean;
  stepLog: AgentLogEntry[];
  finalState: AgentProjectState;
  validation: AgentValidationResult;
  error?: string;
}