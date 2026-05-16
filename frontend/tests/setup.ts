import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

// jsdom doesn't implement ResizeObserver
(globalThis as any).ResizeObserver =
  (globalThis as any).ResizeObserver ||
  class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };

// matchMedia is also unimplemented and used by the store's theme loader
(globalThis as any).matchMedia =
  (globalThis as any).matchMedia ||
  (() => ({ matches: false, addListener() {}, removeListener() {} }));

// Crypto.randomUUID may be missing in older jsdom; polyfill if needed
if (!(globalThis as any).crypto?.randomUUID) {
  (globalThis as any).crypto = {
    ...(globalThis as any).crypto,
    randomUUID: () => Math.random().toString(36).slice(2) + Date.now().toString(36),
  };
}

afterEach(() => cleanup());
