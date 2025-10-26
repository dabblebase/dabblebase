import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: true,
  turbopack: {
    root: "/workspace/examples/simple-storage-example",
  },
};

export default nextConfig;
