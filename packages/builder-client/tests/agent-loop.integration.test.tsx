// @vitest-environment jsdom

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import * as Y from "yjs";
import { afterEach, describe, expect, it, vi } from "vitest";
import { WorkspaceShell } from "../app/workspace-shell";

vi.mock("@builder/agent", () => {
  return {
    runAgentLoop: vi.fn().mockResolvedValue({
      ok: true,
      validation: { passed: true, message: "Agent loop finished." },
      finalState: {
        projectId: "agent-project",
        code: "export default function Page() { return <main><button>Subscribe</button></main>; }",
        ir: {
          id: "page-id",
          name: "Page",
          route: "/",
          meta: {},
          root: {
            id: "root",
            type: "element",
            tag: "main",
            styles: {},
            props: {},
            children: []
          }
        },
        issues: []
      },
      stepLog: [
        {
          phase: "plan",
          status: "success",
          message: "Planned 1 step."
        },
        {
          phase: "report",
          status: "success",
          message: "Agent loop finished."
        }
      ]
    })
  };
});

vi.mock("@builder/collab", () => {
  const docs = new Map<string, Y.Doc>();

  return {
    useYjsDoc: (projectId: string) => {
      if (!docs.has(projectId)) {
        const doc = new Y.Doc();
        doc.getMap("workspace");
        doc.getText(`source:${projectId}:app/page.tsx`);
        docs.set(projectId, doc);
      }

      return docs.get(projectId) as Y.Doc;
    },
    useSharedObject: (doc: Y.Doc, key: string) => doc.getMap(key),
    useAwareness: () => ({ connected: true, states: [] as unknown[] })
  };
});

vi.mock("@builder/ide", () => {
  return {
    IdeShell: () => <div>IDE Mock</div>
  };
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("WorkspaceShell agent loop", () => {
  it("runs the agent loop and renders the step log", async () => {
    const user = userEvent.setup();
    vi.spyOn(window, "prompt").mockReturnValue("Create a blue button that says Subscribe.");

    render(<WorkspaceShell projectId="agent-project" />);

    await user.click(screen.getByRole("button", { name: "Run Agent" }));

    await waitFor(() => {
      expect(screen.getByText("Agent Step Log")).toBeTruthy();
    });

    expect(screen.getByText(/Planned 1 step/)).toBeTruthy();
    expect(screen.getByLabelText("Agent step log").textContent).toContain("Agent loop finished.");
  });
});