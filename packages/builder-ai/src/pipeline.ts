import type { IRNode } from "../../builder-ir/dist/src/types.js";
import { z } from "zod";

const DEFAULT_ENDPOINT =
  process.env.NEXT_PUBLIC_BUILDER_AI_ENDPOINT ?? "http://127.0.0.1:4001/api/ai/generate-component";

const StyleValueSchema = z.object({
  value: z.union([z.string(), z.number()]),
  breakpoint: z.string().optional(),
  mediaQuery: z.string().optional()
});

const ResponsiveStylesSchema = z.record(z.union([StyleValueSchema, z.array(StyleValueSchema)])).default({});

const BindingSchema = z.object({
  binding: z.string().min(1)
});

const IRNodeSchema: z.ZodTypeAny = z.lazy(() =>
  z.union([
    z.object({
      id: z.string().min(1),
      type: z.literal("text"),
      content: z.union([z.string(), BindingSchema]),
      styles: ResponsiveStylesSchema,
      customCode: z
        .object({
          imports: z.string().optional(),
          variables: z.string().optional(),
          functions: z.string().optional(),
          effects: z.string().optional()
        })
        .optional(),
      name: z.string().optional(),
      locked: z.boolean().optional()
    }),
    z.object({
      id: z.string().min(1),
      type: z.literal("element"),
      tag: z.string().min(1),
      styles: ResponsiveStylesSchema,
      props: z.record(z.unknown()).default({}),
      children: z.array(IRNodeSchema).default([]),
      events: z
        .array(
          z.object({
            name: z.string().min(1),
            handler: z.string().min(1),
            preventDefault: z.boolean().optional()
          })
        )
        .optional(),
      accessibility: z.record(z.unknown()).optional(),
      customCode: z
        .object({
          imports: z.string().optional(),
          variables: z.string().optional(),
          functions: z.string().optional(),
          effects: z.string().optional()
        })
        .optional(),
      name: z.string().optional(),
      locked: z.boolean().optional()
    })
  ])
);

const AIResponseSchema = z.object({
  irNode: IRNodeSchema
});

export interface GenerateComponentOptions {
  endpoint?: string;
  fetchImpl?: typeof fetch;
}

function parseJsonFromText(payload: string): unknown {
  const fenced = payload.match(/```(?:json)?\s*([\s\S]*?)\s*```/i);
  const candidate = fenced?.[1] ?? payload;

  try {
    return JSON.parse(candidate);
  } catch {
    const firstBrace = candidate.indexOf("{");
    const lastBrace = candidate.lastIndexOf("}");
    if (firstBrace >= 0 && lastBrace > firstBrace) {
      return JSON.parse(candidate.slice(firstBrace, lastBrace + 1));
    }
    throw new Error("AI response did not contain valid JSON");
  }
}

function normalizeResponse(raw: unknown): unknown {
  if (typeof raw === "string") {
    return parseJsonFromText(raw);
  }

  if (raw && typeof raw === "object") {
    const record = raw as Record<string, unknown>;
    if (typeof record.irNode === "string") {
      return { ...record, irNode: parseJsonFromText(record.irNode) };
    }
    return raw;
  }

  return raw;
}

export async function generateComponent(
  prompt: string,
  designTokens: Record<string, unknown>,
  options: GenerateComponentOptions = {}
): Promise<IRNode> {
  const trimmed = prompt.trim();
  if (!trimmed) {
    throw new Error("Prompt cannot be empty");
  }

  const endpoint = options.endpoint ?? DEFAULT_ENDPOINT;
  const fetchImpl = options.fetchImpl ?? fetch;

  const response = await fetchImpl(endpoint, {
    method: "POST",
    headers: {
      "content-type": "application/json"
    },
    body: JSON.stringify({
      prompt: trimmed,
      designTokens
    })
  });

  const rawText = await response.text();
  let rawJson: unknown = null;
  if (rawText.trim().length > 0) {
    rawJson = parseJsonFromText(rawText);
  }

  if (!response.ok) {
    const errorMessage =
      rawJson && typeof rawJson === "object" && "error" in (rawJson as Record<string, unknown>)
        ? String((rawJson as Record<string, unknown>).error)
        : `AI request failed with status ${response.status}`;
    throw new Error(errorMessage);
  }

  const normalized = normalizeResponse(rawJson);
  const parsed = AIResponseSchema.safeParse(normalized);
  if (!parsed.success) {
    throw new Error(`Invalid AI node payload: ${parsed.error.message}`);
  }

  return parsed.data.irNode as IRNode;
}
