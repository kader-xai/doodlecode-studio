import { useStore } from "../store";
import { APP_VERSION, FILE_FORMAT_VERSION } from "../types";

const LINKS = [
  {
    label: "LinkedIn",
    href: "https://linkedin.com/in/kader-xai",
    icon: "in",
    color: "#a5d8ff",
  },
  {
    label: "GitHub",
    href: "https://github.com/kader-xai",
    icon: "{ }",
    color: "#d0bfff",
  },
  {
    label: "Website",
    href: "https://kader-xai.github.io",
    icon: "🌐",
    color: "#b2f2bb",
  },
];

export function About() {
  const close = useStore((s) => s.setAboutOpen);
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={() => close(false)}
    >
      <div
        className="relative w-[460px] max-w-[92vw] bg-white dark:bg-[#1f2228] border-2 border-ink dark:border-white/70 rounded-3xl shadow-sketch p-6 font-hand"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="absolute top-3 right-3 btn-sketch pink text-base px-2 py-0.5"
          onClick={() => close(false)}
        >
          ✕
        </button>

        <div className="text-4xl mb-1">🎨 DoodleCode Studio</div>
        <div className="text-xl text-ink/70 dark:text-white/70">
          A doodle-powered Python notebook & presentation canvas.
        </div>
        <div className="text-base font-mono text-ink/50 dark:text-white/50 mt-1">
          v{APP_VERSION} · file-format v{FILE_FORMAT_VERSION}
        </div>

        <div className="mt-5 flex items-center gap-3">
          <div
            className="w-14 h-14 rounded-2xl border-2 border-ink dark:border-white/70 flex items-center justify-center text-3xl"
            style={{ background: "#eebefa" }}
          >
            K
          </div>
          <div>
            <div className="text-3xl leading-tight">Developed by Kader-xai</div>
            <div className="text-lg text-ink/60 dark:text-white/60">
              Engineer · designer · doodler
            </div>
          </div>
        </div>

        <div className="mt-5 space-y-2">
          {LINKS.map((l) => (
            <a
              key={l.label}
              href={l.href}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 px-3 py-2 rounded-xl border-2 border-ink dark:border-white/70 hover:translate-x-[1px] hover:translate-y-[1px] transition"
              style={{ background: l.color }}
            >
              <span className="w-9 h-9 rounded-lg border-2 border-ink/80 flex items-center justify-center font-mono text-base bg-white/70">
                {l.icon}
              </span>
              <div className="flex-1">
                <div className="text-2xl leading-none text-ink">{l.label}</div>
                <div className="text-base font-mono text-ink/70 break-all">{l.href}</div>
              </div>
              <span className="font-hand text-xl text-ink">↗</span>
            </a>
          ))}
        </div>

        <div className="mt-5 text-base text-ink/60 dark:text-white/60">
          Built with FastAPI, Jupyter kernels, React, Monaco, React Flow, and roughjs.
          Open source under the MIT license.
        </div>
      </div>
    </div>
  );
}
