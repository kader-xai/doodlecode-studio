/// <reference types="vite/client" />

// Iter 181: allow dynamic `import("…​.css")` (used to code-split KaTeX's
// stylesheet alongside its JS chunk) without a TS module-resolution error.
declare module "*.css";
