# MLX TTS Operating Workflow

## Decision Flow

1. Honor explicit backend/model override.
2. Detect language and task:
   - Vietnamese tones -> `mlx-indextts2`.
   - Chinese content-fidelity or crosstalk -> `mlx-voxcpm2` repaired model first.
   - Chinese相声/stage-dialogue naturalness or OmniVoice comparison -> `mlx-omnivoice`.
   - Qwen voice cloning/instruct/replay/speed -> `mlx-qwen3-tts`.
   - Emotion library, separate emotion reference, or auto Qwen emotion -> `mlx-indextts2`.
3. If uncertain, run a 1-3 line compare pilot and score results.

## Reference Audio Rules

- Prefer 5-15 seconds of clear speech per speaker.
- Use separated vocal audio when the source contains music, audience, room echo, or another speaker.
- For IndexTTS2, keep `speaker_ref` and `emotion_ref` separate when you need emotion disentanglement.
- For speed-only comparisons, do not add emotion references to IndexTTS2 unless
  every backend is doing an equivalent emotion-control pass.
- For OmniVoice and VoxCPM2, `ref_text` must be the exact transcript of
  `ref_audio`. Approximate prompt text can produce extra spoken content.
- For VoxCPM2 fair speed/content comparison, use speaker cloning with
  `ref_audio` only. Do not forward decorative `instruct` text from a shared
  manifest unless the run is explicitly testing voice-design mode.
- For dialogue, store per-speaker reference paths in the manifest instead of swapping globals manually.
- If generated audio carries background noise, clean the reference before changing model parameters.
- For OmniVoice crosstalk, prefer dry same-speaker clips whose transcript has no filler words or repeated phrases. Use the verified `fjymb_library_final` 0526/0527 refs when comparing crosstalk. Do not inject per-line `speed` unless the user asks for tempo control.

## Batch Pattern

1. Convert script to manifest:

```bash
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/batch_manifest.py \
  --input script.txt \
  --output batch_manifest.csv \
  --backend indextts \
  --language zh \
  --speaker-ref "逗哏=/path/a.wav" \
  --speaker-ref "捧哏=/path/b.wav"
```

2. If the run includes Qwen3-TTS or OmniVoice voice cloning, enrich exact
   reference transcripts:

```bash
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/enrich_ref_text.py \
  --manifest batch_manifest.csv \
  --catalog /Users/vanch/mlx-indextts2/outputs/fjymb_library_final/catalog.csv \
  --output batch_manifest.with_ref_text.csv \
  --strict
```

3. Generate with the backend-native batch or replay command.
   For cross-backend comparisons, prefer the unified runner:

```bash
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/run_backend_benchmark.py \
  --manifest batch_manifest.csv \
  --qwen-manifest /Users/vanch/mlx-qwen3-tts/outputs/official_int8_replay_manifest_icl_cleanrefs_v4.json \
  --output-root outputs/four_backend_compare \
  --backends indextts voxcpm2 qwen_tts omnivoice \
  --limit 4
```

4. Stitch outputs:

```bash
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/stitch_wavs.py \
  --manifest batch_manifest.csv \
  --output merged.wav
```

5. Run ASR/leakage checks:

```bash
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/asr_check.py \
  --manifest batch_manifest_with_asr.csv \
  --output metrics.csv
```

## Metrics

Use the following when comparing:

- `content_score`: ASR similarity against intended text, highest priority.
- `leakage_score`: similarity between ASR text and reference prompt text; lower is better.
- `voice_score`: manual or model-based speaker similarity.
- `emotion_score`: manual or classifier score for intended emotion.
- `rtf`: elapsed generation time / audio duration; lower is faster.

RTF comparison rules:

- State the denominator: segment audio sum or merged WAV duration.
- State whether elapsed time includes model loading, first-use tokenizer/audio
  codec setup, denoise, ASR, and stitching.
- Compare same row counts where possible. Short batches overstate warmup cost,
  especially for IndexTTS2.
- Keep generation entrypoints stable. A temporary script is not equivalent to a
  backend-native replay command unless parameters and timing scope match.

Use `scripts/compare_outputs.py` to produce a compact ranking table from metric CSVs.
