import { createHash } from "node:crypto";
import type { IRNode } from "../../builder-ir/dist/src/types.js";
import type { BlockPackage } from "./schema";

function canonicalize(value: unknown): string {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }

  if (Array.isArray(value)) {
    return `[${value.map((item) => canonicalize(item)).join(",")}]`;
  }

  const entries = Object.entries(value as Record<string, unknown>).sort(([a], [b]) => a.localeCompare(b));
  const content = entries.map(([key, val]) => `${JSON.stringify(key)}:${canonicalize(val)}`).join(",");
  return `{${content}}`;
}

export function hashBlock(irNode: IRNode): string {
  return createHash("sha256").update(canonicalize(irNode)).digest("hex");
}

export function verifyBlock(pkg: BlockPackage): boolean {
  return hashBlock(pkg.irNode) === pkg.signature;
}

export function signBlock(irNode: IRNode, authorKey?: string): BlockPackage {
  const now = new Date().toISOString();
  const signature = hashBlock(irNode);
  const authorName = authorKey?.trim() || "anonymous";

  return {
    metadata: {
      id: `block-${signature.slice(0, 12)}`,
      name: "Untitled Block",
      description: "Generated marketplace block package",
      version: "0.1.0",
      author: authorName,
      license: "UNLICENSED",
      framework: ["next-react", "vite-react"],
      trust: "unverified",
      keywords: [],
      category: "general",
      createdAt: now,
      updatedAt: now,
      dependencies: [],
    },
    irNode,
    signature,
  };
}
