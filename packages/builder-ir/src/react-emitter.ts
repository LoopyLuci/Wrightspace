import type {
  ProjectIR,
  PageIR,
  IRNode,
  ElementNode,
  TextNode,
  ComponentNode,
  SlotNode,
  ResponsiveStyles,
} from "./types";

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

function emitNode(node: IRNode): string {
  switch (node.type) {
    case "element":
      return emitElementNode(node as ElementNode);
    case "text":
      return emitTextNode(node as TextNode);
    // TODO: component, slot, etc.
    default:
      return "";
  }
}

function emitCustomCodeRegion(label: string, code?: string): string {
  if (!code) return "";
  return `// @builder:region ${label}\n${code}\n// @builder:end\n`;
}

function emitPage(page: PageIR): string {
  let code = "";
  // Imports region
  if (page.root && (page.root as any).customCode) {
    const cc = (page.root as any).customCode;
    code += emitCustomCodeRegion("imports", cc.imports);
    code += emitCustomCodeRegion("variables", cc.variables);
    code += emitCustomCodeRegion("functions", cc.functions);
    code += emitCustomCodeRegion("effects", cc.effects);
  }
  code += `\nexport default function Page() {\n  return (\n    ${emitNode(page.root)}\n  );\n}`;
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
