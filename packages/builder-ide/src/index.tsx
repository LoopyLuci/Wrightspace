import React from "react";

export interface IdeShellProps {
  projectName: string;
}

export function IdeShell({ projectName }: IdeShellProps): React.JSX.Element {
  return (
    <section style={{ height: "100%", width: "100%", padding: "12px" }}>
      <h2 style={{ fontSize: "14px", margin: 0 }}>IDE: {projectName}</h2>
      <p style={{ opacity: 0.7 }}>Monaco wrapper + file tree + terminal stub lands in Phase 1 Task 3/4.</p>
    </section>
  );
}
