import type { AgentStep } from "./types";

function createButtonPlan(prompt: string): AgentStep[] {
  const labelMatch = prompt.match(/says?\s+(["']?)([^"'.!?]+)\1/i);
  const label = labelMatch?.[2]?.trim() || "Subscribe";

  return [
    {
      description: `Insert CTA button labeled ${label}`,
      target: "page:/",
      action: "create",
      expectedDiff: "Append one button element under the root hero container with accessible text content.",
      metadata: {
        variant: "button",
        label,
        color: /blue/i.test(prompt) ? "blue" : "accent"
      }
    }
  ];
}

function createSecurityAuditPlan(): AgentStep[] {
  return [
    {
      description: "Audit the current page for security and accessibility issues",
      target: "page:/",
      action: "update",
      expectedDiff: "Produce severity-rated findings and suggested fixes without destructive edits.",
      mode: "report",
      metadata: {
        audit: ["external-links", "form-labels", "button-semantics", "keyboard-navigation"]
      }
    }
  ];
}

function createMultiPagePlan(): AgentStep[] {
  return [
    {
      description: "Create a shared marketing shell and route scaffold",
      target: "app-shell",
      action: "create",
      expectedDiff: "Add home, pricing, and contact pages plus shared navigation."
    }
  ];
}

function createResponsivePlan(): AgentStep[] {
  return [
    {
      description: "Refactor the hero layout for smaller breakpoints",
      target: "page:/",
      action: "update",
      expectedDiff: "Preserve content while removing overflow and stacking media below copy on narrow screens."
    }
  ];
}

export function createPlan(prompt: string, benchmarkId?: string): AgentStep[] {
  const normalized = prompt.toLowerCase();

  if (
    benchmarkId === "security-accessibility-audit" ||
    normalized.includes("audit") ||
    normalized.includes("accessibility") ||
    normalized.includes("security")
  ) {
    return createSecurityAuditPlan();
  }

  if (benchmarkId === "single-element-creation" || normalized.includes("button") || normalized.includes("subscribe")) {
    return createButtonPlan(prompt);
  }

  if (benchmarkId === "multi-page-scaffold" || normalized.includes("pricing page") || normalized.includes("contact page")) {
    return createMultiPagePlan();
  }

  if (benchmarkId === "responsive-refactor" || normalized.includes("mobile") || normalized.includes("responsive")) {
    return createResponsivePlan();
  }

  return [
    {
      description: "Inspect the current page and prepare a targeted update",
      target: "page:/",
      action: "update",
      expectedDiff: "Produce a narrow, benchmark-style change with preserved structure."
    }
  ];
}