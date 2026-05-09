import { useCallback, useEffect, useMemo, useState } from "react";
import type { IRNode } from "../../builder-ir/dist/src/types.js";
import { generateComponent, type GenerateComponentOptions } from "./pipeline";

type CommandBarProps = {
  designTokens: Record<string, unknown>;
  onInsert: (node: IRNode) => void;
  title?: string;
  shortcutHint?: string;
  generate?: (prompt: string, designTokens: Record<string, unknown>) => Promise<IRNode>;
  generateOptions?: GenerateComponentOptions;
};

export function CommandBar({
  designTokens,
  onInsert,
  title = "Generate Component",
  shortcutHint = "Ctrl/Cmd+K",
  generate,
  generateOptions
}: CommandBarProps) {
  const [open, setOpen] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<IRNode | null>(null);

  const generateFn = useMemo(
    () => generate ?? ((nextPrompt: string, tokens: Record<string, unknown>) => generateComponent(nextPrompt, tokens, generateOptions)),
    [generate, generateOptions]
  );

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const isOpenShortcut = (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k";
      if (isOpenShortcut) {
        event.preventDefault();
        setOpen(true);
        return;
      }

      if (event.key === "Escape") {
        setOpen(false);
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const onSubmit = useCallback(async () => {
    if (!prompt.trim()) {
      setError("Describe what you want to generate first.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const node = await generateFn(prompt, designTokens);
      setPreview(node);
    } catch (submitError) {
      const message = submitError instanceof Error ? submitError.message : String(submitError);
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [designTokens, generateFn, prompt]);

  const onAccept = useCallback(() => {
    if (!preview) {
      return;
    }

    onInsert(preview);
    setOpen(false);
    setPrompt("");
    setPreview(null);
    setError(null);
  }, [onInsert, preview]);

  return (
    <>
      <button type="button" className="workspace-btn" onClick={() => setOpen(true)} aria-label="Open AI command bar">
        AI Command Bar ({shortcutHint})
      </button>

      {open && (
        <div className="commandbar-backdrop" role="presentation" onClick={() => setOpen(false)}>
          <section
            className="commandbar-modal"
            role="dialog"
            aria-modal="true"
            aria-label={title}
            onClick={(event) => event.stopPropagation()}
          >
            <header className="commandbar-header">
              <h2>{title}</h2>
              <button type="button" className="workspace-btn" onClick={() => setOpen(false)}>
                Close
              </button>
            </header>

            <label className="commandbar-label" htmlFor="builder-ai-prompt">
              Prompt
            </label>
            <textarea
              id="builder-ai-prompt"
              className="commandbar-input"
              placeholder="Example: Build a testimonial card with avatar, quote, and author"
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              rows={4}
            />

            <div className="commandbar-actions">
              <button type="button" className="workspace-btn workspace-btn-active" onClick={() => void onSubmit()} disabled={loading}>
                {loading ? "Generating..." : "Generate"}
              </button>
              <span className="commandbar-shortcut">Shortcut: {shortcutHint}</span>
            </div>

            {error && <p className="commandbar-error">{error}</p>}

            {preview && (
              <div className="commandbar-preview">
                <p className="commandbar-preview-title">Preview Node JSON</p>
                <pre>{JSON.stringify(preview, null, 2)}</pre>
                <button type="button" className="workspace-btn workspace-btn-active" onClick={onAccept}>
                  Insert Into Page
                </button>
              </div>
            )}
          </section>
        </div>
      )}
    </>
  );
}
