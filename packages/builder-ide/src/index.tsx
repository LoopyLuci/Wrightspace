"use client";

import type { ReactElement } from "react";

export interface IdeShellProps {
  projectName: string;
  code: string;
  connected: boolean;
  collaboratorCount: number;
  irError: string | null;
  irSnapshot: string | null;
  onCodeChange: (nextCode: string) => void;
}
 
export function IdeShell({
  projectName,
  code,
  connected,
  collaboratorCount,
  irError,
  irSnapshot,
  onCodeChange
}: IdeShellProps): ReactElement {
  return (
    <section
      style={{
        display: "grid",
        gap: 16,
        height: "100%",
        width: "100%",
        padding: 16,
        background:
          "linear-gradient(180deg, rgba(10, 18, 32, 0.96), rgba(11, 22, 38, 0.96)), radial-gradient(circle at top left, rgba(65, 178, 255, 0.16), transparent 42%)",
        color: "#ecf4ff"
      }}
    >
      <header style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "baseline" }}>
        <div>
          <p style={{ margin: 0, fontSize: 12, letterSpacing: "0.16em", textTransform: "uppercase", opacity: 0.65 }}>
            IDE
          </p>
          <h2 style={{ margin: "4px 0 0", fontSize: 18 }}>Project {projectName}</h2>
        </div>
        <div style={{ textAlign: "right", fontSize: 12, opacity: 0.8 }}>
          <div>{connected ? "Connected" : "Offline"}</div>
          <div>{collaboratorCount} collaborator{collaboratorCount === 1 ? "" : "s"}</div>
        </div>
      </header>

      <label style={{ display: "grid", gap: 10, flex: 1, minHeight: 0 }}>
        <span style={{ fontSize: 12, letterSpacing: "0.14em", textTransform: "uppercase", opacity: 0.7 }}>Source</span>
        <textarea
          value={code}
          onChange={(event) => onCodeChange(event.target.value)}
          spellCheck={false}
          style={{
            flex: 1,
            minHeight: 280,
            resize: "none",
            borderRadius: 18,
            border: "1px solid rgba(148, 190, 255, 0.24)",
            background: "rgba(4, 10, 20, 0.72)",
            color: "#f5fbff",
            padding: 16,
            fontFamily: '"SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace',
            fontSize: 13,
            lineHeight: 1.6,
            boxShadow: "inset 0 1px 0 rgba(255, 255, 255, 0.06)"
          }}
        />
      </label>

      <section
        style={{
          display: "grid",
          gap: 12,
          borderRadius: 18,
          padding: 16,
          background: "rgba(255, 255, 255, 0.04)",
          border: "1px solid rgba(148, 190, 255, 0.16)"
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
          <span style={{ fontSize: 12, letterSpacing: "0.14em", textTransform: "uppercase", opacity: 0.72 }}>
            Shared IR Snapshot
          </span>
          <span style={{ fontSize: 12, opacity: 0.7 }}>Awareness state mirrors to the preview iframe</span>
        </div>
        <pre
          style={{
            margin: 0,
            maxHeight: 220,
            overflow: "auto",
            fontSize: 12,
            lineHeight: 1.6,
            whiteSpace: "pre-wrap",
            wordBreak: "break-word"
          }}
        >
          {String(irSnapshot ?? irError ?? "Waiting for synchronized input...")}
        </pre>
      </section>
    </section>
  );
}
