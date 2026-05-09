import type { AgentProjectState, AgentSnapshot } from "./types";

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