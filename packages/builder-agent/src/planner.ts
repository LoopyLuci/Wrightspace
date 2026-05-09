import { z } from "zod";
import type { AgentStep } from "./types";

const DEFAULT_COMPONENT_ENDPOINT =
  process.env.NEXT_PUBLIC_BUILDER_AI_ENDPOINT ?? "http://127.0.0.1:4001/api/ai/generate-component";

const DEFAULT_PLAN_ENDPOINT = process.env.NEXT_PUBLIC_BUILDER_AI_PLAN_ENDPOINT
  ?? (DEFAULT_COMPONENT_ENDPOINT.endsWith("/api/ai/generate-component")
    ? DEFAULT_COMPONENT_ENDPOINT.replace("/api/ai/generate-component", "/api/ai/generate-plan")
    : DEFAULT_COMPONENT_ENDPOINT);

const StepSchema = z.object({
  description: z.string().min(1),
  target: z.string().min(1),
  action: z.enum(["create", "update", "delete"]),
  expectedDiff: z.string().min(1),
  mode: z.enum(["apply", "report"]).optional(),
  metadata: z.record(z.unknown()).optional()
});

const PlanPayloadSchema = z.object({
  plan: z.array(StepSchema).min(1),
  usage: z
    .object({
      total_tokens: z.number().int().nonnegative().optional(),
      totalTokens: z.number().int().nonnegative().optional()
    })
    .optional()
});

export interface CreatePlanOptions {
  benchmarkId?: string;
  irSnapshot?: string | null;
  endpoint?: string;
  fetchImpl?: typeof fetch;
}

export interface PlanResult {
  steps: AgentStep[];
  tokenCount?: number;
  source: "llm" | "template";
}

function parseJsonFromText(payload: string): unknown {
  const fenced = payload.match(/```(?:json)?\s*([\s\S]*?)\s*```/i);
  const candidate = fenced?.[1] ?? payload;

  try {
    return JSON.parse(candidate);
  } catch {
    const firstBracket = candidate.indexOf("[");
    const lastBracket = candidate.lastIndexOf("]");
    if (firstBracket >= 0 && lastBracket > firstBracket) {
      return JSON.parse(candidate.slice(firstBracket, lastBracket + 1));
    }

    const firstBrace = candidate.indexOf("{");
    const lastBrace = candidate.lastIndexOf("}");
    if (firstBrace >= 0 && lastBrace > firstBrace) {
      return JSON.parse(candidate.slice(firstBrace, lastBrace + 1));
    }

    throw new Error("Planner response did not contain valid JSON");
  }
}

function extractTokenCount(raw: unknown): number | undefined {
  if (!raw || typeof raw !== "object") {
    return undefined;
  }

  const usage = (raw as Record<string, unknown>).usage;
  if (!usage || typeof usage !== "object") {
    return undefined;
  }

  const totalTokens = (usage as Record<string, unknown>).total_tokens;
  if (typeof totalTokens === "number") {
    return totalTokens;
  }

  const camelTotalTokens = (usage as Record<string, unknown>).totalTokens;
  if (typeof camelTotalTokens === "number") {
    return camelTotalTokens;
  }

  return undefined;
}

function normalizePlanPayload(raw: unknown): { plan: AgentStep[]; tokenCount?: number } {
  if (Array.isArray(raw)) {
    const parsedArray = z.array(StepSchema).min(1).parse(raw);
    return { plan: parsedArray as AgentStep[] };
  }

  if (raw && typeof raw === "object") {
    const record = raw as Record<string, unknown>;
    if (Array.isArray(record.steps)) {
      const parsed = PlanPayloadSchema.parse({
        plan: record.steps,
        usage: record.usage
      });

      return {
        plan: parsed.plan as AgentStep[],
        tokenCount: parsed.usage?.total_tokens ?? parsed.usage?.totalTokens
      };
    }

    const parsed = PlanPayloadSchema.parse(record);
    return {
      plan: parsed.plan as AgentStep[],
      tokenCount: parsed.usage?.total_tokens ?? parsed.usage?.totalTokens
    };
  }

  throw new Error("Planner response has unsupported shape");
}

function attachExecutionHints(plan: AgentStep[], prompt: string, benchmarkId?: string): AgentStep[] {
  const normalized = prompt.toLowerCase();

  return plan.map((step, index) => {
    const metadata = { ...(step.metadata ?? {}) };
    if (benchmarkId === "security-accessibility-audit" || step.mode === "report") {
      metadata.audit = ["external-links", "form-labels", "button-semantics", "keyboard-navigation"];
      return {
        ...step,
        mode: "report",
        metadata
      };
    }

    if (benchmarkId === "single-element-creation" || normalized.includes("button") || normalized.includes("subscribe")) {
      if (index === 0) {
        metadata.variant = "button";
        if (typeof metadata.label !== "string") {
          const labelMatch = prompt.match(/says?\s+(["']?)([^"'.!?]+)\1/i);
          metadata.label = labelMatch?.[2]?.trim() || "Subscribe";
        }
        if (typeof metadata.color !== "string") {
          metadata.color = /blue/i.test(prompt) ? "blue" : "accent";
        }
      }
      return {
        ...step,
        metadata
      };
    }

    if (benchmarkId === "multi-page-scaffold" || normalized.includes("pricing") || normalized.includes("contact")) {
      if (index === 0) {
        metadata.variant = "multi-page-scaffold";
      }
      return {
        ...step,
        metadata
      };
    }

    if (benchmarkId === "responsive-refactor" || normalized.includes("responsive") || normalized.includes("mobile")) {
      if (index === 0) {
        metadata.variant = "responsive-refactor";
      }
      return {
        ...step,
        metadata
      };
    }

    return {
      ...step,
      metadata
    };
  });
}

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
      expectedDiff: "Add home, pricing, and contact pages plus shared navigation.",
      metadata: {
        variant: "multi-page-scaffold"
      }
    }
  ];
}

function createResponsivePlan(): AgentStep[] {
  return [
    {
      description: "Refactor the hero layout for smaller breakpoints",
      target: "page:/",
      action: "update",
      expectedDiff: "Preserve content while removing overflow and stacking media below copy on narrow screens.",
      metadata: {
        variant: "responsive-refactor"
      }
    }
  ];
}

function createTemplatePlan(prompt: string, benchmarkId?: string): AgentStep[] {
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

async function createLLMPlan(prompt: string, options: CreatePlanOptions): Promise<PlanResult> {
  const trimmed = prompt.trim();
  if (!trimmed) {
    throw new Error("Prompt cannot be empty");
  }

  const endpoint = options.endpoint ?? DEFAULT_PLAN_ENDPOINT;
  const fetchImpl = options.fetchImpl ?? fetch;

  const response = await fetchImpl(endpoint, {
    method: "POST",
    headers: {
      "content-type": "application/json"
    },
    body: JSON.stringify({
      prompt: trimmed,
      benchmarkId: options.benchmarkId,
      irSnapshot: options.irSnapshot,
      responseFormat: "agent-plan"
    })
  });

  const rawText = await response.text();
  const rawJson = rawText.trim().length > 0 ? parseJsonFromText(rawText) : null;

  if (!response.ok) {
    throw new Error(`Planner request failed with status ${response.status}`);
  }

  const normalized = normalizePlanPayload(rawJson);
  const tokenCount = normalized.tokenCount ?? extractTokenCount(rawJson);

  return {
    steps: attachExecutionHints(normalized.plan, prompt, options.benchmarkId),
    tokenCount,
    source: "llm"
  };
}

export async function createPlan(prompt: string, options: CreatePlanOptions = {}): Promise<PlanResult> {
  try {
    return await createLLMPlan(prompt, options);
  } catch {
    return {
      steps: createTemplatePlan(prompt, options.benchmarkId),
      source: "template",
      tokenCount: 0
    };
  }
}