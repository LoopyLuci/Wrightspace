import { WorkspaceShell } from "./workspace-shell";

type HomePageProps = {
  searchParams?: Promise<{
    projectId?: string | string[];
  }>;
};

export default async function HomePage({ searchParams }: HomePageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const rawProjectId = resolvedSearchParams.projectId;
  const projectId = Array.isArray(rawProjectId) ? rawProjectId[0] : rawProjectId;

  return <WorkspaceShell projectId={projectId ?? "starter-project"} />;
}
