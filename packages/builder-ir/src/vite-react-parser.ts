import type { FrameworkParser } from "./emitter";
import type { ProjectIR } from "./types";
import { parseReactComponentIR } from "./reverse-parser";

export class ViteReactParser implements FrameworkParser {
  targetFramework = "vite-react" as const;

  parseProject(files: Record<string, string>): ProjectIR {
    const appCode = files["src/App.tsx"];
    if (!appCode) {
      throw new Error("Missing src/App.tsx in Vite React project output");
    }

    return {
      schemaVersion: "1.0.0",
      framework: "react",
      designTokens: {},
      pages: [
        parseReactComponentIR(appCode, {
          componentName: "App",
          pageId: "page-id",
          pageName: "App",
          route: "/",
        }),
      ],
      components: {},
      assets: {},
    };
  }
}
