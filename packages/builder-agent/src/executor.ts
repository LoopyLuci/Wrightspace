import * as Y from "yjs";
import { createSyncManager, EDITOR_ORIGIN, getSourceText, setYText } from "@builder/sync";
import { parsePageIR } from "../../builder-ir/dist/src/reverse-parser.js";
import type { ElementNode, IRNode, PageIR, TextNode } from "../../builder-ir/dist/src/types.js";
import { validatePageIR } from "../../builder-ir/dist/src/validator.js";
import type { AgentIssue, AgentProjectState, AgentStep } from "./types";

const WORKSPACE_KEY = "workspace";

function createEmptyPageIR(projectId: string): PageIR {
  return {
    id: `${projectId}-page`,
    name: "Page",
    route: "/",
    meta: {},
    state: [],
    root: {
      id: `${projectId}-root`,
      type: "element",
      tag: "main",
      styles: {},
      props: {},
      children: []
    }
  };
}

export function createInitialProjectState(input: {
  projectId: string;
  initialCode?: string;
  initialIrSnapshot?: string | null;
}): AgentProjectState {
  const parsedIr = input.initialIrSnapshot
    ? validatePageIR(JSON.parse(input.initialIrSnapshot))
    : input.initialCode
      ? validatePageIR(parsePageIR(input.initialCode))
      : createEmptyPageIR(input.projectId);

  return {
    projectId: input.projectId,
    code: input.initialCode ?? "",
    ir: parsedIr,
    issues: []
  };
}

function buildButtonNode(label: string, color: string): ElementNode {
  const textNode: TextNode = {
    id: `agent-text-${label.toLowerCase().replace(/\s+/g, "-")}`,
    type: "text",
    content: label,
    styles: {
      color: { value: "white" },
      fontWeight: { value: "700" }
    }
  };

  return {
    id: `agent-button-${label.toLowerCase().replace(/\s+/g, "-")}`,
    type: "element",
    tag: "button",
    styles: {
      backgroundColor: { value: color === "blue" ? "blue" : "var(--color-accent)" },
      padding: { value: "1rem 2rem" },
      borderRadius: { value: "999px" }
    },
    props: {
      type: "button"
    },
    accessibility: {
      role: "button",
      label
    },
    children: [textNode]
  };
}

function insertNodeAfterHeading(page: PageIR, nextNode: IRNode): PageIR {
  if (page.root.type !== "element") {
    throw new Error("Page root must be an element to insert children");
  }

  const children = [...page.root.children];
  const headingIndex = children.findIndex((child) => child.type === "element" && ["h1", "h2", "h3"].includes(child.tag));
  const insertAt = headingIndex >= 0 ? headingIndex + 1 : children.length;
  children.splice(insertAt, 0, nextNode);

  return {
    ...page,
    root: {
      ...page.root,
      children
    }
  };
}

function analyzeSecurityAndAccessibility(projectState: AgentProjectState): AgentIssue[] {
  const issues: AgentIssue[] = [];
  const code = projectState.code;

  if (/target=\"_blank\"/.test(code) && !/rel=\"[^\"]*noreferrer/.test(code)) {
    issues.push({
      code: "unsafe-external-link",
      severity: "high",
      message: "External link opens in a new tab without rel=noreferrer.",
      suggestion: "Add rel=\"noreferrer\" to external links that use target=\"_blank\"."
    });
  }

  if (/<input[^>]+placeholder=/.test(code) && !/<label/.test(code)) {
    issues.push({
      code: "missing-form-label",
      severity: "high",
      message: "Form inputs rely on placeholders without explicit labels.",
      suggestion: "Add visible or programmatic labels for each form control."
    });
  }

  if (/role=\"button\"/.test(code) && !/<button/.test(code)) {
    issues.push({
      code: "non-semantic-button",
      severity: "medium",
      message: "Interactive control uses role=button instead of a semantic button element.",
      suggestion: "Replace role-based button divs with a real <button type=\"button\"> element."
    });
  }

  if (/tabIndex=\{0\}/.test(code)) {
    issues.push({
      code: "keyboard-navigation-risk",
      severity: "medium",
      message: "Custom tab stop detected and should be reviewed for semantic keyboard handling.",
      suggestion: "Prefer semantic interactive elements over manually managed keyboard navigation."
    });
  }

  return issues;
}

function applyWithSync(projectState: AgentProjectState, nextPage: PageIR): AgentProjectState {
  const doc = new Y.Doc();
  const workspace = doc.getMap(WORKSPACE_KEY);
  const sourceText = getSourceText(doc, projectState.projectId);
  const syncManager = createSyncManager(doc, projectState.projectId);

  setYText(sourceText, projectState.code, EDITOR_ORIGIN);
  workspace.set("ir", JSON.stringify(projectState.ir));
  syncManager.start();

  doc.transact(() => {
    workspace.set("ir", JSON.stringify(nextPage, null, 2));
  }, EDITOR_ORIGIN);

  syncManager.syncNow();

  const irError = workspace.get("irError");
  if (typeof irError === "string" && irError.length > 0) {
    syncManager.stop();
    throw new Error(irError);
  }

  const emittedCode = (workspace.get("code") as string | undefined) ?? sourceText.toString();
  const emittedIr = validatePageIR(JSON.parse(String(workspace.get("ir") ?? JSON.stringify(nextPage))));
  syncManager.stop();

  return {
    ...projectState,
    code: emittedCode,
    ir: emittedIr,
    issues: []
  };
}

function applyCodeSnapshot(projectState: AgentProjectState, nextCode: string): AgentProjectState {
  const nextIr = validatePageIR(parsePageIR(nextCode));
  return {
    ...projectState,
    code: nextCode,
    ir: nextIr,
    issues: []
  };
}

function createMultiPageScaffoldCode(): string {
  return `export default function Page() {
  return (
    <main style={{ padding: "2rem", display: "grid", gap: "1.5rem" }}>
      <nav aria-label="Primary" style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
        <a href="/">Home</a>
        <a href="/pricing">Pricing</a>
        <a href="/contact">Contact</a>
      </nav>
      <section>
        <h1>Acme SaaS</h1>
        <p>Build and launch visual experiences faster.</p>
      </section>
      <section>
        <h2>Pricing</h2>
        <p>Choose a plan that fits your team.</p>
      </section>
      <section>
        <h2>Contact</h2>
        <p>Email hello@example.com to talk to sales.</p>
      </section>
    </main>
  );
}
`;
}

function createResponsiveRefactorCode(): string {
  return `export default function Page() {
  return (
    <main style={{ padding: "2rem" }}>
      <section
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
          gap: "1.5rem",
          alignItems: "center",
          maxWidth: "1000px",
          margin: "0 auto"
        }}
      >
        <div>
          <h1>Build products visually</h1>
          <p>Ship clean React code without rewriting your work.</p>
        </div>
        <img
          src="https://placehold.co/640x420"
          alt="Product preview"
          width={640}
          height={420}
          style={{ width: "100%", height: "auto" }}
        />
      </section>
    </main>
  );
}
`;
}

export function executeStep(projectState: AgentProjectState, step: AgentStep): AgentProjectState {
  if (step.mode === "report") {
    return {
      ...projectState,
      issues: analyzeSecurityAndAccessibility(projectState)
    };
  }

  if (step.metadata?.variant === "button") {
    const label = typeof step.metadata.label === "string" ? step.metadata.label : "Subscribe";
    const color = typeof step.metadata.color === "string" ? step.metadata.color : "accent";
    const nextPage = insertNodeAfterHeading(projectState.ir, buildButtonNode(label, color));
    return applyWithSync(projectState, validatePageIR(nextPage));
  }

  if (step.metadata?.variant === "multi-page-scaffold") {
    return applyCodeSnapshot(projectState, createMultiPageScaffoldCode());
  }

  if (step.metadata?.variant === "responsive-refactor") {
    return applyCodeSnapshot(projectState, createResponsiveRefactorCode());
  }

  return projectState;
}