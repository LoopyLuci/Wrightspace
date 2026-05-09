import { mkdtempSync, rmSync, writeFileSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { execSync } from "node:child_process";
import { describe, expect, it } from "vitest";
import { emitProject, parseProject } from "../src/project-io";
import { createHeroProjectIR } from "./fixtures/hero-fixture";

function writeProjectToDisk(rootDir: string, files: Record<string, string>): void {
  for (const [relativePath, content] of Object.entries(files)) {
    const fullPath = join(rootDir, relativePath);
    mkdirSync(dirname(fullPath), { recursive: true });
    writeFileSync(fullPath, content, "utf8");
  }
}

function assertProjectBuilds(files: Record<string, string>, folderName: string): void {
  const tempRoot = mkdtempSync(join(tmpdir(), `builder-ir-${folderName}-`));
  try {
    writeProjectToDisk(tempRoot, files);
    execSync("npm install", {
      cwd: tempRoot,
      stdio: "pipe",
      timeout: 300000,
    });
    execSync("npm run build", {
      cwd: tempRoot,
      stdio: "pipe",
      timeout: 300000,
    });
  } finally {
    rmSync(tempRoot, { recursive: true, force: true });
  }
}

describe("framework parity roundtrip", () => {
  it(
    "IR -> Vite emit -> Vite parse -> IR preserves core structure",
    () => {
      const original = createHeroProjectIR();
      const viteFiles = emitProject(original, { targetFramework: "vite-react" });
      const roundTrip = parseProject(viteFiles, { targetFramework: "vite-react" });

      expect(roundTrip.pages[0].root).toEqual(original.pages[0].root);
    },
    120000
  );

  it(
    "IR -> Next parse -> Vite parse cross-emitter parity",
    () => {
      const original = createHeroProjectIR();

      const nextFiles = emitProject(original, { targetFramework: "next-react" });
      const parsedFromNext = parseProject(nextFiles, { targetFramework: "next-react" });

      const viteFromParsedNext = emitProject(parsedFromNext, { targetFramework: "vite-react" });
      const parsedFromVite = parseProject(viteFromParsedNext, { targetFramework: "vite-react" });

      expect(parsedFromVite.pages[0].root).toEqual(original.pages[0].root);
    },
    120000
  );

  it(
    "emitted Next and Vite projects build",
    () => {
      const original = createHeroProjectIR();

      const nextFiles = emitProject(original, { targetFramework: "next-react" });
      const viteFiles = emitProject(original, { targetFramework: "vite-react" });

      assertProjectBuilds(nextFiles, "next");
      assertProjectBuilds(viteFiles, "vite");
    },
    900000
  );
});
