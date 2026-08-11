# mlx-indextts2 Reference

Root: `/Users/vanch/mlx-indextts2`

## Versioned Models

- Non-Vietnamese default: IndexTTS 2.5 GPT 8-bit at
  `models/mlx-IndexTTS-2.5-8bit`.
- Validated Hugging Face source revision:
  `d0aa86e75bb6f3437f3831e95056fa72842d89ef`.
- 2.5 languages: `zh`, `en`, `ja`, `es`, `ar`.
- Vietnamese stays on the separate IndexTTS 2.0 local-extension model at
  `models/mlx-indexTTS2-vietnamese-8bit`.
- Standard 2.0 remains available at `models/mlx-indexTTS2-standard-8bit` for
  regression comparison; 1.5 is legacy-only.

Do not share speaker caches between 2.0 and 2.5. The 2.5 cache contract is
revision/schema-bound and rejects incompatible caches.

## Strengths

- 2.5 supports Chinese, English, Japanese, Spanish, and Arabic synthesis plus
  cross-lingual voice cloning.
- 2.5 adds Pinyin, CMU, and Kana pronunciation annotations and completed-segment
  streaming.
- Speaker and emotion are disentangled: use the speaker reference for timbre,
  and a separate emotion reference, eight-value manual emotion, or Qwen emotion
  text for delivery.
- Batch generation, combined WAV output, API/WebUI, denoise, emotion2vec
  libraries, and novel/dialogue planning remain available.

## Install and Entrypoints

Install the optional 2.5 language frontend once:

```bash
cd /Users/vanch/mlx-indextts2
uv sync --extra v25
```

After installation, use the virtual environment's Python module entrypoint for
benchmark and production commands. A plain `uv run` can exact-sync away extras
that were not selected on that invocation.

IndexTTS 2.5 single generation:

```bash
cd /Users/vanch/mlx-indextts2
.venv/bin/python -m mlx_indextts.cli generate \
  --model models/mlx-IndexTTS-2.5-8bit --profile v25 \
  --language ja -r speakers/reference_v25.npz \
  -t "本日のニュースを正確に読み上げてください。" \
  -o outputs/example_ja.wav
```

Vietnamese 2.0:

```bash
cd /Users/vanch/mlx-indextts2
.venv/bin/python -m mlx_indextts.cli generate \
  --model models/mlx-indexTTS2-vietnamese-8bit --profile vietnamese \
  -r speakers/ban_khoe_vietnamese_v2.npz \
  -t "Đêm nay gió rất nhẹ." -o outputs/example_vi.wav
```

Batch:

```bash
cd /Users/vanch/mlx-indextts2
.venv/bin/python -m mlx_indextts.cli batch \
  -i batch_manifest.csv -o outputs/batch --profile v25 --combine
```

Plan dialogue/novel:

```bash
cd /Users/vanch/mlx-indextts2
.venv/bin/python -m mlx_indextts.cli plan \
  -i script.txt -o outputs/plan.csv
```

## Native Parameters To Preserve

- `--profile v25|2.5|auto|standard|vietnamese|vi`
- `--model`
- `--language zh|en|ja|es|ar` for 2.5
- `--ref-audio`
- `--emotion-ref-audio`
- `--emotion` / `--auto-emotion` / `--emotion-text`
- `--emo-alpha`
- `--temperature`, `--top-p`, `--top-k`, `--repetition-penalty`
- `--max-tokens`, `--max-text-tokens`
- 2.5: `--duration-factor`, `--text-normalization`, `--use-gpt-latent`,
  `--stream`
- duration fit: `--target-duration`, `--fit-duration`
- batch speed controls: `--dynamic-max-tokens/--no-dynamic-max-tokens`,
  `--tokens-per-char`, `--min-max-tokens`
- `--diffusion-steps`, `--cfg-rate`
- `--denoise-ref` / `--no-denoise-ref`
- CSV row-level language, speaker reference, and emotion reference columns

Emotion sources are mutually exclusive: use exactly one of Qwen emotion,
manual emotion, or emotion-reference audio.

## Evaluation Rules and Known Constraints

- Formal 2.5 artifact ID: `mlx_indextts2_v25_8bit`.
- Vietnamese 2.0 artifact ID: `mlx_indextts2_vietnamese_8bit`.
- Never relabel historical `mlx_indextts2_standard_8bit` output as 2.5.
- English and Spanish automatic detection is ambiguous. Pass an explicit
  language for every formal five-language run.
- For validated 2.5 long-form testing, use `--max-text-tokens 20`. The old
  120-token default caused content collapse in two formal long-text cases.
- For 10/20-second expansion of a short line, use bounded model-native
  `--duration-factor` before safe `--fit-duration`. This can hit the target and
  preserve words, but UTMOS and speaker similarity fall sharply at 20 seconds.
  Report that quality tradeoff instead of treating duration control as free.
- Batch RTF is sensitive to warmup amortization. Separate cold load/reference
  preprocessing from steady-state generation when possible.
- Do not compare a separated `emotion_ref_audio` run to speaker-only runs as if
  they were the same workload.

## Current Evidence (2026-08-11)

- Project regression: `167 passed, 7 skipped`; Ruff, sdist/wheel, and isolated
  Python 3.13 installation passed.
- Formal 2.5 refresh: 23/23 generated and all were adjudicated by Qwen3-ASR
  1.7B. Spanish and Arabic basic reading had zero error; Japanese basic CER was
  0.125; long-form content passed after safe segmentation.
- Over the 18 cases shared with the previous 2.0 formal artifact, 2.5 improved
  mean RTF but reduced mean UTMOS and speaker similarity. Its verified gain is
  broader language/function coverage, not a universal quality increase.
- Automated metrics do not replace listening. Human subjective review of the
  refreshed audio remains pending.
