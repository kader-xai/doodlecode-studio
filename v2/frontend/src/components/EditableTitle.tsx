import { useEffect, useRef, useState } from "react";

/**
 * Span that becomes an `<input>` on double-click (or when `forceEdit`
 * is set — e.g. F2 from a global handler).
 *
 * - Enter commits.
 * - Esc cancels.
 * - Blur commits.
 *
 * The component owns its own draft state only WHILE editing. The
 * committed value lives in the store via `onCommit`.
 */
export function EditableTitle({
  value,
  onCommit,
  className = "",
  placeholder = "Untitled",
  forceEdit = false,
  onEditEnd,
}: {
  value: string | undefined;
  onCommit: (next: string) => void;
  className?: string;
  placeholder?: string;
  forceEdit?: boolean;
  onEditEnd?: () => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value ?? "");
  const inputRef = useRef<HTMLInputElement>(null);

  // Sync external forceEdit (F2 keyboard shortcut, etc.)
  useEffect(() => {
    if (forceEdit) {
      setDraft(value ?? "");
      setEditing(true);
    }
  }, [forceEdit, value]);

  useEffect(() => {
    if (editing) {
      inputRef.current?.focus();
      inputRef.current?.select();
    }
  }, [editing]);

  const commit = () => {
    const trimmed = draft.trim();
    if (trimmed && trimmed !== value) onCommit(trimmed);
    setEditing(false);
    onEditEnd?.();
  };
  const cancel = () => {
    setEditing(false);
    onEditEnd?.();
  };

  if (!editing) {
    return (
      <span
        // Move cursor — hints "you can drag the cell from here".
        // Double-click switches to text edit; single click does nothing
        // special so ReactFlow's drag handler still fires.
        className={`${className} cursor-move select-none`}
        onDoubleClick={(e) => {
          e.stopPropagation();
          setDraft(value ?? "");
          setEditing(true);
        }}
        title="Drag to move · Double-click to rename"
      >
        {value || <span className="opacity-50">{placeholder}</span>}
      </span>
    );
  }

  return (
    <input
      ref={inputRef}
      value={draft}
      onChange={(e) => setDraft(e.target.value)}
      onBlur={commit}
      onKeyDown={(e) => {
        e.stopPropagation();
        if (e.key === "Enter") commit();
        else if (e.key === "Escape") cancel();
      }}
      onClick={(e) => e.stopPropagation()}
      onPointerDown={(e) => e.stopPropagation()}
      className={`${className} bg-white/90 dark:bg-black/40 px-1 rounded border-2 border-ink/40 dark:border-white/40 outline-none`}
    />
  );
}
