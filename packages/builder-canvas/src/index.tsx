"use client";

import { useEffect, useMemo, useState } from "react";
import type { ReactElement } from "react";

export interface CanvasHostProps {
  iframeUrl: string;
}

export function CanvasHost({ iframeUrl }: CanvasHostProps): ReactElement {
  return (
    <div style={{ position: "relative", height: "100%", width: "100%", borderRadius: 16, overflow: "hidden" }}>
      <iframe
        title="builder-canvas"
        src={iframeUrl}
        style={{ border: 0, height: "100%", width: "100%", display: "block" }}
        sandbox="allow-same-origin allow-scripts"
      />
    </div>
  );
}

export interface CanvasPreviewProps {
  projectId?: string;
}

type WorkspaceSnapshot = {
  code: string;
  ir: string | null;
  irError: string | null;
  projectId: string;
  collaborators: Array<{ clientId: number; state: unknown }>;
};

export function CanvasPreview({ projectId }: CanvasPreviewProps): ReactElement {
  const [snapshot, setSnapshot] = useState<WorkspaceSnapshot | null>(null);

  useEffect(() => {
    const listener = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) {
        return;
      }

      const payload = event.data as { type?: string; snapshot?: WorkspaceSnapshot } | undefined;
      if (payload?.type === "builder-sync" && payload.snapshot) {
        setSnapshot(payload.snapshot);
      }
    };

    window.addEventListener("message", listener);
    return () => window.removeEventListener("message", listener);
  }, []);

  const summary = useMemo(() => {
    if (!snapshot?.ir) {
      return null;
    }

    try {
      const parsed = JSON.parse(snapshot.ir) as { name?: string; root?: { tag?: string } };
      return parsed.name ?? parsed.root?.tag ?? null;
    } catch {
      return null;
    }
  }, [snapshot?.ir]);

  return (
    <section
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        padding: 24,
        background:
          "radial-gradient(circle at 20% 20%, rgba(79, 209, 197, 0.26), rgba(255, 248, 232, 0.95) 42%), linear-gradient(135deg, #f7fffd 0%, #f8f5ff 100%)"
      }}
    >
      <article
        style={{
          width: "min(640px, 94vw)",
          borderRadius: 24,
          border: "1px solid rgba(16, 42, 67, 0.2)",
          background: "rgba(255, 255, 255, 0.86)",
          padding: "28px 24px",
          boxShadow: "0 22px 48px rgba(16, 42, 67, 0.18)"
        }}
      >
        <p style={{ margin: 0, opacity: 0.65, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase" }}>
          Live Canvas
        </p>
        <h1 style={{ margin: "10px 0 8px", fontSize: 34, lineHeight: 1.1 }}>Builder Preview Surface</h1>
        <p style={{ margin: 0, opacity: 0.85, lineHeight: 1.55 }}>
          {snapshot
            ? `Project ${projectId ?? snapshot.projectId} is synced. ${snapshot.collaborators.length} collaborator(s) are visible.`
            : "Waiting for a workspace sync from the parent window."}
        </p>

        <div
          style={{
            marginTop: 20,
            borderRadius: 20,
            border: "1px solid rgba(16, 42, 67, 0.12)",
            padding: 18,
            background: "linear-gradient(135deg, rgba(18, 35, 60, 0.04), rgba(81, 182, 161, 0.08))"
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, marginBottom: 12 }}>
            <strong style={{ fontSize: 13, textTransform: "uppercase", letterSpacing: "0.12em" }}>IR Summary</strong>
            <span style={{ fontSize: 12, opacity: 0.65 }}>{snapshot?.collaborators.length ?? 0} peers</span>
          </div>
          <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 10 }}>{summary ?? "No parsed structure yet"}</div>
          <pre
            style={{
              margin: 0,
              maxHeight: 220,
              overflow: "auto",
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
              fontSize: 12,
              lineHeight: 1.6
            }}
          >
            {snapshot?.irError ?? snapshot?.ir ?? "The preview will mirror the shared document once the editor starts typing."}
          </pre>
        </div>
      </article>
    </section>
  );
}
