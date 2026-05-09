import { describe, expect, it } from "vitest";
import type { IRNode } from "../../builder-ir/dist/src/types.js";
import { hashBlock, signBlock, verifyBlock } from "../src/integrity";

const sampleNode: IRNode = {
  id: "root",
  type: "element",
  tag: "div",
  styles: {},
  props: { className: "card" },
  children: [
    {
      id: "text-1",
      type: "text",
      content: "Hello",
      styles: {},
    },
  ],
};

describe("block integrity", () => {
  it("hashes deterministically", () => {
    const a = hashBlock(sampleNode);
    const b = hashBlock({ ...sampleNode, props: { className: "card" } });
    expect(a).toBe(b);
  });

  it("signs and verifies block package", () => {
    const pkg = signBlock(sampleNode, "alice");
    expect(verifyBlock(pkg)).toBe(true);
  });

  it("detects tampering", () => {
    const pkg = signBlock(sampleNode, "alice");
    const tampered = {
      ...pkg,
      irNode: {
        ...pkg.irNode,
        props: { className: "changed" },
      },
    };
    expect(verifyBlock(tampered)).toBe(false);
  });
});
