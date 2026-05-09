"use client";

import { useEffect, useMemo, useState } from "react";
import { IdeShell } from "@builder/ide";

type ViewMode = "canvas" | "split" | "code";

const MODE_LABELS: Record<ViewMode, string> = {
  canvas: "Canvas Focus",
  split: "Split View",
  code: "Code Focus"
};

const PREVIEW_URL = "/preview";

export function WorkspaceShell() {
  const [mode, setMode] = useState<ViewMode>("split");
  const shortcutHelp = useMemo(
    () => ["Alt+1 Canvas", "Alt+2 Split", "Alt+3 Code"].join("  |  "),
    []
  );

  useEffect(() => {
    const listener = (event: KeyboardEvent) => {
      if (!event.altKey) {
        return;
      }

      if (event.key === "1") {
        setMode("canvas");
      } else if (event.key === "2") {
        setMode("split");
      } else if (event.key === "3") {
        setMode("code");
      }
    };

    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, []);

  return (
    <main className="workspace-root">
      <header className="workspace-header">
        <div>
          <p className="workspace-kicker">Phase 1 Workspace</p>
          <h1 className="workspace-title">WebBuilder Studio</h1>
        </div>
        <div className="workspace-controls" role="toolbar" aria-label="Workspace mode switcher">
          <ModeButton mode={mode} target="canvas" onSelect={setMode} />
          <ModeButton mode={mode} target="split" onSelect={setMode} />
          <ModeButton mode={mode} target="code" onSelect={setMode} />
        </div>
      </header>

      <p className="workspace-status">
        Mode: <strong>{MODE_LABELS[mode]}</strong>
        <span>{shortcutHelp}</span>
      </p>

      {mode === "split" && (
        <section className="workspace-grid workspace-grid-split">
          <CanvasPanel />
          <CodePanel />
        </section>
      )}

      {mode === "canvas" && (
        <section className="workspace-grid workspace-grid-canvas-only">
          <CanvasPanel />
        </section>
      )}

      {mode === "code" && (
        <section className="workspace-grid workspace-grid-code-only">
          <CodePanel />
        </section>
      )}
    </main>
  );
}

function CanvasPanel() {
  return (
    <article className="workspace-panel">
      <h2>Canvas</h2>
      <div className="workspace-frame-wrap">
        <iframe
          title="Builder Preview"
          src={PREVIEW_URL}
          sandbox="allow-same-origin allow-scripts"
          className="workspace-frame"
        />
      </div>
    </article>
  );
}

function CodePanel() {
  return (
    <article className="workspace-panel">
      <h2>Code</h2>
      <div className="workspace-ide-wrap">
        <IdeShell projectName="starter-project" />
      </div>
    </article>
  );
}

function ModeButton({
  mode,
  target,
  onSelect
}: {
  mode: ViewMode;
  target: ViewMode;
  onSelect: (next: ViewMode) => void;
}) {
  return (
    <button
      type="button"
      className={mode === target ? "workspace-btn workspace-btn-active" : "workspace-btn"}
      onClick={() => onSelect(target)}
    >
      {MODE_LABELS[target]}
    </button>
  );
}
