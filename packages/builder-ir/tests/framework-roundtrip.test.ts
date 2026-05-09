import { mkdtempSync, rmSync, writeFileSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { execSync } from "node:child_process";
import { describe, expect, it } from "vitest";
import { emitProject, parseProject } from "../src/project-io";
import { createHeroProjectIR } from "./fixtures/hero-fixture";
import { createSlotStateProjectIR } from "./fixtures/slot-state-fixture";

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
    "Hero Next roundtrip preserves core structure",
    () => {
      const original = createHeroProjectIR();
      const nextFiles = emitProject(original, { targetFramework: "next-react" });
      const roundTrip = parseProject(nextFiles, { targetFramework: "next-react" });

      expect(roundTrip.pages[0].root).toEqual(original.pages[0].root);
    },
    120000
  );

  it(
    "Hero Vite roundtrip preserves core structure",
    () => {
      const original = createHeroProjectIR();
      const viteFiles = emitProject(original, { targetFramework: "vite-react" });
      const roundTrip = parseProject(viteFiles, { targetFramework: "vite-react" });

      expect(roundTrip.pages[0].root).toEqual(original.pages[0].root);
    },
    120000
  );

  it(
    "SlotState Next roundtrip preserves slots and state",
    () => {
      const original = createSlotStateProjectIR();
      const nextFiles = emitProject(original, { targetFramework: "next-react" });
      const roundTrip = parseProject(nextFiles, { targetFramework: "next-react" });

      expect(roundTrip.pages[0].root).toEqual(original.pages[0].root);

      const parsedComponent = (roundTrip.pages[0].root as any).children?.[0];
      expect(parsedComponent?.state).toEqual([{ name: "count", type: "number", initialValue: 0 }]);
    },
    120000
  );

  it(
    "SlotState Vite roundtrip preserves slots and state",
    () => {
      const original = createSlotStateProjectIR();
      const viteFiles = emitProject(original, { targetFramework: "vite-react" });
      const roundTrip = parseProject(viteFiles, { targetFramework: "vite-react" });

      expect(roundTrip.pages[0].root).toEqual(original.pages[0].root);

      const parsedComponent = (roundTrip.pages[0].root as any).children?.[0];
      expect(parsedComponent?.state).toEqual([{ name: "count", type: "number", initialValue: 0 }]);
    },
    120000
  );

  it(
    "SlotState cross-emitter parity",
    () => {
      const original = createSlotStateProjectIR();

      const nextFiles = emitProject(original, { targetFramework: "next-react" });
      const parsedFromNext = parseProject(nextFiles, { targetFramework: "next-react" });

      const viteFromParsedNext = emitProject(parsedFromNext, { targetFramework: "vite-react" });
      const parsedFromVite = parseProject(viteFromParsedNext, { targetFramework: "vite-react" });

      expect(parsedFromVite.pages[0].root).toEqual(original.pages[0].root);

      const parsedComponent = (parsedFromVite.pages[0].root as any).children?.[0];
      expect(parsedComponent?.state).toEqual([{ name: "count", type: "number", initialValue: 0 }]);
    },
    120000
  );

  it(
    "Hero and SlotState emitted projects build for Next and Vite",
    () => {
      const hero = createHeroProjectIR();
      const slotState = createSlotStateProjectIR();

      const heroNext = emitProject(hero, { targetFramework: "next-react" });
      const heroVite = emitProject(hero, { targetFramework: "vite-react" });
      const slotStateNext = emitProject(slotState, { targetFramework: "next-react" });
      const slotStateVite = emitProject(slotState, { targetFramework: "vite-react" });

      assertProjectBuilds(heroNext, "hero-next");
      assertProjectBuilds(heroVite, "hero-vite");
      assertProjectBuilds(slotStateNext, "slot-state-next");
      assertProjectBuilds(slotStateVite, "slot-state-vite");
    },
    900000
  );
});
