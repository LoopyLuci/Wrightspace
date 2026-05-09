import { describe, expect, it, vi } from "vitest";
import { generateComponent } from "../src/pipeline";

const validNode = {
  id: "ai-node-1",
  type: "element",
  tag: "section",
  styles: {
    display: { value: "flex" }
  },
  props: {
    className: "ai-section"
  },
  children: [
    {
      id: "ai-text-1",
      type: "text",
      content: "AI generated",
      styles: {}
    }
  ]
};

describe("generateComponent", () => {
  it("returns validated node when endpoint responds with JSON", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ irNode: validNode }), {
        status: 200,
        headers: { "content-type": "application/json" }
      })
    );

    const node = await generateComponent("hero section", {}, { fetchImpl });
    expect(node.id).toBe("ai-node-1");
    expect(fetchImpl).toHaveBeenCalledOnce();
  });

  it("parses fenced JSON payloads", async () => {
    const payload = `\`\`\`json\n${JSON.stringify({ irNode: validNode }, null, 2)}\n\`\`\``;
    const fetchImpl = vi.fn().mockResolvedValue(new Response(payload, { status: 200 }));

    const node = await generateComponent("feature grid", {}, { fetchImpl });
    expect(node.type).toBe("element");
  });

  it("throws API error body message on non-2xx responses", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(new Response(JSON.stringify({ error: "rate limit" }), { status: 429 }));

    await expect(generateComponent("hero", {}, { fetchImpl })).rejects.toThrow("rate limit");
  });

  it("rejects invalid node payloads", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValue(new Response(JSON.stringify({ irNode: { type: "element" } }), { status: 200 }));

    await expect(generateComponent("hero", {}, { fetchImpl })).rejects.toThrow("Invalid AI node payload");
  });
});
