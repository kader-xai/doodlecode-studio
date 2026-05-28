"""Turn a sectioned narration .md into a stitched MP3 via ElevenLabs.

Usage:
    export ELEVENLABS_API_KEY=sk-...
    python generate.py --script ../script-hi.md --voice 21m00Tcm4TlvDq8ikWAM --out hi.mp3

The script:
  1. Reads the .md, drops timing comments and stage directions
     (lines starting with `>`), keeps only the spoken content.
  2. Splits into the numbered `## N. <title>` sections.
  3. For each section, hashes the (text + voice + model + settings)
     and reuses any cached MP3 under `./sections/<hash>.mp3`.
  4. Calls ElevenLabs for the rest; writes each per-section MP3 to
     the cache.
  5. Stitches everything together with ffmpeg's concat demuxer into
     the final `--out` MP3.

Re-running with unchanged text + voice is free — only changed
sections re-render.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path


def strip_markdown(md: str) -> list[tuple[str, str]]:
    """Return [(section_title, spoken_text)] pairs.

    Spoken text has the markdown stripped down to plain sentences.
    Markers like `**bold**`, headings, blockquotes, and HR rules are
    removed; SSML `<break ... />` tags are preserved.
    """
    sections: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_body: list[str] = []

    for raw in md.splitlines():
        line = raw.rstrip()
        # New numbered section: `## 3. Foo (0:50 – 1:30)` → title "Foo"
        m = re.match(r"^##\s+\d+\.\s+(.+?)(?:\s*\(.*?\))?\s*$", line)
        if m:
            if current_title is not None:
                sections.append((current_title, current_body))
            current_title = m.group(1).strip()
            current_body = []
            continue
        # Blockquote / front-matter / horizontal rule — skip.
        if line.startswith(">") or line.startswith("---") or line.startswith("# "):
            continue
        # Top of file before any section — skip.
        if current_title is None:
            continue
        # Strip markdown emphasis but keep punctuation. Drop trailing
        # bullet/dash markers if any.
        cleaned = (
            line
            .replace("**", "")
            .replace("__", "")
            .replace("`", "")
            .replace("*", "")
        )
        cleaned = cleaned.strip()
        if cleaned:
            current_body.append(cleaned)
        else:
            # Preserve paragraph breaks with a half-second pause.
            current_body.append('<break time="400ms" />')

    if current_title is not None:
        sections.append((current_title, current_body))
    return [(t, "\n".join(b).strip()) for t, b in sections]


def hash_key(text: str, voice: str, model: str, settings: dict) -> str:
    h = hashlib.sha256()
    h.update(text.encode("utf-8"))
    h.update(voice.encode("utf-8"))
    h.update(model.encode("utf-8"))
    h.update(repr(sorted(settings.items())).encode("utf-8"))
    return h.hexdigest()[:16]


def call_elevenlabs(text: str, voice_id: str, model: str, settings: dict,
                    api_key: str, out_path: Path) -> None:
    """Send one TTS request and write the MP3 to `out_path`."""
    # Lazy import so the script works even if elevenlabs isn't installed
    # yet — we error with a useful message instead of a traceback.
    try:
        from elevenlabs.client import ElevenLabs
    except ImportError:
        print(
            "Missing dependency: `pip install -r requirements.txt`",
            file=sys.stderr,
        )
        sys.exit(1)

    client = ElevenLabs(api_key=api_key)
    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        model_id=model,
        text=text,
        output_format="mp3_44100_128",
        voice_settings={
            "stability": settings["stability"],
            "similarity_boost": settings["similarity"],
            "style": settings["style"],
            "use_speaker_boost": True,
        },
    )
    # `audio` is a generator of bytes chunks.
    out_path.write_bytes(b"".join(audio))


def stitch_mp3(parts: list[Path], out: Path) -> None:
    """Use ffmpeg's concat demuxer to join the per-section clips."""
    if not parts:
        raise RuntimeError("Nothing to stitch.")
    listfile = out.with_suffix(".txt")
    listfile.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in parts) + "\n",
        encoding="utf-8",
    )
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-f", "concat", "-safe", "0", "-i", str(listfile),
             "-c", "copy", str(out)],
            check=True,
        )
    finally:
        listfile.unlink(missing_ok=True)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--script", required=True, type=Path)
    p.add_argument("--voice",  required=True,
                   help="ElevenLabs voice ID (see README)")
    p.add_argument("--out",    required=True, type=Path)
    p.add_argument("--lang",   choices=["en", "hi", "ta"], default="en",
                   help="Informational — multilingual v2 handles all three")
    p.add_argument("--model",  default="eleven_multilingual_v2")
    p.add_argument("--stability",  type=float, default=0.5)
    p.add_argument("--similarity", type=float, default=0.75)
    p.add_argument("--style",      type=float, default=0.0)
    p.add_argument("--keep-sections", action="store_true",
                   help="Keep ./sections/<hash>.mp3 after stitching")
    args = p.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("ELEVENLABS_API_KEY env var not set.", file=sys.stderr)
        return 2

    md = args.script.read_text(encoding="utf-8")
    sections = strip_markdown(md)
    if not sections:
        print(f"No sections found in {args.script}", file=sys.stderr)
        return 1

    settings = {
        "stability": args.stability,
        "similarity": args.similarity,
        "style": args.style,
    }

    cache_dir = Path(__file__).parent / "sections"
    cache_dir.mkdir(exist_ok=True)

    rendered: list[Path] = []
    total_chars = 0
    cached_count = 0

    for idx, (title, text) in enumerate(sections, 1):
        if not text:
            continue
        key = hash_key(text, args.voice, args.model, settings)
        section_mp3 = cache_dir / f"{idx:02d}-{key}.mp3"
        total_chars += len(text)
        if section_mp3.is_file():
            print(f"  [{idx:02d}] {title:<28}  cached ({len(text)} chars)")
            cached_count += 1
        else:
            print(f"  [{idx:02d}] {title:<28}  rendering ({len(text)} chars)…",
                  flush=True)
            call_elevenlabs(text, args.voice, args.model, settings,
                            api_key, section_mp3)
        rendered.append(section_mp3)

    print(f"\n→ Stitching {len(rendered)} sections into {args.out}")
    stitch_mp3(rendered, args.out)
    print(f"  Cached: {cached_count}/{len(rendered)} sections")
    print(f"  Total characters sent: ~{total_chars - sum(len(s[1]) for s in sections if not (cache_dir / f'{i:02d}-{hash_key(s[1], args.voice, args.model, settings)}.mp3').is_file() for i in [1])}")
    print(f"  Done.  →  {args.out}")

    if not args.keep_sections:
        # Keep the cache — only sweep stray files. (We never remove
        # the per-section MP3s; they're useful for re-runs.)
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
