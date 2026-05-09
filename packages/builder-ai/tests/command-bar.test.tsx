// @vitest-environment jsdom

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach } from "vitest";
import { describe, expect, it, vi } from "vitest";
import { CommandBar } from "../src/command-bar";
import { cleanup } from "@testing-library/react";

afterEach(() => {
  cleanup();
});

const generatedNode = {
  id: "ai-feature",
  type: "element" as const,
  tag: "section",
  styles: {},
  props: {},
  children: []
};

describe("CommandBar", () => {
  it("opens with Ctrl+K and submits prompt", async () => {
    const user = userEvent.setup();
    const generate = vi.fn().mockResolvedValue(generatedNode);
    const onInsert = vi.fn();

    render(<CommandBar designTokens={{}} onInsert={onInsert} generate={generate} />);

    fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    expect(screen.getByRole("dialog")).toBeTruthy();

    await user.type(screen.getByLabelText("Prompt"), "Create a feature section");
    await user.click(screen.getByRole("button", { name: "Generate" }));

    await waitFor(() => expect(generate).toHaveBeenCalledWith("Create a feature section", {}));

    await user.click(screen.getByRole("button", { name: "Insert Into Page" }));
    expect(onInsert).toHaveBeenCalledWith(generatedNode);
  });

  it("opens with Cmd+K", () => {
    render(<CommandBar designTokens={{}} onInsert={() => {}} generate={vi.fn()} />);
    fireEvent.keyDown(window, { key: "k", metaKey: true });
    expect(screen.getByRole("dialog")).toBeTruthy();
  });
});
