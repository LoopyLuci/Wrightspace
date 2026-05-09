import JSZip from "jszip";
import { describe, expect, it } from "vitest";
import { createDocFromSnapshot, createProjectTarball, exportProject, getProjectFilesFromDoc } from "../src/index";

describe("builder export", () => {
  it("exports a Next.js zip with required files", async () => {
    const doc = createDocFromSnapshot({
      projectId: "export-test",
      pageCode: `export default function Page() { return <section className=\"hero\">Hero</section>; }`
    });

    const archive = await exportProject(doc);
    const zip = await JSZip.loadAsync(archive);
    const names = Object.keys(zip.files);

    expect(names).toContain("package.json");
    expect(names).toContain("next.config.js");
    expect(names).toContain("tailwind.config.js");
    expect(names).toContain("postcss.config.js");
    expect(names).toContain("tsconfig.json");
    expect(names).toContain("src/app/layout.tsx");
    expect(names).toContain("src/app/page.tsx");

    const page = await zip.file("src/app/page.tsx")?.async("string");
    expect(page).toContain("Hero");
  });

  it("creates a tarball from exported files", async () => {
    const doc = createDocFromSnapshot({
      projectId: "tar-test",
      pageCode: "export default function Page() { return <div>Tarball</div>; }"
    });

    const files = getProjectFilesFromDoc(doc);
    const tarball = await createProjectTarball(files);

    expect(Buffer.isBuffer(tarball)).toBe(true);
    expect(tarball.length).toBeGreaterThan(100);
  });
});
