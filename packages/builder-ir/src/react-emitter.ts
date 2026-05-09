import type {
  ProjectIR,
  PageIR,
  IRNode,
  ElementNode,
  TextNode,
  ComponentNode,
  SlotNode,
  ResponsiveStyles,
  StateVariable,
} from "./types";
import type { FrameworkEmitter } from "./emitter";

// Utility: map ResponsiveStyles to Tailwind classes (base breakpoint only)
function stylesToTailwind(styles: ResponsiveStyles): string {
  if (!styles) return "";
  // Only base breakpoint for now
  return Object.entries(styles)
    .map(([key, val]) => {
      if (!val) return "";
      const v = Array.isArray(val) ? val[0] : val;
      if (!v || typeof v.value === "undefined") return "";
      // Simple mapping for demo; real mapping would be more robust
      switch (key) {
        case "display":
          return v.value === "flex" ? "flex" : v.value === "block" ? "block" : "";
        case "flexDirection":
          return v.value === "column" ? "flex-col" : v.value === "row" ? "flex-row" : "";
        case "alignItems":
          return v.value === "center" ? "items-center" : "";
        case "padding":
          return typeof v.value === "string" && v.value.includes("rem") ? "py-24 px-8" : "";
        case "backgroundColor":
          return v.value === "var(--color-primary-900)" ? "bg-primary-900" : "";
        case "fontSize":
          return v.value === "3.5rem" ? "text-5xl" : "";
        case "fontWeight":
          return v.value === "700" ? "font-bold" : "";
        case "color":
          return v.value === "white" ? "text-white" : v.value === "var(--color-neutral-300)" ? "text-neutral-300" : "";
        default:
          return "";
      }
    })
    .filter(Boolean)
    .join(" ");
}

function emitTextNode(node: TextNode): string {
  const text =
    typeof node.content === "string"
      ? node.content
      : `{${typeof node.content.binding === "string" ? node.content.binding : ""}}`;
  const className = stylesToTailwind(node.styles);
  return `<span data-builder-id={"${node.id}"}${className ? ` className=\"${className}\"` : ""}>${text}</span>`;
}

function emitElementNode(node: ElementNode): string {
  const classNameFromStyles = stylesToTailwind(node.styles);
  const classNameFromProps = typeof node.props?.className === "string" ? node.props.className : "";
  const className = [classNameFromStyles, classNameFromProps].filter(Boolean).join(" ");
  const props = [
    `data-builder-id={"${node.id}"}`,
    className ? `className=\"${className}\"` : "",
    ...(node.events || []).map((event) => `${event.name}={${event.handler}}`),
    ...Object.entries(node.props || {})
      .filter(([key]) => key !== "className")
      .map(([k, v]) => `${k}=${JSON.stringify(v)}`),
  ]
    .filter(Boolean)
    .join(" ");
  const children = (node.children || []).map(emitNode).join("");
  return `<${node.tag} ${props}>${children}</${node.tag}>`;
}

function emitSlotNode(node: SlotNode): string {
  const fallback = (node.fallback || []).map(emitNode).join("");
  return `<div data-builder-id={"${node.id}"} data-builder-node={"slot"} data-builder-slot-name={"${node.slotName}"}>${fallback}</div>`;
}

function emitComponentNode(node: ComponentNode): string {
  const classNameFromProps = typeof node.props?.className === "string" ? node.props.className : "";
  const props = [
    `data-builder-id={"${node.id}"}`,
    `data-builder-node={"component"}`,
    `data-builder-component-id={"${node.componentId}"}`,
    node.variant ? `data-builder-variant={"${node.variant}"}` : "",
    classNameFromProps ? `className=\"${classNameFromProps}\"` : "",
    ...(node.events || []).map((event) => `${event.name}={${event.handler}}`),
    ...Object.entries(node.props || {})
      .filter(([key]) => key !== "className")
      .map(([k, v]) => `${k}=${JSON.stringify(v)}`),
  ]
    .filter(Boolean)
    .join(" ");

  const slotRegions = Object.entries(node.slots || {})
    .map(([slotName, slotChildren]) => {
      const childrenCode = (slotChildren || []).map(emitNode).join("");
      return `<div data-builder-slot={"${slotName}"}>${childrenCode}</div>`;
    })
    .join("");

  return `<div ${props}>${slotRegions}</div>`;
}

function toSetterName(name: string): string {
  return `set${name.charAt(0).toUpperCase()}${name.slice(1)}`;
}

function serializeStateValue(value: unknown): string {
  if (typeof value === "string") {
    return JSON.stringify(value);
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  if (value === null) {
    return "null";
  }
  return JSON.stringify(value);
}

interface OwnedState {
  owner: string;
  state: StateVariable;
}

function collectOwnedStates(node: IRNode, ownedStates: OwnedState[]): void {
  if (node.type === "component") {
    const componentNode = node as ComponentNode;
    for (const state of componentNode.state || []) {
      ownedStates.push({ owner: componentNode.id, state });
    }
    for (const slotNodes of Object.values(componentNode.slots || {})) {
      for (const slotNode of slotNodes) {
        collectOwnedStates(slotNode, ownedStates);
      }
    }
    return;
  }

  if (node.type === "slot") {
    const slotNode = node as SlotNode;
    for (const fallbackNode of slotNode.fallback || []) {
      collectOwnedStates(fallbackNode, ownedStates);
    }
    return;
  }

  if (node.type === "element") {
    const elementNode = node as ElementNode;
    for (const child of elementNode.children || []) {
      collectOwnedStates(child, ownedStates);
    }
  }
}

function emitStateDeclarations(page: PageIR): string {
  const declarations: string[] = [];
  for (const state of page.state || []) {
    declarations.push(
      `  const [${state.name}, ${toSetterName(state.name)}] = useState<${state.type}>(${serializeStateValue(
        state.initialValue
      )}); // @builder:state owner=page type=${state.type}`
    );
  }

  const ownedStates: OwnedState[] = [];
  collectOwnedStates(page.root, ownedStates);
  for (const { owner, state } of ownedStates) {
    declarations.push(
      `  const [${state.name}, ${toSetterName(state.name)}] = useState<${state.type}>(${serializeStateValue(
        state.initialValue
      )}); // @builder:state owner=${owner} type=${state.type}`
    );
  }

  return declarations.join("\n");
}

function emitNode(node: IRNode): string {
  switch (node.type) {
    case "element":
      return emitElementNode(node as ElementNode);
    case "text":
      return emitTextNode(node as TextNode);
    case "component":
      return emitComponentNode(node as ComponentNode);
    case "slot":
      return emitSlotNode(node as SlotNode);
    default:
      return "";
  }
}

function emitCustomCodeRegion(label: string, code?: string): string {
  if (!code) return "";
  return `// @builder:region ${label}\n${code}\n// @builder:end\n`;
}

function emitPage(page: PageIR): string {
  return emitComponent(page, "Page");
}

function emitComponent(page: PageIR, componentName: string): string {
  let code = "// @ts-nocheck\n\"use client\";\nimport { useState } from \"react\";\n";
  // Imports region
  if (page.root && (page.root as any).customCode) {
    const cc = (page.root as any).customCode;
    code += emitCustomCodeRegion("imports", cc.imports);
    code += emitCustomCodeRegion("variables", cc.variables);
    code += emitCustomCodeRegion("functions", cc.functions);
    code += emitCustomCodeRegion("effects", cc.effects);
  }
  const stateDeclarations = emitStateDeclarations(page);
  code += `\nexport default function ${componentName}(props: any) {\n${stateDeclarations ? `${stateDeclarations}\n` : ""}  return (\n    ${emitNode(
    page.root
  )}\n  );\n}`;
  return code;
}

export function generateProject(ir: ProjectIR): Record<string, string> {
  // For MVP: emit only first page as app/page.tsx
  const files: Record<string, string> = {};
  if (ir.pages && ir.pages.length > 0) {
    files["app/page.tsx"] = emitPage(ir.pages[0]);
  }
  // TODO: emit components, assets, etc.
  return files;
}

export function emitNextPage(page: PageIR): string {
  return emitPage(page);
}

export function emitViteApp(page: PageIR): string {
  return emitComponent(page, "App");
}

function emitNextProjectScaffold(page: PageIR): Record<string, string> {
  const pageCode = emitNextPage(page);
  return {
    "package.json": JSON.stringify(
      {
        name: "builder-next-app",
        private: true,
        version: "0.0.0",
        scripts: {
          build: "next build",
        },
        dependencies: {
          next: "15.3.2",
          react: "19.1.0",
          "react-dom": "19.1.0",
        },
        devDependencies: {
          "@types/node": "^22.15.17",
          "@types/react": "^19.1.2",
          "@types/react-dom": "^19.1.2",
          typescript: "^5.8.3",
        },
      },
      null,
      2
    ),
    "tsconfig.json": JSON.stringify(
      {
        compilerOptions: {
          target: "ES2017",
          lib: ["dom", "dom.iterable", "esnext"],
          allowJs: true,
          skipLibCheck: true,
          strict: true,
          forceConsistentCasingInFileNames: true,
          noEmit: true,
          esModuleInterop: true,
          module: "esnext",
          moduleResolution: "bundler",
          resolveJsonModule: true,
          isolatedModules: true,
          jsx: "preserve",
          incremental: true,
          plugins: [{ name: "next" }],
        },
        include: ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
        exclude: ["node_modules"],
      },
      null,
      2
    ),
    "next-env.d.ts": "/// <reference types=\"next\" />\n/// <reference types=\"next/image-types/global\" />\n\n// NOTE: This file should not be edited\n",
    "app/layout.tsx": "import \"./globals.css\";\n\nexport default function RootLayout({ children }: { children: React.ReactNode }) {\n  return (\n    <html lang=\"en\">\n      <body>{children}</body>\n    </html>\n  );\n}\n",
    "app/globals.css": ":root {\n  color-scheme: light;\n}\n",
    "app/page.tsx": pageCode,
  };
}

export class NextReactEmitter implements FrameworkEmitter {
  targetFramework = "next-react" as const;

  emitProject(project: ProjectIR): Record<string, string> {
    if (!project.pages.length) {
      return {};
    }
    return emitNextProjectScaffold(project.pages[0]);
  }
}
