// @vitest-environment jsdom

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import * as Y from "yjs";
import { describe, expect, it, vi } from "vitest";
import { WorkspaceShell } from "../app/workspace-shell";

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

describe("WorkspaceShell AI command bar", () => {
  it("opens on Ctrl+K and submit triggers AI endpoint", async () => {
    const user = userEvent.setup();
    const fetchSpy = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          irNode: {
            id: "ai-node",
            type: "element",
            tag: "section",
            styles: {},
            props: {},
            children: []
          }
        }),
        {
          status: 200,
          headers: { "content-type": "application/json" }
        }
      )
    );

    vi.stubGlobal("fetch", fetchSpy);

    render(<WorkspaceShell projectId="integration-project" />);

    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    expect(screen.getByRole("dialog")).toBeTruthy();

    await user.type(screen.getByLabelText("Prompt"), "Generate a pricing section");
    await user.click(screen.getByRole("button", { name: "Generate" }));

    await waitFor(() => expect(fetchSpy).toHaveBeenCalledOnce());

    const requestInit = fetchSpy.mock.calls[0]?.[1] as RequestInit;
    const body = JSON.parse(String(requestInit.body));
    expect(body.prompt).toBe("Generate a pricing section");
  });
});
