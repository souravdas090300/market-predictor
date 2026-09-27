import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  transpilePackages: [],
  turbopack: {
    resolveAlias: {
      '@': './src',
    },
  },
};

export default nextConfig;
