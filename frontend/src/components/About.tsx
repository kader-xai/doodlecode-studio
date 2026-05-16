import { useStore } from "../store";
import { APP_VERSION, FILE_FORMAT_VERSION } from "../types";

const PROJECT_URL = "https://github.com/kader-xai/doodlecode-studio";
const AI_BRIEF_PATH = "docs/AI_HANDOFF.md";
const AI_BRIEF_URL = `${PROJECT_URL}/blob/main/${AI_BRIEF_PATH}`;
const MEETUP_URL = "https://www.meetup.com/g/machine-learning-group-riyadh";

const LINKS = [
  { label: "LinkedIn", href: "https://linkedin.com/in/kader-xai", icon: "in", color: "#a5d8ff" },
  { label: "GitHub profile", href: "https://github.com/kader-xai", icon: "{ }", color: "#d0bfff" },
  { label: "Website", href: "https://kader-xai.github.io", icon: "🌐", color: "#b2f2bb" },
];

export function About() {
  const close = useStore((s) => s.setAboutOpen);
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
      onClick={() => close(false)}
    >
      <div
        className="relative w-[520px] max-w-[92vw] max-h-[92vh] overflow-auto scrollbar-none bg-white dark:bg-[#1f2228] border-2 border-ink dark:border-white rounded-3xl shadow-sketch p-6 font-hand text-ink dark:text-white"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="absolute top-3 right-3 w-9 h-9 rounded-full border-2 border-ink dark:border-white bg-white dark:bg-[#0f1115] text-ink dark:text-white text-xl"
          onClick={() => close(false)}
        >
          ✕
        </button>

        <div className="text-4xl mb-1 text-ink dark:text-white">🎨 DoodleCode Studio</div>
        <div className="text-xl text-ink/80 dark:text-white/90">
          A doodle-powered Python notebook & presentation canvas.
        </div>
        <div className="text-base font-mono text-ink/70 dark:text-white/80 mt-1">
          v{APP_VERSION} · file-format v{FILE_FORMAT_VERSION}
        </div>

        {/* Author */}
        <div className="mt-5 flex items-center gap-3">
          <div
            className="w-14 h-14 rounded-2xl border-2 border-ink dark:border-white flex items-center justify-center text-3xl text-ink"
            style={{ background: "#eebefa" }}
          >
            K
          </div>
          <div>
            <div className="text-3xl leading-tight text-ink dark:text-white">
              Co-AI Developed by Kader Mohideen
            </div>
            <div className="text-lg text-ink/80 dark:text-white/85">
              Engineer · designer · doodler
            </div>
          </div>
        </div>

        {/* Project URL CTA */}
        <div className="mt-4 flex items-center gap-3">
          <span
            className="font-hand text-5xl select-none"
            style={{ animation: "wiggle 1.6s ease-in-out infinite" }}
            aria-hidden
          >
            👉
          </span>
          <a
            href={PROJECT_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 px-3 py-3 rounded-2xl border-2 border-ink dark:border-white bg-marker-yellow dark:bg-amber-700 text-ink dark:text-white hover:translate-x-[1px] hover:translate-y-[1px] transition"
          >
            <div className="font-hand text-2xl flex items-center gap-2 text-ink dark:text-white">
              ⭐ Star &amp; clone the project
            </div>
            <div className="font-mono text-base break-all underline decoration-dotted underline-offset-4 text-ink dark:text-white">
              {PROJECT_URL}
            </div>
          </a>
        </div>

        {/* Extra links */}
        <div className="mt-4 space-y-2">
          {LINKS.map((l) => (
            <a
              key={l.label}
              href={l.href}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 px-3 py-2 rounded-xl border-2 border-ink dark:border-white text-ink hover:translate-x-[1px] hover:translate-y-[1px] transition"
              style={{ background: l.color }}
            >
              <span className="w-9 h-9 rounded-lg border-2 border-ink/80 flex items-center justify-center font-mono text-base bg-white/70 text-ink">
                {l.icon}
              </span>
              <div className="flex-1">
                <div className="text-2xl leading-none text-ink">{l.label}</div>
                <div className="text-base font-mono text-ink/85 break-all">{l.href}</div>
              </div>
              <span className="font-hand text-xl text-ink">↗</span>
            </a>
          ))}
        </div>

        <div className="mt-4 text-sm text-ink/80 dark:text-white/85">
          Built with FastAPI, Jupyter kernels, React, Monaco, React Flow,
          and roughjs.
        </div>

        {/* Compact footer — the four cards above are the primary CTAs;
            License, Community, and AI brief sit small below them. */}
        <div className="mt-4 pt-3 border-t-2 border-dashed border-ink/30 dark:border-white/30 space-y-2 text-xs">
          <div className="flex items-center gap-2 px-2 py-1.5 rounded-lg border border-ink/40 dark:border-white/40 bg-white dark:bg-[#0f1115] text-ink dark:text-white">
            <span className="text-sm">📜</span>
            <span className="font-hand text-sm">License</span>
            <span className="font-mono text-[11px] text-ink/80 dark:text-white/80 ml-auto">
              MIT © 2026 Kader Mohideen
            </span>
          </div>

          <a
            href={MEETUP_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-2 py-1.5 rounded-lg border border-ink/40 dark:border-white/40 bg-[#e6fcf5] dark:bg-[#1b4332] text-ink dark:text-white hover:translate-x-[1px] hover:translate-y-[1px] transition"
          >
            <span className="text-sm">🤝</span>
            <span className="font-hand text-sm">Community</span>
            <span className="font-mono text-[11px] truncate text-ink/80 dark:text-white/85 ml-auto">
              ML Group · Riyadh ↗
            </span>
          </a>

          <a
            href={AI_BRIEF_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-2 py-1.5 rounded-lg border border-ink/40 dark:border-white/40 bg-[#f3f0ff] dark:bg-[#2a1e5c] text-ink dark:text-white hover:translate-x-[1px] hover:translate-y-[1px] transition"
          >
            <span className="text-sm">🤖</span>
            <span className="font-hand text-sm">Point your AI</span>
            <span className="font-mono text-[11px] truncate text-ink/80 dark:text-white/85 ml-auto">
              {AI_BRIEF_PATH} ↗
            </span>
          </a>
        </div>
      </div>

      <style>{`
        @keyframes wiggle {
          0%, 100% { transform: translateX(0) rotate(-8deg); }
          50%      { transform: translateX(8px) rotate(0deg); }
        }
      `}</style>
    </div>
  );
}
