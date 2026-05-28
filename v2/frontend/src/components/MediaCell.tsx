import { Handle, NodeProps, Position } from "reactflow";
import { DoodleBorder } from "./DoodleBorder";
import { ResizeHandle } from "./ResizeHandle";
import { useStore } from "../store";

const VIDEO_EXT = /\.(mp4|webm|mov|m4v|ogg|ogv)(\?|#|$)/i;
const DEFAULT_W = 480;
const DEFAULT_H = 320;

/** Resolve a YouTube watch URL / youtu.be short link to its
 *  embed URL. Returns null when the input isn't YouTube. */
function youTubeEmbed(url: string): string | null {
  try {
    const u = new URL(url);
    const host = u.hostname.replace(/^www\./, "");
    // youtu.be/<id>
    if (host === "youtu.be") {
      const id = u.pathname.slice(1).split("/")[0];
      return id ? `https://www.youtube.com/embed/${id}` : null;
    }
    // youtube.com/watch?v=<id>
    if (host === "youtube.com" || host === "m.youtube.com") {
      if (u.pathname === "/watch") {
        const id = u.searchParams.get("v");
        return id ? `https://www.youtube.com/embed/${id}` : null;
      }
      // youtube.com/embed/<id> — already an embed; keep as-is.
      if (u.pathname.startsWith("/embed/")) return url;
      // youtube.com/shorts/<id> → embed
      const shorts = u.pathname.match(/^\/shorts\/([^/]+)/);
      if (shorts) return `https://www.youtube.com/embed/${shorts[1]}`;
    }
    return null;
  } catch {
    return null;
  }
}

/** Vimeo link → player embed. */
function vimeoEmbed(url: string): string | null {
  try {
    const u = new URL(url);
    if (u.hostname.replace(/^www\./, "") !== "vimeo.com") return null;
    const m = u.pathname.match(/^\/(\d+)/);
    return m ? `https://player.vimeo.com/video/${m[1]}` : null;
  } catch {
    return null;
  }
}

/**
 * Media cell — frameless image or video that fills its card.
 *
 * Source is just a URL. The card has no title strip; the resize
 * handle in the bottom-right corner drives w/h via the store.
 *
 * Cell-coordinate resize: the ResizeHandle divides by the current
 * ReactFlow zoom so dragging "looks like" 1:1 even when the canvas
 * is zoomed in/out.
 *
 * Edit URL: double-click anywhere on the media to prompt for a new
 * URL. Lightweight stand-in until iter 14's full media editor modal.
 */
export function MediaCell({ data, selected }: NodeProps<{ cellId: string }>) {
  const cellId = data.cellId;
  const cell = useStore((s) => s.cells.find((c) => c.id === cellId));
  const setSource = useStore((s) => s.setSource);
  const setSelected = useStore((s) => s.setSelected);

  if (!cell) return null;

  const w = cell.w ?? DEFAULT_W;
  const h = cell.h ?? DEFAULT_H;
  const embedUrl = youTubeEmbed(cell.source) ?? vimeoEmbed(cell.source);
  const isEmbed = !!embedUrl;
  const isVideo = !isEmbed && VIDEO_EXT.test(cell.source);

  const ringColor = selected ? "#c2255c" : "var(--doodle-stroke, #2a2a2a)";
  const ringWidth = selected ? 3.5 : 2.5;

  const editUrl = (e?: React.MouseEvent) => {
    e?.stopPropagation();
    const next = window.prompt("Image or video URL", cell.source);
    if (next != null && next.trim()) setSource(cellId, next.trim());
  };

  return (
    <div
      className="relative"
      style={{ width: w, height: h }}
      onClickCapture={() => setSelected(cellId)}
    >
      <Handle type="target" position={Position.Left} className="!bg-transparent !border-0" />

      <div className="absolute inset-0">
        <DoodleBorder stroke={ringColor} fill="#000000" strokeWidth={ringWidth} radius={14} />

        {/* Media is positioned ABOVE the border SVG (which is
         *  absolute + pointer-events: none under the hood).
         *  No `nodrag` here so the cell can be dragged from its body.
         *  Inner <img>/<video>/<iframe> are passive enough that
         *  drag-from-image is the more useful behavior. Double-click
         *  still opens the URL prompt. */}
        <div
          className="absolute inset-1 overflow-hidden rounded-lg"
          onDoubleClick={editUrl}
          title="Drag to move · Double-click to change URL"
        >
          {!cell.source ? (
            <div
              className="w-full h-full flex flex-col items-center justify-center text-center text-white/80 cursor-pointer"
              onClick={editUrl}
            >
              <div className="font-hand text-3xl">🖼  Add a URL</div>
              <div className="font-hand text-base opacity-70 mt-1">
                Image, video, YouTube, or Vimeo URL
              </div>
            </div>
          ) : isEmbed ? (
            <iframe
              src={embedUrl!}
              title={cell.title ?? "video"}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
              loading="lazy"
              referrerPolicy="strict-origin-when-cross-origin"
              style={{ display: "block", width: "100%", height: "100%", border: "0", background: "#000" }}
            />
          ) : isVideo ? (
            <video
              src={cell.source}
              autoPlay
              loop
              muted
              playsInline
              preload="auto"
              style={{ display: "block", width: "100%", height: "100%", objectFit: "contain", background: "#000" }}
            />
          ) : (
            <img
              src={cell.source}
              alt={cell.title ?? "media"}
              style={{ display: "block", width: "100%", height: "100%", objectFit: "contain", background: "#000" }}
              onError={(e) => {
                // Show a tiny inline broken-image hint instead of the
                // default favicon-style fallback.
                const t = e.currentTarget;
                t.style.display = "none";
                const parent = t.parentElement;
                if (parent && !parent.querySelector(".media-broken")) {
                  const note = document.createElement("div");
                  note.className = "media-broken w-full h-full flex items-center justify-center text-white/70 font-hand text-xl";
                  note.textContent = `❌  Could not load image`;
                  parent.appendChild(note);
                }
              }}
            />
          )}
        </div>

        <ResizeHandle cellId={cellId} baseWidth={w} baseHeight={h} />
      </div>

      <Handle type="source" position={Position.Right} className="!bg-transparent !border-0" />
    </div>
  );
}
