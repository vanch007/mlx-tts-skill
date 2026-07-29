# mlx-qwen3-tts Reference

Root: `/Users/vanch/mlx-qwen3-tts`

Status: official-lineage int8 candidate family. Registry ids now include:

- `qwen3_tts_8bit` -> `models/Qwen3-TTS-official-mlx-int8`
- `qwen3_tts_custom_voice_8bit` -> `models/Qwen3-TTS-CustomVoice-official-mlx-int8`
- `qwen3_tts_voice_design_8bit` -> `models/Qwen3-TTS-VoiceDesign-official-mlx-int8`

Use `scripts/audit_model_lineage.py` before benchmark or replay. Do not mark
this backend production until ASR, leakage, voice clone/style, and full-manifest
benchmarks pass.

Latest smoke: `outputs/official_int8_smoke.wav`, short Chinese sentence, RTF
`0.6215`.

CustomVoice smoke: `outputs/custom_voice_int8_smoke.wav`.

VoiceDesign smoke: `outputs/voice_design_int8_smoke.wav`.

Latest full replay: `outputs/official_int8_icl_cleanrefs_v4_full_merged.wav`,
64 rows, RTF `0.3250`, Whisper ASR average similarity `0.8694`, reference leak
score `0.1429`.

## Strengths

- Project-local wrapper exists and can load official Qwen3-TTS bf16/int8 assets.
- Old community 8bit is kept as `qwen3_tts_8bit_community_candidate` only; broken
  symlinks now fail before generation.
- Fast full-task replay path; old 64-line crosstalk replay must be rerun on the
  official int8 candidate before comparison.
- Supports Qwen-style Base ICL cloning with reference audio/text.
- Supports official CustomVoice preset speakers after local int8 conversion:
  `serena`, `vivian`, `uncle_fu`, `ryan`, `aiden`, `ono_anna`, `sohee`,
  `eric`, `dylan`.
- Supports VoiceDesign natural-language `--instruct` after local int8 conversion.
- Supports CLI/runtime batch and streaming flags without routing through `mlx-audio`.
- Supports one-command VoiceDesign-to-Base cloning through
  `mlx-qwen-tts design-clone` and API `/design_clone`.
- Supports local FastAPI/WebUI/tokenizer entrypoints:
  `mlx-qwen-tts-api`, `mlx-qwen-tts-webui`, and `mlx-qwen-tts tokenize`.
- Batch uses dynamic per-row acoustic-token budgeting by default. Avoid fixed
  high caps on short crosstalk lines; they can run to the hard 12Hz limit and
  create long reference-text-like tails.
- `--native-batch` exposes the official `batch_generate` fast path, but only
  for shared-reference/shared-parameter jobs. Do not use it for crosstalk
  manifests that rely on different per-row references.
- ICL quality depends heavily on clean paired refs. Current best sweep refs are
  `0526` for `逗哏` and `0289` for `捧哏`; short or phrase-heavy refs can cause
  prefix leakage or long-token runaway.

## Key Commands

Info:

```bash
cd /Users/vanch/mlx-qwen3-tts
uv run mlx-qwen-tts info
uv run python scripts/audit_model_lineage.py --model qwen3_tts_8bit
uv run python scripts/prepare_official_rebuild.py --force
uv run python scripts/prepare_official_rebuild.py --include-weights --force
uv run python scripts/quantize_official_mlx.py --force
uv run python scripts/prepare_official_rebuild.py --family custom_voice --include-weights --force
uv run python scripts/quantize_official_mlx.py --family custom_voice --force
uv run python scripts/prepare_official_rebuild.py --family voice_design --include-weights --force
uv run python scripts/quantize_official_mlx.py --family voice_design --force
```

Single:

```bash
cd /Users/vanch/mlx-qwen3-tts
uv run mlx-qwen-tts generate \
  --model qwen3_tts_8bit \
  --text "今天我们说一段相声。" \
  --ref-audio /path/ref.wav \
  --ref-text "参考音频对应文本" \
  --output outputs/example.wav \
  --print-lineage
```

Replay manifest:

```bash
cd /Users/vanch/mlx-qwen3-tts
uv run mlx-qwen-tts batch --model qwen3_tts_8bit --input manifest.csv --output-dir outputs/replay --combine
uv run python scripts/replay_manifest.py --manifest batch_manifest.csv --output-dir outputs/replay
uv run python scripts/stitch_wavs.py --manifest outputs/replay/manifest.csv --output outputs/replay_full_merged.wav
```

Native batch, API, WebUI, tokenizer:

```bash
uv run mlx-qwen-tts batch --model qwen3_tts_8bit --input shared_ref.jsonl --output-dir outputs/native --native-batch --combine --require-ref-text
uv run mlx-qwen-tts tokenize --model qwen3_tts_8bit --text "今天我们说一段相声。"
uv run mlx-qwen-tts design-clone --design-instruct "young male, calm" --reference-text "今天我们说一段相声。" --target-text "各位观众，今天继续。" --output outputs/design_clone.wav
uv run --extra api mlx-qwen-tts-api
uv run --extra webui mlx-qwen-tts-webui
```

Benchmark:

```bash
cd /Users/vanch/mlx-qwen3-tts
uv run python scripts/benchmark_qwen.py --model qwen3_tts_8bit --output-dir outputs/bench
```

## Native Parameters To Preserve

- `--model`
- `--text`
- `--ref-audio`
- `--ref-text`
- `--voice`
- `--instruct`
- `--temperature`
- `--speed`
- `--lang-code`
- `--top-k`
- `--top-p`
- `--max-tokens`
- `--stream`
- `--streaming-interval`
- `--native-batch`
- `--require-ref-text`
- `design-clone`: `--design-model`, `--clone-model`, `--design-instruct`,
  `--reference-text`, `--target-text`, `--reference-output`
- replay manifest speaker/text columns

Strict clone validation must happen before model load. If `ref_audio` is present
without exact `ref_text` and `--require-ref-text` is enabled, treat it as an
input error, not a generation failure.

## Recommended Use

- Candidate comparison for voice cloning and instruct-style delivery.
- Full-manifest replay only for non-production comparison until official parity is rebuilt.
- Comparison mode against IndexTTS/VoxCPM2 for crosstalk demos.

If generated audio includes reference text, first verify `ref_text` handling and prompt packaging. Do not accept reference-text leakage as a model-quality issue until the manifest and runtime prompt path are checked.
Use dynamic per-row max-token budgeting for replay manifests; short Chinese lines
should not inherit a fixed high cap.

Latest cross-backend pilot finding:

- Scene/emotion refs produced content score `0.5899` and leakage `0.0902`.
- Clean ICL refs (`0526` for `逗哏`, `0289` for `捧哏`) produced content score
  `0.9813` and leakage `0.0305`.
- For Qwen3-TTS production comparison, always use the clean ICL manifest:
  `/Users/vanch/mlx-qwen3-tts/outputs/official_int8_replay_manifest_icl_cleanrefs_v4.json`.
