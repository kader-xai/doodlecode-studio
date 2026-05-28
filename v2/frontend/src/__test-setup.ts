// Vitest setup — runs before every test file.
//
// jsdom doesn't implement matchMedia; store.ts reads it once at
// initialization to decide the theme. Stub it to keep imports happy.
if (typeof window !== "undefined" && !window.matchMedia) {
  (window as unknown as { matchMedia: (q: string) => MediaQueryList }).matchMedia = (() => ({
    matches: false,
    media: "",
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  })) as unknown as (q: string) => MediaQueryList;
}
