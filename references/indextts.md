# mlx-indextts2 Reference

Root: `/Users/vanch/mlx-indextts2`

## Strengths

- Best option for Vietnamese and IndexTTS2-style Chinese/English generation.
- Supports speaker/emotion disentanglement: `speaker_ref` for timbre and `emotion_ref_audio` or Qwen/manual emotion for delivery.
- Supports batch generation, combined WAV output, API/WebUI, Qwen text emotion, denoise, emotion2vec library, and novel/dialogue planning.
- Local defaults use 8bit models and auto-route Vietnamese tone-mark text.

## Known Constraints

- Batch RTF is sensitive to warmup amortization. The first rows can include
  semantic codec, speaker, CAMPPlus, and reference-processing setup. A short
  20-line batch can look much slower than a 64-line replay even with similar
  steady-state speed.
- Do not enable per-row `emotion_ref_audio` for speed-only comparison unless
  the task specifically tests separated emotion control. It adds a second
  reference-audio path per row and can dominate short-batch RTF.
- Do not compare IndexTTS2 `emotion_ref_audio` runs directly against
  speaker-only Qwen/VoxCPM2/OmniVoice runs. Label those runs as
  `emotion_ref` and compare them only against equivalent emotion-control runs.

## Key Commands

Single:

```bash
cd /Users/vanch/mlx-indextts2
uv run mlx-indextts generate -r speakers/ref.npz -t "Đêm nay gió rất nhẹ." -o outputs/example.wav --profile auto
```

Batch:

```bash
cd /Users/vanch/mlx-indextts2
uv run mlx-indextts batch -i batch_manifest.csv -o outputs/batch --profile auto --combine
```

Plan dialogue/novel:

```bash
cd /Users/vanch/mlx-indextts2
uv run mlx-indextts plan -i script.txt -o outputs/plan.csv
```

Emotion library:

```bash
cd /Users/vanch/mlx-indextts2
uv run mlx-indextts emotion2vec --input clips_dir --output-dir outputs/emotion_library
```

## Native Parameters To Preserve

- `--profile auto|standard|vietnamese`
- `--model`
- `--ref-audio`
- `--emotion-ref-audio`
- `--emotion` / `--auto-emotion`
- `--emo-alpha`
- `--temperature`, `--top-p`, `--top-k`, `--repetition-penalty`
- `--max-tokens`, `--max-text-tokens-per-segment`
- batch speed controls: `--dynamic-max-tokens/--no-dynamic-max-tokens`,
  `--tokens-per-char`, `--min-max-tokens`
- `--diffusion-steps`, `--cfg-rate`
- `--denoise-ref` / `--no-denoise-ref`
- CSV per-row speaker and emotion reference columns

Emotion sources are mutually exclusive: use exactly one of Qwen auto emotion, manual emotion vector, or emotion reference audio.

## Recommended Use

- Vietnamese: default here.
- Novel/dialogue with emotion smoothing: start here.
- Speaker/emotion separation: start here.
- Fast crosstalk comparison: use clean per-speaker refs only; skip
  `emotion_ref_audio` and Qwen auto emotion unless emotion quality is the test
  target.
- If generated pauses or wrong text appear, reduce segment length and run ASR回读 before trimming audio.
