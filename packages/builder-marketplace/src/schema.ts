import type { IRNode } from "../../builder-ir/dist/src/types.js";
import { z } from "zod";

export const TRUST_LEVELS = ["verified", "community", "unverified"] as const;
export type BlockTrust = (typeof TRUST_LEVELS)[number];

export const FRAMEWORK_TARGETS = ["next-react", "vite-react"] as const;
export type FrameworkTarget = (typeof FRAMEWORK_TARGETS)[number];

export interface BlockDependency {
  id: string;
  version: string;
}

export interface BlockMetadata {
  id: string;
  name: string;
  description: string;
  version: string;
  author: string;
  license: string;
  framework: FrameworkTarget[];
  trust: BlockTrust;
  keywords: string[];
  category: string;
  createdAt: string;
  updatedAt: string;
  dependencies: BlockDependency[];
  irNode: IRNode;
  signature: string;
}

export type BlockPackage = {
  metadata: Omit<BlockMetadata, "irNode" | "signature">;
  irNode: IRNode;
  signature: string;
};

export type RegistryEntry = Omit<BlockMetadata, "irNode">;

const semverRegex = /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/;

export const BlockDependencySchema = z.object({
  id: z.string().min(1),
  version: z.string().regex(semverRegex, "dependency version must be semver"),
});

export const BlockPackageMetadataSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  description: z.string().min(1),
  version: z.string().regex(semverRegex, "version must be semver"),
  author: z.string().min(1),
  license: z.string().min(1),
  framework: z.array(z.enum(FRAMEWORK_TARGETS)).min(1),
  trust: z.enum(TRUST_LEVELS),
  keywords: z.array(z.string()).default([]),
  category: z.string().min(1),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  dependencies: z.array(BlockDependencySchema).default([]),
});

export const BlockPackageSchema = z.object({
  metadata: BlockPackageMetadataSchema,
  irNode: z.unknown(),
  signature: z.string().regex(/^[a-f0-9]{64}$/i, "signature must be SHA-256 hex"),
});

export const RegistryEntrySchema = BlockPackageMetadataSchema.extend({
  signature: z.string().regex(/^[a-f0-9]{64}$/i, "signature must be SHA-256 hex"),
});

export function parseBlockPackage(input: unknown): BlockPackage {
  return BlockPackageSchema.parse(input) as BlockPackage;
}

export function parseRegistryEntry(input: unknown): RegistryEntry {
  return RegistryEntrySchema.parse(input) as RegistryEntry;
}

export function toRegistryEntry(pkg: BlockPackage): RegistryEntry {
  const metadata = pkg.metadata;
  return {
    ...metadata,
    signature: pkg.signature,
  };
}
