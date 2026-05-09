// @vitest-environment jsdom

import React from "react";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import * as Y from "yjs";
import { afterEach, describe, expect, it, vi } from "vitest";
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

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("WorkspaceShell export + deploy", () => {
  it("calls export endpoint and triggers file download", async () => {
    const user = userEvent.setup();
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
    const fetchSpy = vi.fn().mockResolvedValue(
      new Response(new Blob(["zip"], { type: "application/zip" }), {
        status: 200,
        headers: { "content-type": "application/zip" }
      })
    );

    vi.stubGlobal("fetch", fetchSpy);
    const createObjectUrlSpy = vi.fn(() => "blob:export");
    const revokeObjectUrlSpy = vi.fn();
    vi.stubGlobal("URL", Object.assign(URL, {
      createObjectURL: createObjectUrlSpy,
      revokeObjectURL: revokeObjectUrlSpy
    }));

    render(<WorkspaceShell projectId="export-project" />);

    await user.click(screen.getByRole("button", { name: "Export" }));

    await waitFor(() => expect(fetchSpy).toHaveBeenCalledWith("/api/export", expect.any(Object)));
    expect(clickSpy).toHaveBeenCalled();
    expect(createObjectUrlSpy).toHaveBeenCalled();
    expect(revokeObjectUrlSpy).toHaveBeenCalledWith("blob:export");
  });

  it("runs deploy flow and shows live URL after polling", async () => {
    const user = userEvent.setup();
    const fetchSpy = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            deploymentId: "dep_1",
            status: "building",
            readyState: "BUILDING",
            liveUrl: null
          }),
          { status: 200, headers: { "content-type": "application/json" } }
        )
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            deploymentId: "dep_1",
            status: "ready",
            readyState: "READY",
            liveUrl: "https://example.vercel.app"
          }),
          { status: 200, headers: { "content-type": "application/json" } }
        )
      );

    vi.stubGlobal("fetch", fetchSpy);
    const realSetTimeout = window.setTimeout.bind(window);
    vi.spyOn(window, "setTimeout").mockImplementation(((handler: TimerHandler) => {
      return realSetTimeout(handler, 0);
    }) as typeof window.setTimeout);

    render(<WorkspaceShell projectId="deploy-project" />);

    await user.click(screen.getByRole("button", { name: "Deploy to Vercel" }));

    await waitFor(() => {
      const liveLink = screen.getByRole("link", { name: "Open Live URL" });
      expect(liveLink.getAttribute("href")).toBe("https://example.vercel.app");
    });

    expect(fetchSpy).toHaveBeenCalledTimes(2);
    expect(fetchSpy).toHaveBeenNthCalledWith(1, "/api/vercel/deploy", expect.any(Object));
    expect(fetchSpy).toHaveBeenNthCalledWith(2, "/api/vercel/deploy?id=dep_1", expect.any(Object));
  });
});
