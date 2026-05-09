import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: {
    externalDir: true
  },
  transpilePackages: ["@builder/agent", "@builder/ai", "@builder/canvas", "@builder/collab", "@builder/export", "@builder/ide", "@builder/ir", "@builder/marketplace", "@builder/sync"]
};

export default nextConfig;
