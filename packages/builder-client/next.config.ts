import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: {
    externalDir: true
  },
  transpilePackages: ["@builder/ai", "@builder/canvas", "@builder/collab", "@builder/export", "@builder/ide", "@builder/ir", "@builder/sync"]
};

export default nextConfig;
