import type { BlockPackage, RegistryEntry } from "./schema";

export interface SearchBlocksParams {
  q?: string;
  category?: string;
  framework?: string;
}

function asBaseUrl(baseUrl: string): string {
  return baseUrl.replace(/\/+$/, "");
}

export async function publishBlock(baseUrl: string, pkg: BlockPackage): Promise<BlockPackage> {
  const response = await fetch(`${asBaseUrl(baseUrl)}/api/marketplace/publish`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(pkg),
  });

  if (!response.ok) {
    throw new Error(`publish failed with status ${response.status}`);
  }

  return (await response.json()) as BlockPackage;
}

export async function searchBlocks(baseUrl: string, params: SearchBlocksParams = {}): Promise<RegistryEntry[]> {
  const query = new URLSearchParams();
  if (params.q) query.set("q", params.q);
  if (params.category) query.set("category", params.category);
  if (params.framework) query.set("framework", params.framework);

  const suffix = query.toString();
  const endpoint = `${asBaseUrl(baseUrl)}/api/marketplace/search${suffix ? `?${suffix}` : ""}`;
  const response = await fetch(endpoint);

  if (!response.ok) {
    throw new Error(`search failed with status ${response.status}`);
  }

  return (await response.json()) as RegistryEntry[];
}

export async function getBlock(baseUrl: string, id: string): Promise<BlockPackage> {
  const response = await fetch(`${asBaseUrl(baseUrl)}/api/marketplace/blocks/${encodeURIComponent(id)}`);
  if (!response.ok) {
    throw new Error(`getBlock failed with status ${response.status}`);
  }
  return (await response.json()) as BlockPackage;
}

export async function listBlockVersions(baseUrl: string, id: string): Promise<string[]> {
  const response = await fetch(`${asBaseUrl(baseUrl)}/api/marketplace/blocks/${encodeURIComponent(id)}/versions`);
  if (!response.ok) {
    throw new Error(`listBlockVersions failed with status ${response.status}`);
  }
  return (await response.json()) as string[];
}
