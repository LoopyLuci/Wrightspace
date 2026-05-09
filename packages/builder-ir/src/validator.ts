import { z } from "zod";

const BuilderNodeSchema: z.ZodType<any> = z.lazy(() =>
  z.object({
    id: z.string().min(1),
    type: z.enum(["page", "section", "heading", "text", "button", "container"]),
    props: z.record(z.union([z.string(), z.number(), z.boolean()])),
    children: z.array(BuilderNodeSchema)
  })
);

export const BuilderPageIRSchema = z.object({
  version: z.literal("1.0"),
  pageId: z.string().min(1),
  root: BuilderNodeSchema
});
