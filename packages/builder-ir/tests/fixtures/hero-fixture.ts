import type { ElementNode, ProjectIR, TextNode } from "../../src/types";

export const heroFixture: ElementNode = {
  id: "hero-uuid-123",
  type: "element",
  tag: "section",
  name: "Hero",
  styles: {
    display: { value: "flex" },
    flexDirection: { value: "column", breakpoint: "base" },
    alignItems: { value: "center" },
    padding: { value: "6rem 2rem", breakpoint: "base" },
    backgroundColor: { value: "var(--color-primary-900)" },
  },
  props: { className: "hero-section" },
  children: [
    {
      id: "heading-uuid",
      type: "text",
      framework: "react",
      content: "Acme Analytics",
      styles: {
        fontSize: { value: "3.5rem", breakpoint: "base" },
        fontWeight: { value: "700" },
        color: { value: "white" },
      },
    } as TextNode,
    {
      id: "subtitle-uuid",
      type: "text",
      content: { binding: "props.subtitle" },
      styles: { color: { value: "var(--color-neutral-300)" } },
    } as TextNode,
    {
      id: "cta-button",
      type: "element",
      tag: "button",
      props: { type: "button" },
      styles: {
        backgroundColor: { value: "var(--color-accent)" },
        padding: { value: "1rem 2rem" },
      },
      children: [
        {
          id: "cta-text",
          type: "text",
          content: "Get Started",
          styles: {},
        } as TextNode,
      ],
      events: [{ name: "onClick", handler: "handleCTAClick" }],
    } as ElementNode,
  ],
  customCode: {
    functions:
      "function handleCTAClick() {\n  trackEvent('hero_cta_clicked');\n  router.push('/signup');\n}",
  },
};

export function createHeroProjectIR(): ProjectIR {
  return {
    schemaVersion: "1.0.0",
    framework: "react",
    designTokens: {},
    pages: [
      {
        id: "page-id",
        name: "HeroPage",
        route: "/",
        root: heroFixture,
        meta: {},
        state: [],
      },
    ],
    components: {},
    assets: {},
  };
}
