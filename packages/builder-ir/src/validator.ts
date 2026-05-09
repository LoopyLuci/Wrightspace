import { z } from "zod";
import type { IRNode, PageIR, ProjectIR } from "./types";

export const StyleValueSchema = z.object({
  value: z.union([z.string(), z.number()]),
  breakpoint: z.enum(["base", "sm", "md", "lg", "xl", "2xl"]).optional(),
  mediaQuery: z.string().optional()
});

export const ResponsiveStylesSchema = z.record(z.union([StyleValueSchema, z.array(StyleValueSchema)])).default({});

const BindingSchema = z.object({
  binding: z.string().min(1)
});

const EventHandlerSchema = z.object({
  name: z.string().min(1),
  handler: z.string().min(1),
  preventDefault: z.boolean().optional()
});

const StateVariableSchema = z.object({
  name: z.string().min(1),
  type: z.enum(["string", "number", "boolean", "object", "array"]),
  initialValue: z.unknown(),
  persist: z.boolean().optional()
});

const PropSchemaEntrySchema: z.ZodTypeAny = z.lazy(() =>
  z.object({
    type: z.enum(["string", "number", "boolean", "object", "array", "union", "literal"]),
    required: z.boolean().optional(),
    default: z.unknown().optional(),
    description: z.string().optional(),
    properties: z.record(PropSchemaEntrySchema).optional(),
    items: PropSchemaEntrySchema.optional(),
    options: z.array(PropSchemaEntrySchema).optional(),
    enum: z.array(z.string()).optional()
  })
);

const SlotSchemaEntrySchema = z.object({
  description: z.string().optional(),
  allowedTypes: z.array(z.string()).optional()
});

const CustomCodeSchema = z
  .object({
    imports: z.string().optional(),
    variables: z.string().optional(),
    functions: z.string().optional(),
    effects: z.string().optional()
  })
  .optional();

export const IRNodeSchema: z.ZodTypeAny = z.lazy(() =>
  z.union([
    z.object({
      id: z.string().min(1),
      type: z.literal("element"),
      name: z.string().optional(),
      locked: z.boolean().optional(),
      customCode: CustomCodeSchema,
      tag: z.string().min(1),
      styles: ResponsiveStylesSchema,
      props: z.record(z.unknown()).default({}),
      children: z.array(IRNodeSchema).default([]),
      events: z.array(EventHandlerSchema).optional(),
      accessibility: z.record(z.unknown()).optional()
    }),
    z.object({
      id: z.string().min(1),
      type: z.literal("component"),
      name: z.string().optional(),
      locked: z.boolean().optional(),
      customCode: CustomCodeSchema,
      componentId: z.string().min(1),
      variant: z.string().optional(),
      props: z.record(z.unknown()).default({}),
      slots: z.record(z.array(IRNodeSchema)).default({}),
      events: z.array(EventHandlerSchema).optional(),
      state: z.array(StateVariableSchema).optional(),
      propSchema: z.record(PropSchemaEntrySchema).optional(),
      slotSchema: z.record(SlotSchemaEntrySchema).optional()
    }),
    z.object({
      id: z.string().min(1),
      type: z.literal("text"),
      name: z.string().optional(),
      locked: z.boolean().optional(),
      customCode: CustomCodeSchema,
      content: z.union([z.string(), BindingSchema]),
      styles: ResponsiveStylesSchema
    }),
    z.object({
      id: z.string().min(1),
      type: z.literal("slot"),
      name: z.string().optional(),
      locked: z.boolean().optional(),
      customCode: CustomCodeSchema,
      slotName: z.string().min(1),
      fallback: z.array(IRNodeSchema).optional()
    })
  ])
);

export const PageIRSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  route: z.string().min(1),
  root: IRNodeSchema,
  meta: z
    .object({
      title: z.string().optional(),
      description: z.string().optional(),
      ogImage: z.string().optional()
    })
    .default({}),
  state: z.array(StateVariableSchema).optional()
});

export const ProjectIRSchema = z.object({
  schemaVersion: z.string().min(1),
  framework: z.enum(["react", "vue", "svelte", "web-component", "vanilla"]),
  designTokens: z.record(z.unknown()).default({}),
  pages: z.array(PageIRSchema),
  components: z.record(IRNodeSchema).default({}),
  assets: z.record(z.string()).default({})
});

export const BuilderPageIRSchema = PageIRSchema;

export function validateIRNode(value: unknown): IRNode {
  return IRNodeSchema.parse(value) as IRNode;
}

export function validatePageIR(value: unknown): PageIR {
  return PageIRSchema.parse(value) as PageIR;
}

export function validateProjectIR(value: unknown): ProjectIR {
  return ProjectIRSchema.parse(value) as ProjectIR;
}

export function isValidPageIR(value: unknown): value is PageIR {
  return PageIRSchema.safeParse(value).success;
}
