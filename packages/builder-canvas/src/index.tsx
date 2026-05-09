import React from "react";

export interface CanvasHostProps {
  iframeUrl: string;
}

export function CanvasHost({ iframeUrl }: CanvasHostProps): React.JSX.Element {
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

export function CanvasPreview(): React.JSX.Element {
  return (
    <section
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        background:
          "radial-gradient(circle at 20% 20%, rgba(79, 209, 197, 0.24), rgba(255, 248, 232, 0.95) 40%), linear-gradient(135deg, #f5fffd 0%, #f9f4ff 100%)"
      }}
    >
      <article
        style={{
          width: "min(560px, 90vw)",
          borderRadius: 24,
          border: "1px solid rgba(16, 42, 67, 0.2)",
          background: "rgba(255, 255, 255, 0.86)",
          padding: "28px 24px",
          boxShadow: "0 22px 48px rgba(16, 42, 67, 0.18)"
        }}
      >
        <p style={{ margin: 0, opacity: 0.65, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase" }}>
          Canvas Placeholder
        </p>
        <h1 style={{ margin: "10px 0 8px", fontSize: 34, lineHeight: 1.1 }}>Builder Preview Surface</h1>
        <p style={{ margin: 0, opacity: 0.85, lineHeight: 1.55 }}>
          This static preview route is the initial sandbox target. Live Vite preview and instrumentation bridge will plug
          in during the next cycle.
        </p>
        <button
          type="button"
          style={{
            marginTop: 20,
            border: 0,
            borderRadius: 999,
            padding: "12px 18px",
            background: "#102a43",
            color: "#fff",
            fontWeight: 700,
            cursor: "pointer"
          }}
        >
          Primary CTA
        </button>
      </article>
    </section>
  );
}
