import { describe, expect, it } from "vitest";
import { generateProject } from "../src/react-emitter";
import { parsePageIR } from "../src/reverse-parser";
import { createHeroProjectIR, heroFixture } from "./fixtures/hero-fixture";

describe("IR roundtrip", () => {
  it("IR → emit → parse → IR: deep-equal structural match", () => {
    const pageIR = {
      id: "page-id",
      name: "HeroPage",
      route: "/",
      root: heroFixture,
      meta: {},
      state: [],
    };
    const projectIR = createHeroProjectIR();
    const files = generateProject(projectIR);
    const code = files["app/page.tsx"];
    const parsed = parsePageIR(code);
    // Only compare root for now
    expect(parsed.root).toEqual(pageIR.root);
  });

  it("Custom code survival: mutate region, parse, region preserved", () => {
    const pageIR = {
      id: "page-id",
      name: "HeroPage",
      route: "/",
      root: heroFixture,
      meta: {},
      state: [],
    };
    const projectIR = createHeroProjectIR();
    let files = generateProject(projectIR);
    let code = files["app/page.tsx"];
    // Mutate the functions region
    code = code.replace(
      /function handleCTAClick\(\) \{[\s\S]*?\}/,
      "function handleCTAClick() {\n  alert('mutated!');\n}"
    );
    const parsed = parsePageIR(code);
    expect(parsed.root.customCode?.functions).toContain("mutated!");
  });

  it("Idempotency: emit twice, code matches (ignoring whitespace)", () => {
    const pageIR = {
      id: "page-id",
      name: "HeroPage",
      route: "/",
      root: heroFixture,
      meta: {},
      state: [],
    };
    const projectIR = createHeroProjectIR();
    const files1 = generateProject(projectIR);
    const files2 = generateProject(projectIR);
    const code1 = files1["app/page.tsx"].replace(/\s+/g, "");
    const code2 = files2["app/page.tsx"].replace(/\s+/g, "");
    expect(code1).toBe(code2);
  });
});
