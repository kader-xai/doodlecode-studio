import { useStore } from "../store";
import { APP_VERSION, FILE_FORMAT_VERSION } from "../types";

const PROJECT_URL = "https://github.com/kader-xai/doodlecode-studio";

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
        className="relative w-[500px] max-w-[92vw] bg-white dark:bg-[#1f2228] border-2 border-ink dark:border-white rounded-3xl shadow-sketch p-6 font-hand text-ink dark:text-white"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="absolute top-3 right-3 w-8 h-8 rounded-full border-2 border-ink dark:border-white bg-white dark:bg-[#0f1115] text-ink dark:text-white text-xl"
          onClick={() => close(false)}
        >
          ✕
        </button>

        <div className="text-4xl mb-1">🎨 DoodleCode Studio</div>
        <div className="text-xl text-ink/80 dark:text-white/90">
          A doodle-powered Python notebook & presentation canvas.
        </div>
        <div className="text-base font-mono text-ink/60 dark:text-white/70 mt-1">
          v{APP_VERSION} · file-format v{FILE_FORMAT_VERSION}
        </div>

        {/* Author headline */}
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
            <div className="text-lg text-ink/70 dark:text-white/80">
              Engineer · designer · doodler
            </div>
          </div>
        </div>

        {/* Project URL CTA with hand pointing at it — easy to point to
            on a video, easy to click during a live demo. */}
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
            <div className="font-hand text-2xl flex items-center gap-2">
              ⭐ Star &amp; clone the project
            </div>
            <div className="font-mono text-base break-all underline decoration-dotted underline-offset-4">
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
                <div className="text-2xl leading-none">{l.label}</div>
                <div className="text-base font-mono text-ink/80 break-all">{l.href}</div>
              </div>
              <span className="font-hand text-xl">↗</span>
            </a>
          ))}
        </div>

        <div className="mt-4 text-base text-ink/70 dark:text-white/80">
          Built with FastAPI, Jupyter kernels, React, Monaco, React Flow,
          and roughjs. Open source under the MIT license.
        </div>
      </div>

      {/* Small keyframes for the pointing hand */}
      <style>{`
        @keyframes wiggle {
          0%, 100% { transform: translateX(0) rotate(-8deg); }
          50%      { transform: translateX(8px) rotate(0deg); }
        }
      `}</style>
    </div>
  );
}
