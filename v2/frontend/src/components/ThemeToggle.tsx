import { useStore } from "../store";

export function ThemeToggle() {
  const theme = useStore((s) => s.theme);
  const toggle = useStore((s) => s.toggleTheme);
  return (
    <button
      onClick={toggle}
      title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
      className="relative font-hand text-2xl px-3 py-1.5 rounded-xl border-2 border-ink dark:border-white/70 bg-white/70 dark:bg-[#262a31] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
    >
      {theme === "dark" ? "🌙 Dark" : "☀️ Light"}
    </button>
  );
}
