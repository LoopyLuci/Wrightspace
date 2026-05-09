import { describe, expect, it } from "vitest";
import { generateProject } from "../src/react-emitter";
import { parsePageIR } from "../src/reverse-parser";
import type { ElementNode, ProjectIR, TextNode } from "../src/types";

export const heroFixture: ElementNode = {
  id: 'hero-uuid-123',
  type: 'element',
  tag: 'section',
  name: 'Hero',
  styles: {
    display: { value: 'flex' },
    flexDirection: { value: 'column', breakpoint: 'base' },
    alignItems: { value: 'center' },
    padding: { value: '6rem 2rem', breakpoint: 'base' },
    backgroundColor: { value: 'var(--color-primary-900)' },
  },
  props: { className: 'hero-section' },
  children: [
    {
      id: 'heading-uuid',
      type: 'text',
      framework: 'react',
      content: 'Acme Analytics',
      styles: {
        fontSize: { value: '3.5rem', breakpoint: 'base' },
        fontWeight: { value: '700' },
        color: { value: 'white' },
      },
    } as TextNode,
    {
      id: 'subtitle-uuid',
      type: 'text',
      content: { binding: 'props.subtitle' },
      styles: { color: { value: 'var(--color-neutral-300)' } },
    } as TextNode,
    {
      id: 'cta-button',
      type: 'element',
      tag: 'button',
      props: { type: 'button' },
      styles: {
        backgroundColor: { value: 'var(--color-accent)' },
        padding: { value: '1rem 2rem' },
      },
      children: [
        {
          id: 'cta-text',
          type: 'text',
          content: 'Get Started',
          styles: {},
        } as TextNode,
      ],
      events: [
        { name: 'onClick', handler: 'handleCTAClick' },
      ],
    } as ElementNode,
  ],
  customCode: {
    functions:
      "function handleCTAClick() {\n  trackEvent('hero_cta_clicked');\n  router.push('/signup');\n}",
  },
};

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
    const projectIR: ProjectIR = {
      schemaVersion: "1.0.0",
      framework: 'react',
      designTokens: {},
      pages: [pageIR],
      components: {},
      assets: {},
    };
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
    const projectIR: ProjectIR = {
      schemaVersion: "1.0.0",
      framework: 'react',
      designTokens: {},
      pages: [pageIR],
      components: {},
      assets: {},
    };
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
    const projectIR: ProjectIR = {
      schemaVersion: "1.0.0",
      framework: 'react',
      designTokens: {},
      pages: [pageIR],
      components: {},
      assets: {},
    };
    const files1 = generateProject(projectIR);
    const files2 = generateProject(projectIR);
    const code1 = files1["app/page.tsx"].replace(/\s+/g, "");
    const code2 = files2["app/page.tsx"].replace(/\s+/g, "");
    expect(code1).toBe(code2);
  });
});
