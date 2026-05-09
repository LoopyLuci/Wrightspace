import type { AgentProjectState } from "./types";

export interface AgentSnapshot {
  code: string;
  irSnapshot: string;
  issues: AgentProjectState["issues"];
}

export function createSnapshot(state: AgentProjectState): AgentSnapshot {
  return {
    code: state.code,
    irSnapshot: JSON.stringify(state.ir),
    issues: state.issues.map((issue) => ({ ...issue }))
  };
}

export function restoreSnapshot(projectId: string, snapshot: AgentSnapshot): AgentProjectState {
  return {
    projectId,
    code: snapshot.code,
    ir: JSON.parse(snapshot.irSnapshot),
    issues: snapshot.issues.map((issue) => ({ ...issue }))
  };
}