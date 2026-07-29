# mlx-omnivoice Reference

Root: `/Users/vanch/mlx-omnivoice`

## Strengths

- Standalone dedicated MLX OmniVoice runtime, separate from upstream OmniVoice and not a `mlx-audio` wrapper.
- Current default model is the local 8bit package at `models/OmniVoice-8bit`.
- Good candidate for Chinese crosstalk/stage dialogue when clean per-speaker references are available.
- Supports voice cloning, voice design / instruct-style generation, batch replay, stitched merged output, and explicit generation controls.
- Full 64-line crosstalk replay has passed ASR content checks after the runtime parity fixes.
- Local FastAPI and Gradio entrypoints exist as lightweight replacements for
  the upstream demo/service surface.
- API also exposes speaker prompt caching and unload controls.

## Known Constraints

- Reference prompts matter strongly. Filler-heavy reference text can leak words like `哎`, `哦`, `回去`, or other口癖 into generated speech.
- `ref_text` must be the exact transcript of `ref_audio`. Do not hand-write an approximate prompt transcript. OmniVoice aligns `ref_text + target_text` with `ref_audio_tokens + target_mask`; mismatched prompt text can make the target audio include extra content.
- Keep normal prompt alignment enabled. Use `--no-prepend-ref-text` only for diagnostics, not for production voice cloning.
- Do not solve filler leakage by trimming audio. First replace the reference with a cleaner same-speaker segment and rerun ASR.
- For this user's crosstalk task, do not inject per-line `speed` unless explicitly requested. Use clean references and sampling controls first.
- Proper nouns and mixed English terms may still need text normalization, e.g. `DeepSeek`, `Codex`, `Flux3`, `Z Image`.
- OmniVoice does not replace IndexTTS2 for separated speaker/emotion reference workflows.

## Key Commands

Prepare a clean crosstalk manifest without speed injection:

```bash
cd /Users/vanch/mlx-omnivoice
.venv/bin/python scripts/prepare_dialogue_manifest.py \
  --input outputs/groupchat_crosstalk_omnivoice8bit/input_manifest.jsonl \
  --output outputs/groupchat_crosstalk_omnivoice8bit/input_manifest_cleanrefs_nospeed.jsonl \
  --speaker-a-ref-audio /path/speaker_a_clean.wav \
  --speaker-a-ref-text "speaker A reference transcript" \
  --speaker-b-ref-audio /path/speaker_b_clean.wav \
  --speaker-b-ref-text "speaker B reference transcript" \
  --no-speed \
  --drop-duration
```

Replay and merge:

```bash
cd /Users/vanch/mlx-omnivoice
.venv/bin/python scripts/replay_manifest.py \
  --model omnivoice_8bit \
  --manifest outputs/groupchat_crosstalk_omnivoice8bit/input_manifest_cleanrefs_nospeed.jsonl \
  --output-dir outputs/groupchat_crosstalk_omnivoice8bit/full_cleanrefs_nospeed \
  --combine \
  --combine-crossfade-ms 45 \
  --position-temperature 2.0 \
  --guidance-scale 2.0 \
  --num-step 24 \
  --speed 1.0
```

Local API / WebUI:

```bash
cd /Users/vanch/mlx-omnivoice
uv run mlx-omnivoice-api
uv run mlx-omnivoice-webui
```

## Native Parameters To Preserve

- `--model`
- `--manifest`
- `--output-dir`
- `--combine`
- `--combine-crossfade-ms`
- `--num-step`
- `--guidance-scale`
- `--class-temperature`
- `--position-temperature`
- `--speed`
- `--max-text-tokens-per-segment`
- per-row `ref_audio`, `ref_text`, `speaker`, `text`, `instruct`
- diagnostic-only `--no-prepend-ref-text`
- manifest preparation flags: `--no-speed`, `--drop-duration`, `--override-speed`
- API endpoints: `/health`, `/generate`, `/batch`, `/speaker`, `/unload`
- `--require-ref-text` must fail before model load for generate, batch, and
  speaker-cache flows when `ref_audio` is present without exact `ref_text`.

## Recommended Use

- Chinese crosstalk or staged two-speaker narration where the user wants a dedicated OmniVoice comparison.
- Replaying a prepared dialogue manifest with clean per-speaker reference clips.
- Testing whether OmniVoice gives better crosstalk cadence than Qwen TTS or IndexTTS2.

Use ASR回读 after every full replay. For the latest no-speed 8bit crosstalk run:

- Output: `/Users/vanch/mlx-omnivoice/outputs/groupchat_crosstalk_omnivoice8bit/full_cleanrefs_nospeed/combined.wav`
- Duration: `187.746s`
- Wall RTF: `0.5823`
- ASR leakage counts: `哎=0`, `哦=0`, `哎去=0`, `回去=0`, `啊=0`
