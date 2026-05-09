import { createDocFromSnapshot, exportProject } from "@builder/export";

export const runtime = "nodejs";

type ExportRequestBody = {
  projectId?: string;
  code?: string;
  irSnapshot?: string | null;
};

export async function POST(request: Request): Promise<Response> {
  let body: ExportRequestBody;
  try {
    body = (await request.json()) as ExportRequestBody;
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

  const zipBuffer = await exportProject(doc);

  return new Response(new Uint8Array(zipBuffer), {
    status: 200,
    headers: {
      "content-type": "application/zip",
      "content-disposition": `attachment; filename=webbuilder-${projectId}.zip`
    }
  });
}
