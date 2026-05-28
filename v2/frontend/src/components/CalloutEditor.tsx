import { useEffect, useState } from "react";
import { DoodleBorder } from "./DoodleBorder";
import { useStore } from "../store";
import type { Callout } from "../types";

const MAX_IMAGE_BYTES = 5 * 1024 * 1024;

/**
 * Singleton modal for editing a cell's full callout list.
 *
 * Image input works three ways per row:
 *   1. **Click 🖼 file label** — a real `<label><input type=file></label>`
 *      so the OS file picker opens reliably even when the input is
 *      visually hidden. (A programmatic `inputEl.click()` works in
 *      Chrome but Safari/macOS sometimes drops the user-gesture
 *      context, which is why this used to be flaky.)
 *   2. **Drag-and-drop** onto the row body.
 *   3. **Paste** (Cmd/Ctrl+V) while focused inside the row's textarea.
 *
 * All three converge on `acceptFile(idx, file)`. Files > 5 MB are
 * rejected with a clear alert so the saved .py stays portable.
 *
 * We hold a LOCAL draft so keystrokes don't churn the store on every
 * char — same pattern that stabilized MarkdownCell editing. Save
 * commits the whole array.
 */
export function CalloutEditor() {
  const cellId = useStore((s) => s.calloutEditorCellId);
  const openCalloutEditor = useStore((s) => s.openCalloutEditor);
  const cell = useStore((s) => s.cells.find((c) => c.id === s.calloutEditorCellId));
  const setCallouts = useStore((s) => s.setCallouts);

  const [draft, setDraft] = useState<Callout[]>([]);

  useEffect(() => {
    if (!cellId) return;
    setDraft(
      cell?.callouts && cell.callouts.length
        ? cell.callouts.map((c) => ({ ...c }))
        : [{ text: "" }],
    );
  }, [cellId, cell]);

  useEffect(() => {
    if (!cellId) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        openCalloutEditor(null);
      } else if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        save();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cellId, draft]);

  if (!cellId || !cell) return null;

  const save = () => {
    setCallouts(cellId, draft);
    openCalloutEditor(null);
  };
  const cancel = () => openCalloutEditor(null);

  const updateRow = (i: number, patch: Partial<Callout>) => {
    setDraft((d) => d.map((c, j) => (j === i ? { ...c, ...patch } : c)));
  };
  const removeRow = (i: number) => setDraft((d) => d.filter((_, j) => j !== i));
  const moveRow = (i: number, dir: -1 | 1) => {
    setDraft((d) => {
      const next = [...d];
      const j = i + dir;
      if (j < 0 || j >= next.length) return d;
      [next[i], next[j]] = [next[j], next[i]];
      return next;
    });
  };
  const addRow = () => setDraft((d) => [...d, { text: "" }]);

  /** Convert a File to a data URL and store it on row `idx`. */
  const acceptFile = (idx: number, file: File | null | undefined) => {
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      window.alert(`That's not an image (${file.type || "unknown type"}).`);
      return;
    }
    if (file.size > MAX_IMAGE_BYTES) {
      window.alert(
        `That image is ${(file.size / 1024 / 1024).toFixed(1)} MB — over the 5 MB limit. ` +
          "Try a smaller version so the saved .py stays portable.",
      );
      return;
    }
    const reader = new FileReader();
    reader.onload = () => updateRow(idx, { image: String(reader.result) });
    reader.onerror = () => window.alert("Could not read that file.");
    reader.readAsDataURL(file);
  };

  return (
    <div
      className="fixed inset-0 z-[100] bg-black/40 backdrop-blur-sm flex items-center justify-center p-6"
      onClick={cancel}
    >
      <div
        className="relative max-w-2xl w-full max-h-[90vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <DoodleBorder
          stroke="var(--doodle-stroke, #2a2a2a)"
          fill="var(--doodle-help-fill, #fff8e1)"
          strokeWidth={3}
          radius={18}
        />
        <div className="relative p-5 flex-1 overflow-hidden flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-hand text-3xl">💬 Callouts</h2>
            <div className="flex gap-2">
              <button
                onClick={cancel}
                className="font-hand text-base px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-white/80 dark:bg-[#1f2228] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
              >
                Cancel
              </button>
              <button
                onClick={save}
                className="font-hand text-base px-3 py-0.5 rounded-lg border-2 border-ink dark:border-white/70 bg-marker-mint dark:bg-[#2b8a3e] text-ink dark:text-white shadow-sketch hover:translate-y-[1px] transition"
                title="Save (Cmd/Ctrl+Enter)"
              >
                ✓ Save
              </button>
            </div>
          </div>

          <p className="font-hand text-base text-ink/70 dark:text-white/70 mb-2">
            Editing callouts on <span className="font-mono">{cell.title || cell.id.slice(0, 6)}</span>.
            Drop, paste, or pick an image — up to 5 MB.
          </p>

          <div className="flex-1 overflow-auto pr-1 space-y-3">
            {draft.map((co, i) => (
              <CalloutRow
                key={i}
                callout={co}
                index={i}
                count={draft.length}
                onText={(t) => updateRow(i, { text: t })}
                onFile={(f) => acceptFile(i, f)}
                onClearImage={() => updateRow(i, { image: undefined })}
                onMoveUp={() => moveRow(i, -1)}
                onMoveDown={() => moveRow(i, +1)}
                onRemove={() => removeRow(i)}
              />
            ))}
            <button
              onClick={addRow}
              className="font-hand text-lg px-3 py-1 rounded-lg border-2 border-dashed border-ink/40 dark:border-white/40 text-ink/70 dark:text-white/70 hover:bg-marker-yellow/40 dark:hover:bg-amber-700/30 transition w-full"
            >
              ＋ Add another callout
            </button>
          </div>

          <p className="font-hand text-xs text-ink/50 dark:text-white/50 mt-2">
            Esc · Cancel · Cmd/Ctrl+Enter · Save
          </p>
        </div>
      </div>
    </div>
  );
}

function CalloutRow({
  callout, index, count, onText, onFile, onClearImage, onMoveUp, onMoveDown, onRemove,
}: {
  callout: Callout;
  index: number;
  count: number;
  onText: (t: string) => void;
  onFile: (f: File | null) => void;
  onClearImage: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
  onRemove: () => void;
}) {
  const [dragOver, setDragOver] = useState(false);

  return (
    <div
      className={`rounded-xl border-2 ${dragOver ? "border-[#c2255c] bg-marker-pink/30" : "border-ink/30 dark:border-white/30 bg-white/60 dark:bg-black/30"} p-2.5 transition`}
      onDragOver={(e) => {
        if (Array.from(e.dataTransfer.items).some((it) => it.kind === "file")) {
          e.preventDefault();
          setDragOver(true);
        }
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        const f = e.dataTransfer.files?.[0];
        if (f) onFile(f);
      }}
    >
      <div className="flex items-center justify-between mb-1.5">
        <span className="font-hand text-base text-ink/80 dark:text-white/80">
          Callout {index + 1} / {count}
        </span>
        <div className="flex gap-1 items-center">
          <SmallBtn label="↑" title="Move up" onClick={onMoveUp} disabled={index === 0} />
          <SmallBtn label="↓" title="Move down" onClick={onMoveDown} disabled={index === count - 1} />
          {/* Native label wrapping a hidden input — opens the OS file
           *  picker on click without losing the user-gesture context
           *  the way fileInputRef.click() can. */}
          <label
            title="Add / replace image (click, drop, or paste)"
            className="font-hand text-sm h-7 px-1.5 inline-flex items-center justify-center rounded border-2 border-ink/50 dark:border-white/40 bg-white/90 dark:bg-[#262a31] text-ink dark:text-white hover:translate-y-[1px] transition cursor-pointer"
          >
            🖼
            <input
              type="file"
              accept="image/*"
              className="sr-only"
              onChange={(e) => {
                const f = e.target.files?.[0] ?? null;
                e.target.value = "";
                onFile(f);
              }}
            />
          </label>
          {callout.image && <SmallBtn label="✗" title="Remove image" onClick={onClearImage} />}
          <SmallBtn label="🗑" title="Delete this callout" onClick={onRemove} />
        </div>
      </div>
      {callout.image && (
        <img
          src={callout.image}
          alt=""
          className="mb-1.5 rounded border-2 border-ink/40 max-h-40 object-contain bg-white"
        />
      )}
      <textarea
        value={callout.text}
        onChange={(e) => onText(e.target.value)}
        onPaste={(e) => {
          const item = Array.from(e.clipboardData.items).find((it) =>
            it.type.startsWith("image/"),
          );
          if (item) {
            e.preventDefault();
            const f = item.getAsFile();
            if (f) onFile(f);
          }
        }}
        placeholder="Speech-bubble text…  (paste or drop an image to attach)"
        spellCheck={false}
        rows={3}
        className="w-full font-hand text-lg leading-snug p-2 rounded border-2 border-ink/40 dark:border-white/30 bg-white dark:bg-[#1f2228] text-ink dark:text-white outline-none focus:border-[#c2255c]"
      />
    </div>
  );
}

function SmallBtn({
  label, title, onClick, disabled,
}: { label: string; title: string; onClick: () => void; disabled?: boolean }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={title}
      className="font-hand text-sm w-7 h-7 rounded border-2 border-ink/50 dark:border-white/40 bg-white/90 dark:bg-[#262a31] text-ink dark:text-white hover:translate-y-[1px] transition disabled:opacity-30"
    >
      {label}
    </button>
  );
}
