import { CanvasPreview } from "@builder/canvas";

type PreviewPageProps = {
  searchParams?: Promise<{
    projectId?: string | string[];
  }>;
};

export default async function PreviewPage({ searchParams }: PreviewPageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const rawProjectId = resolvedSearchParams.projectId;
  const projectId = Array.isArray(rawProjectId) ? rawProjectId[0] : rawProjectId;

  return (
    <main className="preview-root">
      <CanvasPreview projectId={projectId} />
    </main>
  );
}
