import { afterEach, describe, expect, it, vi } from "vitest";
import { getBlock, listBlockVersions, publishBlock, searchBlocks } from "../src/registry-client";
import { signBlock } from "../src/integrity";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("registry API client contract", () => {
  it("publishes blocks via POST", async () => {
    const pkg = signBlock({
      id: "root",
      type: "element",
      tag: "div",
      styles: {},
      props: {},
      children: [],
    });

    const fetchMock = vi.spyOn(globalThis, "fetch" as any).mockResolvedValue(
      new Response(JSON.stringify(pkg), { status: 200, headers: { "content-type": "application/json" } })
    );

    const result = await publishBlock("http://localhost:4001", pkg);
    expect(result.signature).toBe(pkg.signature);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("searches blocks with query filters", async () => {
    const entries = [
      {
        id: "card.counter",
        name: "Card Counter",
        description: "desc",
        version: "1.0.0",
        author: "alice",
        license: "MIT",
        framework: ["next-react"],
        trust: "community",
        keywords: ["card"],
        category: "layout",
        createdAt: "2026-05-09T00:00:00.000Z",
        updatedAt: "2026-05-09T00:00:00.000Z",
        dependencies: [],
        signature: "a".repeat(64),
      },
    ];

    vi.spyOn(globalThis, "fetch" as any).mockResolvedValue(
      new Response(JSON.stringify(entries), { status: 200, headers: { "content-type": "application/json" } })
    );

    const result = await searchBlocks("http://localhost:4001", { q: "card", framework: "next-react" });
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe("card.counter");
  });

  it("fetches full block package and versions", async () => {
    const pkg = signBlock({
      id: "root",
      type: "element",
      tag: "div",
      styles: {},
      props: {},
      children: [],
    });

    const fetchMock = vi
      .spyOn(globalThis, "fetch" as any)
      .mockResolvedValueOnce(new Response(JSON.stringify(pkg), { status: 200, headers: { "content-type": "application/json" } }))
      .mockResolvedValueOnce(new Response(JSON.stringify(["1.0.0", "1.1.0"]), { status: 200, headers: { "content-type": "application/json" } }));

    const full = await getBlock("http://localhost:4001", pkg.metadata.id);
    const versions = await listBlockVersions("http://localhost:4001", pkg.metadata.id);

    expect(full.metadata.id).toBe(pkg.metadata.id);
    expect(versions).toEqual(["1.0.0", "1.1.0"]);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
