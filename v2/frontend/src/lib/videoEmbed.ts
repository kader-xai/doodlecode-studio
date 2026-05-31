/**
 * Iter 183: YouTube / Vimeo URL → embed URL, preserving a start
 * timestamp so a media cell can open a video at a specific moment
 * (great for "jump to the demo" showcase slides).
 *
 * Supported timestamp forms on the source URL:
 *   - `?t=90`, `?t=90s`, `?t=1m30s`, `?t=1h2m3s`  (YouTube + youtu.be)
 *   - `?start=90`                                  (YouTube)
 *   - `#t=90s`                                     (Vimeo)
 *
 * Pure + dependency-free so it unit-tests without a DOM.
 */

/** Parse a YouTube-style time string to whole seconds, or null. */
export function parseTimestamp(raw: string | null | undefined): number | null {
  if (!raw) return null;
  const s = raw.trim();
  // Bare seconds: "90" or "90s".
  if (/^\d+s?$/.test(s)) {
    const n = parseInt(s, 10);
    return Number.isFinite(n) && n > 0 ? n : null;
  }
  // Colon clock: "1:30" or "1:02:03".
  if (/^\d+(:\d{1,2}){1,2}$/.test(s)) {
    const total = s.split(":").reduce((acc, part) => acc * 60 + parseInt(part, 10), 0);
    return total > 0 ? total : null;
  }
  // Compound "1h2m3s" / "2m30s" / "45s".
  const m = s.match(/^(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?$/i);
  if (m && (m[1] || m[2] || m[3])) {
    const total = (+(m[1] || 0)) * 3600 + (+(m[2] || 0)) * 60 + (+(m[3] || 0));
    return total > 0 ? total : null;
  }
  return null;
}

/** Pull a start time (in seconds) out of a watch/share URL's query/hash. */
export function startSecondsOf(u: URL): number | null {
  return (
    parseTimestamp(u.searchParams.get("t")) ??
    parseTimestamp(u.searchParams.get("start")) ??
    // Vimeo puts it in the hash: `#t=90s`.
    parseTimestamp(u.hash.replace(/^#t=/, "") || null)
  );
}

// Iter 184: playback flags the user can include on the source URL and
// have carried into the embed — handy for "loop this demo silently"
// showcase slides. Order is fixed so the output is deterministic.
const YT_PASS = ["autoplay", "mute", "controls", "loop", "modestbranding", "rel", "end"] as const;
// Vimeo uses different param names; map source → Vimeo player param.
const VIMEO_PASS: Record<string, string> = {
  autoplay: "autoplay",
  mute: "muted",
  loop: "loop",
  controls: "controls",
};

/** YouTube watch / youtu.be / shorts / embed URL → embed URL. */
export function youTubeEmbed(url: string): string | null {
  try {
    const u = new URL(url);
    const host = u.hostname.replace(/^www\./, "");
    const start = startSecondsOf(u);

    const build = (id: string) => {
      const p = new URLSearchParams();
      if (start) p.set("start", String(start));
      for (const k of YT_PASS) {
        const v = u.searchParams.get(k);
        if (v != null) p.set(k, v);
      }
      // YouTube only loops an embed when a single-video playlist is named.
      if (p.get("loop") === "1") p.set("playlist", id);
      const qs = p.toString();
      return `https://www.youtube.com/embed/${id}${qs ? `?${qs}` : ""}`;
    };

    if (host === "youtu.be") {
      const id = u.pathname.slice(1).split("/")[0];
      return id ? build(id) : null;
    }
    if (host === "youtube.com" || host === "m.youtube.com") {
      if (u.pathname === "/watch") {
        const id = u.searchParams.get("v");
        return id ? build(id) : null;
      }
      if (u.pathname.startsWith("/embed/")) return url; // already an embed
      const shorts = u.pathname.match(/^\/shorts\/([^/]+)/);
      if (shorts) return build(shorts[1]);
    }
    return null;
  } catch {
    return null;
  }
}

/** Vimeo link → player embed (playback flags + start time appended). */
export function vimeoEmbed(url: string): string | null {
  try {
    const u = new URL(url);
    if (u.hostname.replace(/^www\./, "") !== "vimeo.com") return null;
    const m = u.pathname.match(/^\/(\d+)/);
    if (!m) return null;
    const start = startSecondsOf(u);
    const p = new URLSearchParams();
    for (const [src, dst] of Object.entries(VIMEO_PASS)) {
      const v = u.searchParams.get(src);
      if (v != null) p.set(dst, v);
    }
    const qs = p.toString();
    let out = `https://player.vimeo.com/video/${m[1]}`;
    if (qs) out += `?${qs}`;
    if (start) out += `#t=${start}s`;
    return out;
  } catch {
    return null;
  }
}

/** Either provider's embed URL, or null if it's not an embeddable video. */
export function videoEmbed(url: string): string | null {
  return youTubeEmbed(url) ?? vimeoEmbed(url);
}
