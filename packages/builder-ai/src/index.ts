import { z } from "zod";

export const BuildCommandSchema = z.object({
  prompt: z.string().min(1)
});

export type BuildCommand = z.infer<typeof BuildCommandSchema>;

export function parseBuildCommand(input: string): BuildCommand | null {
  const trimmed = input.trim();
  if (!trimmed.startsWith("/build ")) {
    return null;
  }

  const parsed = BuildCommandSchema.safeParse({ prompt: trimmed.slice(7).trim() });
  return parsed.success ? parsed.data : null;
}
