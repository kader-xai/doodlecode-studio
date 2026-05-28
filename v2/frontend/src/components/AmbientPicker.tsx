import { useStore } from "../store";

/** Small 4-button group in the toolbar — picks the ambient theme. */
export function AmbientPicker() {
  const ambient = useStore((s) => s.ambient);
  const setAmbient = useStore((s) => s.setAmbient);
  return (
    <div className="flex gap-0.5 rounded-lg border-2 border-ink/40 dark:border-white/40 p-0.5 bg-white/40 dark:bg-black/30">
      {([
        { id: "off",      label: "∅",  title: "Ambient off" },
        { id: "geometry", label: "△",  title: "Geometry — shapes" },
        { id: "nature",   label: "🌿", title: "Nature — leaves and drops" },
        { id: "science",  label: "⚛",  title: "Science — atoms and beakers" },
      ] as const).map((t) => (
        <button
          key={t.id}
          title={t.title}
          onClick={() => setAmbient(t.id)}
          className={`w-7 h-7 rounded-md border-2 text-base font-hand transition ${
            ambient === t.id
              ? "bg-marker-yellow border-ink dark:bg-amber-700 dark:border-white text-ink dark:text-white shadow-sketch"
              : "bg-white/70 dark:bg-[#1f2228] border-ink/30 dark:border-white/30 text-ink/70 dark:text-white/70 hover:translate-y-[1px]"
          }`}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}
