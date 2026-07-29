# mlx-voxcpm2 Reference

Root: `/Users/vanch/mlx-voxcpm2`

Status: performance-verified candidate. The native runtime is rebuilt from
official `OpenBMB/VoxCPM` inference and official `openbmb/VoxCPM2` components,
with no `mlx-audio` production runtime dependency.

## Strengths

- Potentially strong Chinese content-fidelity backend after standalone rebuild.
- Fast Chinese crosstalk candidate after native MLX optimization.
- The project exists because generic `mlx-community/VoxCPM2-*` packages had tokenizer drift and poor Chinese fidelity.

## Hard Constraint

Do not treat generic community VoxCPM2 packages as production-quality Chinese
TTS. The native local package must preserve official behavior and verify:

- official `VoxCPM2Tokenizer` behavior
- token ID parity
- ASR回读 content match
- no reference-text leakage

For performance comparisons, do not use ad hoc one-off scripts unless they
reproduce the validated replay path. The verified clean-reference run used the
local repaired 8bit model, a warmed single process, two clean speaker refs, and
manifest-derived row timing. If a new run is slower, first compare:

- same model path: `/Users/vanch/mlx-voxcpm2/models/VoxCPM2-8bit`
- same reference files and exact prompt-text strategy
- same `max_tokens`
- do not pass per-row `instruct` for a voice-cloning benchmark unless the
  comparison explicitly tests voice-design/instruct mode
- same row count and text length distribution
- same RTF definition: row-weighted generation time vs full wall time

## Key Commands

Single official-style native generation:

```bash
cd /Users/vanch/mlx-voxcpm2
PYTHONPATH=/Users/vanch/mlx-voxcpm2 /Users/vanch/mlx-indextts2/.venv/bin/python \
  -m mlx_voxcpm2.cli generate \
  --model-dir models/VoxCPM2-official-mlx-int8-components \
  --text "你好，今天我们说一段相声。" \
  --reference-wav-path /path/ref.wav \
  --output benchmarks/single.wav \
  --backend native
```

Prompt-cache continuation:

```bash
PYTHONPATH=/Users/vanch/mlx-voxcpm2 /Users/vanch/mlx-indextts2/.venv/bin/python \
  -m mlx_voxcpm2.cli cache-generate \
  --model-dir models/VoxCPM2-official-mlx-int8-components \
  --prompt-wav-path /path/prompt.wav \
  --prompt-text "提示音频对应文本。" \
  --text "接下来继续说这一句。" \
  --mode continuation \
  --output benchmarks/continuation.wav
```

Legacy candidate build only:

```bash
cd /Users/vanch/mlx-voxcpm2
python scripts/build_repaired_model.py --variant 8bit
python scripts/build_repaired_model.py --variant bf16
```

Tokenizer parity:

```bash
cd /Users/vanch/mlx-voxcpm2
python scripts/tokenizer_parity.py --candidate models/VoxCPM2-8bit
```

Native official rebuild benchmark:

```bash
cd /Users/vanch/mlx-voxcpm2
PYTHONPATH=/Users/vanch/mlx-voxcpm2 /Users/vanch/mlx-indextts2/.venv/bin/python \
  scripts/benchmark_manifest_runtime.py \
  --model-dir models/VoxCPM2-official-mlx-int8-components \
  --manifest /Users/vanch/mlx-indextts2/outputs/groupchat_crosstalk_20260509_scene_ref/audio/manifest.csv \
  --output-dir benchmarks/native-int8-full \
  --backend native --quantization mlx-int8 --clear-cache-every 8
```

Backend-native batch CLI:

```bash
cd /Users/vanch/mlx-voxcpm2
PYTHONPATH=/Users/vanch/mlx-voxcpm2 /Users/vanch/mlx-indextts2/.venv/bin/python \
  -m mlx_voxcpm2.cli batch \
  --model-dir models/VoxCPM2-official-mlx-int8-components \
  --input /Users/vanch/mlx-indextts2/outputs/groupchat_crosstalk_20260509_scene_ref/audio/manifest.csv \
  --output-dir benchmarks/cli-native-int8 \
  --backend native \
  --combine
```

Latest validated 64-row crosstalk benchmark:

- `native_mlx_int8`: RTF 0.2175, peak active+cache 17.46GB, ASR avg CER 0.0688.
- `native_bf16`: RTF 0.4134, peak active+cache 24.35GB, ASR avg CER 0.0810.
- Summary: `/Users/vanch/mlx-voxcpm2/benchmarks/native-compare/summary.csv`.

## Native Parameters To Preserve

The project currently exposes repair/parity/benchmark scripts around the MLX runtime. Preserve:

- candidate model path
- variant: `mlx-int8`, `bf16`, or legacy `rowwise-int8`
- max tokens
- output directory
- reference audio and prompt text when using the generation path that supports cloning
- native runtime switches: `--backend`, `--compile/--no-compile`,
  `--metal-memory-limit-gb`, `--cache-limit-gb`, `--profile-hotpaths`
- retry controls: `--retry-badcase`, retry count, ratio threshold
- batch controls: `--input`, `--output-dir`, `--combine`,
  `--combine-silence-ms`, `--limit`, `--dynamic-max-len/--no-dynamic-max-len`,
  `--max-len-per-char`, `--min-dynamic-max-len`

## Recommended Use

- Chinese short/long content where wrong words are unacceptable.
- Crosstalk/dialogue comparison against IndexTTS and Qwen TTS.
- Regression testing for tokenizer and ASR fidelity.
- Fair RTF benchmark: reuse the verified clean-reference replay manifest or
  regenerate a matching manifest before comparing against other backends.

If the native official-to-local rebuild is unavailable, block Chinese
production use and switch to `mlx-indextts2`/`mlx-omnivoice` or compare mode
instead of silently using a community model.
