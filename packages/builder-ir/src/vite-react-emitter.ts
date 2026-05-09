import type { FrameworkEmitter } from "./emitter";
import type { ProjectIR } from "./types";
import { emitViteApp } from "./react-emitter";

function emitViteProjectScaffold(appCode: string): Record<string, string> {
  return {
    "package.json": JSON.stringify(
      {
        name: "builder-vite-react-app",
        private: true,
        version: "0.0.0",
        type: "module",
        scripts: {
          build: "vite build",
        },
        dependencies: {
          react: "19.1.0",
          "react-dom": "19.1.0",
        },
        devDependencies: {
          "@types/react": "^19.1.2",
          "@types/react-dom": "^19.1.2",
          "@vitejs/plugin-react": "^4.4.1",
          typescript: "^5.8.3",
          vite: "^5.4.19",
        },
      },
      null,
      2
    ),
    "index.html": "<!doctype html>\n<html lang=\"en\">\n  <head>\n    <meta charset=\"UTF-8\" />\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n    <title>Builder Vite React App</title>\n  </head>\n  <body>\n    <div id=\"root\"></div>\n    <script type=\"module\" src=\"/src/main.tsx\"></script>\n  </body>\n</html>\n",
    "vite.config.ts": "import { defineConfig } from \"vite\";\nimport react from \"@vitejs/plugin-react\";\n\nexport default defineConfig({\n  plugins: [react()],\n});\n",
    "src/main.tsx": "import React from \"react\";\nimport ReactDOM from \"react-dom/client\";\nimport App from \"./App\";\nimport \"./index.css\";\n\nReactDOM.createRoot(document.getElementById(\"root\")!).render(\n  <React.StrictMode>\n    <App />\n  </React.StrictMode>\n);\n",
    "src/index.css": "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n",
    "src/App.tsx": appCode,
  };
}

export class ViteReactEmitter implements FrameworkEmitter {
  targetFramework = "vite-react" as const;

  emitProject(project: ProjectIR): Record<string, string> {
    if (!project.pages.length) {
      return {};
    }
    return emitViteProjectScaffold(emitViteApp(project.pages[0]));
  }
}
