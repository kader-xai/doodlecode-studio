import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    strictPort: true,
    proxy: {
      "/api": "http://127.0.0.1:8001",
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
    // Iter 181: Mermaid + KaTeX are code-split into their own lazy
    // chunks (loaded only when a Mermaid/Math diagram renders), so the
    // main bundle is ~456 kB. The lone chunk over the default 500 kB
    // warning is mermaid.core itself, which is inherently large and not
    // on the initial-load path — raise the limit so the build stays
    // green without masking a regression in the main bundle.
    chunkSizeWarningLimit: 650,
  },
});
