import * as Y from "yjs";
import { generateProject } from "../../builder-ir/dist/src/react-emitter.js";
import { parsePageIR } from "../../builder-ir/dist/src/reverse-parser.js";
import type { PageIR, ProjectIR } from "../../builder-ir/dist/src/types.js";

export type SyncMode = "strict" | "loose" | "manual";

export interface SyncManager {
  start(): void;
  stop(): void;
  getMode(): SyncMode;
  setMode(mode: SyncMode): void;
  syncNow(): void;
}

export const SYNC_ORIGIN = Symbol("builder-sync");
export const EDITOR_ORIGIN = Symbol("builder-sync-editor");
export const CANVAS_ORIGIN = Symbol("builder-sync-canvas");

const WORKSPACE_KEY = "workspace";
const SOURCE_FILE_NAME = "app/page.tsx";

type WorkspaceState = Y.Map<string>;

type QueueEntry =
  | { kind: "source"; snapshot: string }
  | { kind: "ir"; snapshot: string };

function getWorkspace(doc: Y.Doc): WorkspaceState {
  return doc.getMap(WORKSPACE_KEY) as WorkspaceState;
}

export function getSourceTextKey(projectId: string): string {
  return `source:${projectId}:${SOURCE_FILE_NAME}`;
}

export function getSourceText(doc: Y.Doc, projectId: string): Y.Text {
  return doc.getText(getSourceTextKey(projectId));
}

export function readYText(text: Y.Text): string {
  return text.toString();
}

export function setYText(text: Y.Text, nextValue: string, origin: unknown = SYNC_ORIGIN): void {
  const currentValue = text.toString();
  if (currentValue === nextValue) {
    return;
  }

  text.doc?.transact(() => {
    text.delete(0, text.length);
    text.insert(0, nextValue);
  }, origin);
}

function stripCustomRegions(code: string): string {
  return code.replace(/\/\/ @builder:region [\w-]+[\r\n]+([\s\S]*?)[\r\n]+\/\/ @builder:end[\r\n]*/g, "");
}

function extractCustomRegions(code: string): Record<string, string> {
  const regions: Record<string, string> = {};
  const regionRegex = /\/\/ @builder:region ([\w-]+)[\r\n]+([\s\S]*?)[\r\n]+\/\/ @builder:end/g;
  let match: RegExpExecArray | null;

  while ((match = regionRegex.exec(code))) {
    const [, label, content] = match;
    regions[label] = content;
  }

  return regions;
}

function stripCustomCodeFromValue(value: unknown): string {
  return JSON.stringify(value, (key, currentValue) => (key === "customCode" ? undefined : currentValue));
}

function extractPageIR(value: string | null | undefined): PageIR | null {
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as PageIR;
  } catch {
    return null;
  }
}

function buildProjectIR(page: PageIR): ProjectIR {
  return {
    schemaVersion: "1.0.0",
    framework: "react",
    designTokens: {},
    pages: [page],
    components: {},
    assets: {}
  };
}

function applyCustomRegions(page: PageIR, sourceCode: string): PageIR {
  const customRegions = extractCustomRegions(sourceCode);
  if (Object.keys(customRegions).length === 0) {
    return page;
  }

  return {
    ...page,
    root: {
      ...page.root,
      customCode: customRegions
    }
  };
}

function generatePageCode(page: PageIR, sourceCode: string): string {
  const mergedPage = applyCustomRegions(page, sourceCode);
  const generated = generateProject(buildProjectIR(mergedPage))[SOURCE_FILE_NAME];

  if (!generated) {
    return "";
  }

  const beforeRegions = extractCustomRegions(sourceCode);
  const afterRegions = extractCustomRegions(generated);

  for (const [label, content] of Object.entries(beforeRegions)) {
    if (afterRegions[label] !== content) {
      throw new Error(`custom region ${label} was not preserved verbatim`);
    }
  }

  return generated;
}

export class YjsSyncManager implements SyncManager {
  private readonly workspace: WorkspaceState;
  private readonly sourceText: Y.Text;
  private mode: SyncMode = "strict";
  private started = false;
  private readonly queue: QueueEntry[] = [];
  private readonly onSourceUpdate = (event: Y.YTextEvent) => {
    if (event.transaction.origin === SYNC_ORIGIN) {
      return;
    }

    const snapshot = this.sourceText.toString();
    this.workspace.set("code", snapshot);
    this.enqueue({ kind: "source", snapshot });
  };
  private readonly onWorkspaceUpdate = (event: Y.YMapEvent<string>) => {
    if (event.transaction.origin === SYNC_ORIGIN) {
      return;
    }

    if (!event.keysChanged.has("ir")) {
      return;
    }

    const snapshot = this.workspace.get("ir") ?? "";
    this.enqueue({ kind: "ir", snapshot });
  };

  constructor(private readonly doc: Y.Doc, private readonly projectId: string) {
    this.workspace = getWorkspace(doc);
    this.sourceText = getSourceText(doc, projectId);
  }

  start(): void {
    if (this.started) {
      return;
    }

    this.started = true;
    if (!this.workspace.has("syncMode")) {
      this.workspace.set("syncMode", this.mode);
    } else {
      const currentMode = this.workspace.get("syncMode");
      if (currentMode === "strict" || currentMode === "loose" || currentMode === "manual") {
        this.mode = currentMode;
      }
    }

    this.sourceText.observe(this.onSourceUpdate);
    this.workspace.observe(this.onWorkspaceUpdate);

    const currentSource = this.sourceText.toString();
    const currentIr = this.workspace.get("ir") ?? "";

    if (currentSource.trim().length === 0 && currentIr) {
      this.enqueue({ kind: "ir", snapshot: currentIr });
    } else if (currentSource.trim().length > 0) {
      this.enqueue({ kind: "source", snapshot: currentSource });
    }

    if (this.mode === "strict") {
      this.flushQueue();
    }
  }

  stop(): void {
    if (!this.started) {
      return;
    }

    this.started = false;
    this.sourceText.unobserve(this.onSourceUpdate);
    this.workspace.unobserve(this.onWorkspaceUpdate);
    this.queue.length = 0;
  }

  getMode(): SyncMode {
    return this.mode;
  }

  setMode(mode: SyncMode): void {
    this.mode = mode;
    this.workspace.set("syncMode", mode);

    if (this.mode === "strict") {
      this.flushQueue();
    }
  }

  syncNow(): void {
    this.flushQueue();
  }

  private enqueue(entry: QueueEntry): void {
    if (this.mode === "strict") {
      this.processEntry(entry);
      return;
    }

    this.queue.push(entry);
  }

  private flushQueue(): void {
    while (this.queue.length > 0) {
      const entry = this.queue.shift();
      if (entry) {
        this.processEntry(entry);
      }
    }
  }

  private processEntry(entry: QueueEntry): void {
    if (entry.kind === "source") {
      this.processSourceSnapshot(entry.snapshot);
      return;
    }

    this.processIrSnapshot(entry.snapshot);
  }

  private processSourceSnapshot(snapshot: string): void {
    this.workspace.set("code", snapshot);

    try {
      const parsed = parsePageIR(snapshot);
      const currentPageIR = extractPageIR(this.workspace.get("ir"));

      if (!currentPageIR || stripCustomCodeFromValue(currentPageIR) !== stripCustomCodeFromValue(parsed)) {
        this.workspace.set("ir", JSON.stringify(parsed, null, 2));
      }

      if (this.workspace.has("irError")) {
        this.workspace.delete("irError");
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      this.workspace.set("irError", message);
    }
  }

  private processIrSnapshot(snapshot: string): void {
    const page = extractPageIR(snapshot);
    if (!page) {
      this.workspace.set("irError", "invalid IR payload");
      return;
    }

    try {
      const generated = generatePageCode(page, this.sourceText.toString());
      setYText(this.sourceText, generated, SYNC_ORIGIN);
      this.workspace.set("code", generated);

      if (this.workspace.has("irError")) {
        this.workspace.delete("irError");
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      this.workspace.set("irError", message);
    }
  }
}

export function createSyncManager(doc: Y.Doc, projectId: string): SyncManager {
  return new YjsSyncManager(doc, projectId);
}