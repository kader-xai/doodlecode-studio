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

// Iter 150: Node 22 ships a native `localStorage` that requires
// --localstorage-file. jsdom's window.localStorage can collide with
// that and fail with "is not a function" at import time. Force an
// in-memory shim so store reads/writes during tests are pure JS,
// never the Node 22 builtin.
if (typeof window !== "undefined") {
  const store = new Map<string, string>();
  const shim: Storage = {
    get length() { return store.size; },
    clear: () => store.clear(),
    getItem: (k: string) => store.get(k) ?? null,
    setItem: (k: string, v: string) => { store.set(k, String(v)); },
    removeItem: (k: string) => { store.delete(k); },
    key: (i: number) => Array.from(store.keys())[i] ?? null,
  };
  Object.defineProperty(window, "localStorage", { value: shim, writable: true, configurable: true });
}
