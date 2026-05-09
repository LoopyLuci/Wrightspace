import { describe, expect, it } from "vitest";
import { BlockPackageSchema, RegistryEntrySchema } from "../src/schema";

const validPackage = {
  metadata: {
    id: "card.counter",
    name: "Card Counter",
    description: "Counter card with slots",
    version: "1.2.0",
    author: "builder-team",
    license: "MIT",
    framework: ["next-react", "vite-react"],
    trust: "verified",
    keywords: ["card", "counter"],
    category: "layout",
    createdAt: "2026-05-09T00:00:00.000Z",
    updatedAt: "2026-05-09T00:00:00.000Z",
    dependencies: [{ id: "button.base", version: "1.0.0" }],
  },
  irNode: {
    id: "root",
    type: "element",
    tag: "div",
    styles: {},
    props: {},
    children: [],
  },
  signature: "a".repeat(64),
};

describe("marketplace schema", () => {
  it("accepts valid block package", () => {
    const parsed = BlockPackageSchema.parse(validPackage);
    expect(parsed.metadata.id).toBe("card.counter");
  });

  it("rejects invalid semver", () => {
    expect(() =>
      BlockPackageSchema.parse({
        ...validPackage,
        metadata: { ...validPackage.metadata, version: "v1" },
      })
    ).toThrow();
  });

  it("rejects invalid trust value", () => {
    expect(() =>
      BlockPackageSchema.parse({
        ...validPackage,
        metadata: { ...validPackage.metadata, trust: "official" },
      })
    ).toThrow();
  });

  it("validates registry entry shape", () => {
    const entry = RegistryEntrySchema.parse({
      ...validPackage.metadata,
      signature: validPackage.signature,
    });
    expect(entry.framework).toContain("next-react");
  });
});
