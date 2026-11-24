import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* Static HTML export for Cloudflare Pages (build output: out/). */
  output: "export",
  images: { unoptimized: true },
  /* MapLibre is loaded via its CSP build + setWorkerUrl (see map-2d.tsx). */
};

export default nextConfig;
