import { PageIR, ProjectIR } from "./types";

export interface EmitResult {
  filePath: string;
  code: string;
}

export type TargetFramework = "next-react" | "vite-react";

export interface FrameworkEmitter {
  targetFramework: TargetFramework;
  emitProject(project: ProjectIR): Record<string, string>;
}

export interface FrameworkParser {
  targetFramework: TargetFramework;
  parseProject(files: Record<string, string>): ProjectIR;
}

export abstract class Emitter {
  abstract emit(page: PageIR): EmitResult;
}
