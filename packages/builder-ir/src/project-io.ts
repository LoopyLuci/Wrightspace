import type { TargetFramework } from "./emitter";
import type { ProjectIR } from "./types";
import { NextReactEmitter } from "./react-emitter";
import { NextReactParser } from "./reverse-parser";
import { ViteReactEmitter } from "./vite-react-emitter";
import { ViteReactParser } from "./vite-react-parser";

export interface ProjectIOOptions {
  targetFramework?: TargetFramework;
}

const emitterRegistry = {
  "next-react": new NextReactEmitter(),
  "vite-react": new ViteReactEmitter(),
} as const;

const parserRegistry = {
  "next-react": new NextReactParser(),
  "vite-react": new ViteReactParser(),
} as const;

function resolveTargetFramework(options?: ProjectIOOptions): TargetFramework {
  return options?.targetFramework ?? "next-react";
}

export function emitProject(project: ProjectIR, options?: ProjectIOOptions): Record<string, string> {
  const targetFramework = resolveTargetFramework(options);
  return emitterRegistry[targetFramework].emitProject(project);
}

export function parseProject(files: Record<string, string>, options?: ProjectIOOptions): ProjectIR {
  const targetFramework = resolveTargetFramework(options);
  return parserRegistry[targetFramework].parseProject(files);
}
