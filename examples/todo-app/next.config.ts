import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: true,
  turbopack: {
    root: "/workspace/examples/todo-app",
  },
};

export default nextConfig;
