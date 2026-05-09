import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@builder/canvas", "@builder/ide"]
};

export default nextConfig;
