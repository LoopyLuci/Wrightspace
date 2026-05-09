import { createDocFromSnapshot, createProjectTarball, getProjectFilesFromDoc } from "@builder/export";

export const runtime = "nodejs";

const VERCEL_API_BASE = "https://api.vercel.com";

type DeployRequestBody = {
  projectId?: string;
  code?: string;
  irSnapshot?: string | null;
};

type VercelDeploymentResponse = {
  id?: string;
  url?: string;
  readyState?: string;
  error?: { message?: string };
};

function vercelToken(): string | null {
  return process.env.VERCEL_ACCESS_TOKEN ?? null;
}

function withTeamScope(path: string): string {
  const url = new URL(path, VERCEL_API_BASE);
  if (process.env.VERCEL_TEAM_ID) {
    url.searchParams.set("teamId", process.env.VERCEL_TEAM_ID);
  }
  return url.toString();
}

function formatLiveUrl(url: string | undefined): string | null {
  if (!url) {
    return null;
  }

  return url.startsWith("http") ? url : `https://${url}`;
}

function stateToPhase(state: string | undefined): "building" | "ready" | "error" {
  if (!state) {
    return "building";
  }

  if (state.toUpperCase() === "READY") {
    return "ready";
  }

  if (state.toUpperCase() === "ERROR" || state.toUpperCase() === "CANCELED") {
    return "error";
  }

  return "building";
}

export async function POST(request: Request): Promise<Response> {
  const token = vercelToken();
  if (!token) {
    return Response.json({ error: "VERCEL_ACCESS_TOKEN is not configured" }, { status: 500 });
  }

  let body: DeployRequestBody;
  try {
    body = (await request.json()) as DeployRequestBody;
  } catch {
    return Response.json({ error: "Invalid JSON payload" }, { status: 400 });
  }

  const projectId = body.projectId?.trim();
  const code = body.code;
  if (!projectId || typeof code !== "string" || code.trim().length === 0) {
    return Response.json({ error: "projectId and code are required" }, { status: 400 });
  }

  const doc = createDocFromSnapshot({
    projectId,
    pageCode: code,
    irSnapshot: body.irSnapshot ?? null
  });

  const files = getProjectFilesFromDoc(doc);
  const tarball = await createProjectTarball(files);

  const form = new FormData();
  form.set("name", `webbuilder-${projectId.toLowerCase().replace(/[^a-z0-9-]/g, "-")}`);
  form.set("projectSettings", JSON.stringify({ framework: "nextjs" }));
  form.set("file", new Blob([new Uint8Array(tarball)], { type: "application/x-tar" }), "project.tar");

  const response = await fetch(withTeamScope("/v13/deployments"), {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`
    },
    body: form
  });

  const payload = (await response.json()) as VercelDeploymentResponse;
  if (!response.ok) {
    return Response.json(
      { error: payload.error?.message ?? `Vercel deploy failed with status ${response.status}` },
      { status: 502 }
    );
  }

  return Response.json({
    deploymentId: payload.id,
    status: stateToPhase(payload.readyState),
    readyState: payload.readyState ?? "BUILDING",
    liveUrl: formatLiveUrl(payload.url)
  });
}

export async function GET(request: Request): Promise<Response> {
  const token = vercelToken();
  if (!token) {
    return Response.json({ error: "VERCEL_ACCESS_TOKEN is not configured" }, { status: 500 });
  }

  const { searchParams } = new URL(request.url);
  const deploymentId = searchParams.get("id")?.trim();
  if (!deploymentId) {
    return Response.json({ error: "id is required" }, { status: 400 });
  }

  const response = await fetch(withTeamScope(`/v13/deployments/${deploymentId}`), {
    headers: {
      Authorization: `Bearer ${token}`
    },
    cache: "no-store"
  });

  const payload = (await response.json()) as VercelDeploymentResponse;
  if (!response.ok) {
    return Response.json(
      { error: payload.error?.message ?? `Vercel status failed with status ${response.status}` },
      { status: 502 }
    );
  }

  return Response.json({
    deploymentId,
    status: stateToPhase(payload.readyState),
    readyState: payload.readyState ?? "BUILDING",
    liveUrl: formatLiveUrl(payload.url)
  });
}
