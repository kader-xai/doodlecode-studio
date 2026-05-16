import { useEffect, useRef, useState } from "react";

/**
 * Renders the cell title as plain text. Double-click flips it into an
 * inline input. Enter / blur saves. Escape cancels.
 *
 * When the title is empty: renders a thin invisible-but-clickable strip
 * so users can still double-click to start a title. No placeholder text,
 * no tooltip — the empty space is the affordance.
 */
export function EditableTitle({
  value,
  onCommit,
  className,
}: {
  value: string | undefined;
  onCommit: (next: string | undefined) => void;
  className?: string;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value ?? "");
  const ref = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!editing) setDraft(value ?? "");
  }, [value, editing]);

  useEffect(() => {
    if (editing) ref.current?.focus();
  }, [editing]);

  const start = (e: React.MouseEvent) => {
    e.stopPropagation();
    setDraft(value ?? "");
    setEditing(true);
  };

  const commit = () => {
    const trimmed = draft.trim();
    if (trimmed !== (value ?? "")) {
      onCommit(trimmed || undefined);
    }
    setEditing(false);
  };

  if (editing) {
    return (
      <input
        ref={ref}
        className={`nodrag border-2 border-ink dark:border-white/70 rounded px-1.5 py-0.5 bg-white dark:bg-[#0f1115] ${className ?? ""}`}
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={commit}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            commit();
          } else if (e.key === "Escape") {
            e.preventDefault();
            setDraft(value ?? "");
            setEditing(false);
          }
        }}
        onClick={(e) => e.stopPropagation()}
        onMouseDown={(e) => e.stopPropagation()}
        style={{ minWidth: 160 }}
      />
    );
  }

  // Empty: render a narrow clickable strip so the area still accepts
  // double-click, without any explanatory text on screen.
  if (!value) {
    return (
      <span
        onDoubleClick={start}
        className="cursor-text inline-block"
        style={{ minWidth: 80, minHeight: "1em" }}
      />
    );
  }

  return (
    <span
      onDoubleClick={start}
      className={`${className ?? ""} cursor-text select-none break-words`}
      style={{ wordBreak: "break-word", overflowWrap: "anywhere" }}
    >
      {value}
    </span>
  );
}
