# Producing the voiceover with ElevenLabs

This folder turns `script-hi.md` and `script-ta.md` (in the parent
folder) into stitched MP3 voiceovers using the ElevenLabs API.

## One-time setup

### 1. Account + API key

1. Go to <https://elevenlabs.io/sign-up> and create an account.
   The free tier gives you ~10 000 characters/month — enough for one
   ~5-minute script, but you'll burn through it quickly if you
   re-render. The cheapest paid plan (Starter, $5/mo) gives 30 000
   chars/month and unlocks **commercial use of generated audio**,
   which YouTube monetization wants.
2. From the dashboard, click your avatar → **Profile** → **API Key**
   and copy it.
3. Export it in your shell:
   ```bash
   export ELEVENLABS_API_KEY=sk-...
   ```

### 2. Pick a voice

ElevenLabs supports Hindi and Tamil through its **multilingual v2**
model. Built-in voices that sound good in both:

| Voice         | Voice ID                  | Tone                  |
|---------------|---------------------------|-----------------------|
| Rachel        | `21m00Tcm4TlvDq8ikWAM`    | warm, conversational  |
| Adam          | `pNInz6obpgDQGcFmaJgB`    | confident, narrator   |
| Bella         | `EXAVITQu4vr4xnSDxMaL`    | bright, energetic     |
| Antoni        | `ErXwobaYiN019PkySvjV`    | calm, friendly        |

For YouTube tutorials I recommend **Adam** for English/Hindi and
**Bella** or **Rachel** for Tamil — but listen to samples at
<https://elevenlabs.io/voice-library> and pick what fits your style.
You can also **clone your own voice** (Voice Lab → Add Voice → Instant
Voice Clone). Three minutes of your audio is enough.

Copy the voice ID you want and pass it via `--voice` (see below).

### 3. Python deps

```bash
cd v2/docs/video-script/elevenlabs
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew install ffmpeg          # macOS — for joining the per-section clips
# sudo apt install ffmpeg    # Ubuntu
```

## Generate the voiceover

The generator splits the script into the numbered sections, sends one
ElevenLabs request per section (keeps each request under the 2 500-char
per-request limit, and lets you re-render single sections cheaply),
then stitches them with ffmpeg into one MP3.

```bash
# Hindi voiceover (~5 min) using the multilingual model:
python generate.py --script ../script-hi.md --lang hi --voice 21m00Tcm4TlvDq8ikWAM --out hi.mp3

# Tamil voiceover (same voice — multilingual v2 handles both):
python generate.py --script ../script-ta.md --lang ta --voice 21m00Tcm4TlvDq8ikWAM --out ta.mp3
```

Flags:

- `--script PATH`   — path to a `.md` file with `## section` headers
- `--lang`          — `hi` or `ta` (informational; the model is the
  same multilingual v2 either way, but this enables a small lang-
  specific cleanup of the markdown)
- `--voice`         — ElevenLabs voice ID
- `--out`           — final MP3 path
- `--model`         — `eleven_multilingual_v2` (default) or
  `eleven_turbo_v2_5` (cheaper, slightly faster, similar quality)
- `--stability`     — 0.0–1.0 (default 0.5). Higher = more monotone.
- `--similarity`    — 0.0–1.0 (default 0.75). Higher = closer to the
  reference voice but less expressive.
- `--style`         — 0.0–1.0 (default 0.0). Bumps expressiveness for
  the multilingual v2 model.
- `--keep-sections` — keep the per-section MP3s in `./sections/` so
  you can re-render or trim individual ones.

The script caches results under `./sections/`, so re-running with the
same script + voice + model is free — only changed sections re-render.

## YouTube auto-dub flow

YouTube's built-in auto-dub does its own MT + TTS. If you want full
control:

1. Record (or screen-capture) your video in English. Upload to
   YouTube. Keep it unlisted while you iterate.
2. Generate `hi.mp3` and `ta.mp3` here.
3. In YouTube Studio → **Subtitles** → add Hindi + Tamil tracks
   transcribed from `script-hi.md` / `script-ta.md`.
4. In **Subtitles → … → Add audio track**, upload `hi.mp3` and
   `ta.mp3`. YouTube will offer them as language options on the
   playback bar.

If you'd rather let YouTube's auto-dub do its thing without uploading
audio, just upload the English video and turn on **Auto-dub** under
**Subtitles → Languages**. Quality has been improving but is uneven —
the per-language MP3 path above gives you the best result.

## Cost estimate

- Each script is ~4 500 characters with the timing comments stripped.
- Multilingual v2 charges 1 char = 1 credit. Two languages ≈ 9 000
  credits → fits comfortably in the $5/mo Starter plan with room to
  re-render twice. Free tier just barely covers one render of both.

## Troubleshooting

| Problem | Fix |
|---|---|
| 401 unauthorized | Re-check `ELEVENLABS_API_KEY`. The Profile page also shows usage stats — confirm you have credits. |
| Hindi pronouncing English brand names oddly | The script uses Devanagari for narration and Latin for technical terms (`DoodleCode`, `pip`, `markdown`). Mixing scripts is intentional — multilingual v2 reads brand names in their original Latin form. |
| Pauses too short / rushed | Add `<break time="500ms" />` SSML tags between sentences. The generator passes them through untouched. |
| Voice doesn't fit your face | Re-run with a different `--voice` ID. Voices are cached per `(voice, section)` so swapping voice re-renders everything. |
| Want a voice that sounds like *you* | Voice Lab → Add Voice → Instant Voice Clone → upload 3 min of audio → use that voice ID. |

## What gets created

```
v2/docs/video-script/elevenlabs/
├── README.md            this file
├── requirements.txt     elevenlabs-python + python-dotenv
├── generate.py          the CLI
├── sections/            per-section .mp3 cache (gitignored)
├── hi.mp3               final Hindi voiceover (gitignored)
└── ta.mp3               final Tamil voiceover (gitignored)
```
