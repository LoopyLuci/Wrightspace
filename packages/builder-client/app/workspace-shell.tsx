"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import type { RefObject } from "react";
import { runAgentLoop, type AgentLogEntry } from "@builder/agent";
import { CommandBar } from "@builder/ai";
import { IdeShell } from "@builder/ide";
import type { IRNode, PageIR } from "../../builder-ir/dist/src/types.js";
import { useAwareness, useSharedObject, useYjsDoc } from "@builder/collab";
import {
  EDITOR_ORIGIN,
  createSyncManager,
  getSourceText,
  setYText,
  type SyncManager,
  type SyncMode
} from "@builder/sync";

type ViewMode = "canvas" | "split" | "code";

const MODE_LABELS: Record<ViewMode, string> = {
  canvas: "Canvas Focus",
  split: "Split View",
  code: "Code Focus"
};

const PREVIEW_URL = "/preview";
const SYNC_MODE_STORAGE_PREFIX = "builder-sync-mode";

const DEFAULT_CODE = `import React from "react";

export default function Home() {
  return (
    <section data-builder-id="hero-uuid-123" className="hero-section">
      <h1>Hello WebBuilder</h1>
      <p>Collaborative code and canvas stay in sync.</p>
    </section>
  );
}`;

type WorkspaceShellProps = {
  projectId: string;
};

type WorkspaceNotice = {
  kind: "success" | "error";
  message: string;
};

type DeployState = {
  phase: "idle" | "building" | "ready" | "error";
  message: string;
  liveUrl?: string | null;
};

type AgentRunState = {
  prompt: string;
  running: boolean;
  logs: AgentLogEntry[];
};

export function WorkspaceShell({ projectId }: WorkspaceShellProps) {
  const [mode, setMode] = useState<ViewMode>("split");
  const [iframeReady, setIframeReady] = useState(false);
  const [notice, setNotice] = useState<WorkspaceNotice | null>(null);
  const [agentRun, setAgentRun] = useState<AgentRunState>({ prompt: "", running: false, logs: [] });
  const [deployState, setDeployState] = useState<DeployState>({
    phase: "idle",
    message: "Not deployed yet",
    liveUrl: null
  });
  const [exporting, setExporting] = useState(false);
  const [deploying, setDeploying] = useState(false);
  const [syncMode, setSyncMode] = useState<SyncMode>(() => {
    if (typeof window === "undefined") {
      return "strict";
    }

    const storedMode = window.localStorage.getItem(`${SYNC_MODE_STORAGE_PREFIX}:${projectId}`);
    return storedMode === "loose" || storedMode === "manual" ? storedMode : "strict";
  });
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const doc = useYjsDoc(projectId);
  const workspace = useSharedObject(doc, "workspace");
  const awareness = useAwareness(doc);
  const syncManager = useMemo<SyncManager>(() => createSyncManager(doc, projectId), [doc, projectId]);
  const sourceText = useMemo(() => getSourceText(doc, projectId), [doc, projectId]);
  const previewUrl = useMemo(() => `${PREVIEW_URL}?projectId=${encodeURIComponent(projectId)}`, [projectId]);
  const shortcutHelp = useMemo(
    () => ["Alt+1 Canvas", "Alt+2 Split", "Alt+3 Code"].join("  |  "),
    []
  );
  const storageKey = useMemo(() => `${SYNC_MODE_STORAGE_PREFIX}:${projectId}`, [projectId]);
  const designTokens = useMemo<Record<string, unknown>>(() => {
    return {};
  }, []);

  useEffect(() => {
    syncManager.start();
    return () => syncManager.stop();
  }, [syncManager]);

  useEffect(() => {
    syncManager.setMode(syncMode);
    window.localStorage.setItem(storageKey, syncMode);
  }, [storageKey, syncManager, syncMode]);

  useEffect(() => {
    if (sourceText.toString().length === 0 && !workspace.has("code") && !workspace.has("ir")) {
      setYText(sourceText, DEFAULT_CODE, EDITOR_ORIGIN);
    }
  }, [sourceText, workspace]);

  const code = (workspace.get("code") as string | undefined) ?? sourceText.toString();
  const ir = (workspace.get("ir") as string | undefined) ?? null;
  const irError = (workspace.get("irError") as string | undefined) ?? null;
  const collaboratorCount = awareness.states.length;
  const activeCode = code || DEFAULT_CODE;

  useEffect(() => {
    const syncPreview = () => {
      if (!iframeReady) {
        return;
      }

      const frame = iframeRef.current;
      if (!frame?.contentWindow) {
        return;
      }

      frame.contentWindow.postMessage(
        {
          type: "builder-sync",
          snapshot: {
            code: activeCode,
            collaborators: awareness.states,
            ir,
            irError,
            projectId
          }
        },
        window.location.origin
      );
    };

    syncPreview();
  }, [activeCode, awareness.states, iframeReady, ir, irError, projectId]);

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

  useEffect(() => {
    if (!notice) {
      return;
    }

    const timeout = window.setTimeout(() => setNotice(null), 3200);
    return () => window.clearTimeout(timeout);
  }, [notice]);

  const handleInsertGeneratedNode = (node: IRNode) => {
    const irSnapshot = workspace.get("ir") as string | undefined;
    if (!irSnapshot) {
      setNotice({ kind: "error", message: "Cannot insert AI node: workspace IR is empty." });
      return;
    }

    let page: PageIR;
    try {
      page = JSON.parse(irSnapshot) as PageIR;
    } catch {
      setNotice({ kind: "error", message: "Cannot insert AI node: workspace IR is invalid JSON." });
      return;
    }

    if (page.root.type !== "element") {
      setNotice({ kind: "error", message: "Cannot insert AI node: page root does not support children." });
      return;
    }

    const nextPage: PageIR = {
      ...page,
      root: {
        ...page.root,
        children: [...page.root.children, node]
      }
    };

    doc.transact(() => {
      workspace.set("ir", JSON.stringify(nextPage, null, 2));
    }, EDITOR_ORIGIN);

    setNotice({ kind: "success", message: "AI node inserted into the current page." });
  };

  const triggerZipDownload = (blob: Blob, fileName: string) => {
    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = objectUrl;
    anchor.download = fileName;
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    URL.revokeObjectURL(objectUrl);
  };

  const handleExportProject = async () => {
    try {
      setExporting(true);
      const response = await fetch("/api/export", {
        method: "POST",
        headers: {
          "content-type": "application/json"
        },
        body: JSON.stringify({
          projectId,
          code: activeCode,
          irSnapshot: ir
        })
      });

      if (!response.ok) {
        const payload = (await response.json()) as { error?: string };
        throw new Error(payload.error ?? "Export failed");
      }

      const zipBlob = await response.blob();
      triggerZipDownload(zipBlob, `webbuilder-${projectId}.zip`);
      setNotice({ kind: "success", message: "Project exported as a Next.js zip." });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setNotice({ kind: "error", message: `Export failed: ${message}` });
    } finally {
      setExporting(false);
    }
  };

  const handleRunAgent = async () => {
    const prompt = window.prompt("Run agent prompt", "Create a blue button that says Subscribe.");
    if (!prompt || !prompt.trim()) {
      return;
    }

    try {
      setAgentRun({ prompt, running: true, logs: [] });
      const result = await runAgentLoop({
        prompt,
        projectId,
        initialCode: activeCode,
        initialIrSnapshot: ir
      });

      setAgentRun({ prompt, running: false, logs: result.stepLog });

      doc.transact(() => {
        workspace.set("ir", JSON.stringify(result.finalState.ir, null, 2));
        workspace.set("code", result.finalState.code);
      }, EDITOR_ORIGIN);
      setYText(sourceText, result.finalState.code, EDITOR_ORIGIN);

      if (result.ok) {
        setNotice({ kind: "success", message: result.validation.message });
      } else {
        setNotice({ kind: "error", message: result.error ?? result.validation.message });
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setAgentRun((current) => ({ ...current, running: false }));
      setNotice({ kind: "error", message: `Agent run failed: ${message}` });
    }
  };

  const pollDeploymentStatus = async (deploymentId: string) => {
    for (let attempt = 0; attempt < 30; attempt += 1) {
      await new Promise((resolve) => window.setTimeout(resolve, 2000));
      const statusResponse = await fetch(`/api/vercel/deploy?id=${encodeURIComponent(deploymentId)}`, {
        cache: "no-store"
      });

      if (!statusResponse.ok) {
        const payload = (await statusResponse.json()) as { error?: string };
        throw new Error(payload.error ?? "Could not read deployment status");
      }

      const payload = (await statusResponse.json()) as {
        status: "building" | "ready" | "error";
        readyState: string;
        liveUrl?: string | null;
      };

      if (payload.status === "ready") {
        setDeployState({
          phase: "ready",
          message: `Deployment ready (${payload.readyState})`,
          liveUrl: payload.liveUrl ?? null
        });
        setNotice({ kind: "success", message: "Deployment is live on Vercel." });
        return;
      }

      if (payload.status === "error") {
        setDeployState({
          phase: "error",
          message: `Deployment failed (${payload.readyState})`,
          liveUrl: payload.liveUrl ?? null
        });
        setNotice({ kind: "error", message: "Deployment failed on Vercel." });
        return;
      }

      setDeployState({
        phase: "building",
        message: `Building (${payload.readyState})`,
        liveUrl: payload.liveUrl ?? null
      });
    }

    throw new Error("Timed out waiting for Vercel deployment");
  };

  const handleDeployToVercel = async () => {
    try {
      setDeploying(true);
      setDeployState({ phase: "building", message: "Creating deployment", liveUrl: null });

      const response = await fetch("/api/vercel/deploy", {
        method: "POST",
        headers: {
          "content-type": "application/json"
        },
        body: JSON.stringify({
          projectId,
          code: activeCode,
          irSnapshot: ir
        })
      });

      if (!response.ok) {
        const payload = (await response.json()) as { error?: string };
        throw new Error(payload.error ?? "Deployment request failed");
      }

      const payload = (await response.json()) as {
        deploymentId?: string;
        status: "building" | "ready" | "error";
        readyState: string;
        liveUrl?: string | null;
      };

      setDeployState({
        phase: payload.status,
        message: payload.status === "ready" ? "Deployment ready" : `Building (${payload.readyState})`,
        liveUrl: payload.liveUrl ?? null
      });

      if (payload.status === "ready") {
        setNotice({ kind: "success", message: "Deployment is live on Vercel." });
        return;
      }

      if (!payload.deploymentId) {
        throw new Error("Missing deployment id in Vercel response");
      }

      await pollDeploymentStatus(payload.deploymentId);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setDeployState({ phase: "error", message, liveUrl: null });
      setNotice({ kind: "error", message: `Deploy failed: ${message}` });
    } finally {
      setDeploying(false);
    }
  };

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
          <SyncModeButton mode={syncMode} target="strict" onSelect={setSyncMode} />
          <SyncModeButton mode={syncMode} target="loose" onSelect={setSyncMode} />
          <SyncModeButton mode={syncMode} target="manual" onSelect={setSyncMode} />
          <button type="button" className="workspace-btn" onClick={() => syncManager.syncNow()}>
            Sync Now
          </button>
          <button type="button" className="workspace-btn" onClick={() => void handleExportProject()} disabled={exporting || deploying}>
            {exporting ? "Exporting..." : "Export"}
          </button>
          <button
            type="button"
            className={deployState.phase === "ready" ? "workspace-btn workspace-btn-active" : "workspace-btn"}
            onClick={() => void handleDeployToVercel()}
            disabled={deploying || exporting}
          >
            {deploying ? "Deploying..." : "Deploy to Vercel"}
          </button>
          <button type="button" className="workspace-btn" onClick={() => void handleRunAgent()} disabled={agentRun.running || deploying || exporting}>
            {agentRun.running ? "Running Agent..." : "Run Agent"}
          </button>
          <CommandBar designTokens={designTokens} onInsert={handleInsertGeneratedNode} />
        </div>
      </header>

      <p className="workspace-status">
        Mode: <strong>{MODE_LABELS[mode]}</strong>
        <span>
          Sync: <strong>{syncMode[0].toUpperCase() + syncMode.slice(1)}</strong> | {shortcutHelp}
        </span>
        <span>
          Deploy: <strong>{deployState.message}</strong>
          {deployState.liveUrl && (
            <>
              {" "}
              <a href={deployState.liveUrl} target="_blank" rel="noreferrer" className="workspace-link">
                Open Live URL
              </a>
            </>
          )}
        </span>
      </p>

      {notice && (
        <p className={notice.kind === "error" ? "workspace-toast workspace-toast-error" : "workspace-toast workspace-toast-success"}>
          {notice.message}
        </p>
      )}

      {agentRun.logs.length > 0 && (
        <section className="workspace-agent-log" aria-label="Agent step log">
          <div className="workspace-agent-log-header">
            <h2>Agent Step Log</h2>
            <span>{agentRun.prompt}</span>
          </div>
          <ol>
            {agentRun.logs.map((entry, index) => {
              const reportDetails = entry.phase === "report" && entry.details !== undefined
                ? JSON.stringify(entry.details, null, 2)
                : null;

              return (
                <li key={`${entry.phase}-${index}`}>
                  <strong>{entry.phase}</strong>: {entry.message}
                  {entry.stepDescription && <span> ({entry.stepDescription})</span>}
                  {(entry.durationMs !== undefined || entry.tokenCount !== undefined) && (
                    <span>
                      {" "}
                      [
                      {entry.durationMs !== undefined ? `${entry.durationMs}ms` : "n/a"}
                      {", "}
                      {entry.tokenCount !== undefined ? `${entry.tokenCount} tokens` : "n/a"}
                      ]
                    </span>
                  )}
                  {reportDetails ? <pre>{reportDetails}</pre> : null}
                </li>
              );
            })}
          </ol>
        </section>
      )}

      {mode === "split" && (
        <section className="workspace-grid workspace-grid-split">
          <CanvasPanel iframeRef={iframeRef} onLoad={() => setIframeReady(true)} previewUrl={previewUrl} />
          <CodePanel
            collaboratorCount={collaboratorCount}
            code={activeCode}
            connected={awareness.connected}
            irError={irError}
            irSnapshot={ir}
            onCodeChange={(nextCode) => setYText(sourceText, nextCode, EDITOR_ORIGIN)}
            projectId={projectId}
          />
        </section>
      )}

      {mode === "canvas" && (
        <section className="workspace-grid workspace-grid-canvas-only">
          <CanvasPanel iframeRef={iframeRef} onLoad={() => setIframeReady(true)} previewUrl={previewUrl} />
        </section>
      )}

      {mode === "code" && (
        <section className="workspace-grid workspace-grid-code-only">
          <CodePanel
            collaboratorCount={collaboratorCount}
            code={activeCode}
            connected={awareness.connected}
            irError={irError}
            irSnapshot={ir}
            onCodeChange={(nextCode) => setYText(sourceText, nextCode, EDITOR_ORIGIN)}
            projectId={projectId}
          />
        </section>
      )}
    </main>
  );
}

function CanvasPanel({
  iframeRef,
  onLoad,
  previewUrl
}: {
  iframeRef: RefObject<HTMLIFrameElement | null>;
  onLoad: () => void;
  previewUrl: string;
}) {
  return (
    <article className="workspace-panel">
      <h2>Canvas</h2>
      <div className="workspace-frame-wrap">
        <iframe
          title="Builder Preview"
          ref={iframeRef}
          onLoad={onLoad}
          src={previewUrl}
          sandbox="allow-same-origin allow-scripts"
          className="workspace-frame"
        />
      </div>
    </article>
  );
}

function CodePanel({
  code,
  connected,
  collaboratorCount,
  irError,
  irSnapshot,
  onCodeChange,
  projectId
}: {
  code: string;
  connected: boolean;
  collaboratorCount: number;
  irError: string | null;
  irSnapshot: string | null;
  onCodeChange: (nextCode: string) => void;
  projectId: string;
}) {
  return (
    <article className="workspace-panel">
      <h2>Code</h2>
      <div className="workspace-ide-wrap">
        <IdeShell
          code={code}
          collaboratorCount={collaboratorCount}
          connected={connected}
          irError={irError}
          irSnapshot={irSnapshot}
          onCodeChange={onCodeChange}
          projectName={projectId}
        />
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

function SyncModeButton({
  mode,
  target,
  onSelect
}: {
  mode: SyncMode;
  target: SyncMode;
  onSelect: (next: SyncMode) => void;
}) {
  const label = target === "strict" ? "Strict" : target === "loose" ? "Loose" : "Manual";

  return (
    <button
      type="button"
      className={mode === target ? "workspace-btn workspace-btn-active" : "workspace-btn"}
      onClick={() => onSelect(target)}
    >
      {label}
    </button>
  );
}
