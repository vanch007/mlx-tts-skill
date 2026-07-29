# MLX TTS Model Catalog

This catalog is the operational inventory for the 11 projects in the local
benchmark roster. Capability claims are intentionally narrow: confirm final
quality with the shared benchmark and listening review.

## Canonical Projects

| Key | Project | Local root | GitHub | Clone | Primary role |
|---|---|---|---|---|---|
| `indextts` | `mlx_indextts2` | `/Users/vanch/mlx-indextts2` | `vanch007/mlx-indextts2` | yes | multilingual cloning, separated emotion control, batch planning |
| `voxcpm2` | `mlx_voxcpm2` | `/Users/vanch/mlx-voxcpm2` | `vanch007/mlx-voxcpm2` | yes | native MLX cloning and fidelity comparison |
| `qwen_tts` | `mlx_qwen3_tts` | `/Users/vanch/mlx-qwen3-tts` | `vanch007/mlx-qwen3-tts` | yes | ICL clone, presets, and natural-language voice design |
| `omnivoice` | `mlx_omnivoice` | `/Users/vanch/mlx-omnivoice` | `vanch007/mlx-omnivoice` | yes | Chinese dialogue and crosstalk |
| `higgs` | `mlx_higgs_audio` | `/Users/vanch/mlx-higgs-audio` | `vanch007/mlx-higgs-audio` | yes | expressive reference cloning and long-form redubbing |
| `dots` | `mlx_dots_tts` | `/Users/vanch/mlx-dots.tts` | `vanch007/mlx-dots-tts` | yes | prompt-audio cloning and long text |
| `zonos2` | `mlx_zonos2` | `/Users/vanch/mlx-ZONOS2` | `vanch007/mlx-ZONOS2` | yes | clone plus conditioning controls |
| `scenema` | `mlx_scenema_audio` | `/Users/vanch/mlx-scenema-audio` | `vanch007/mlx-scenema-audio` | yes | voice design, clone, and action tags |
| `ming` | `mlx_ming_omni_tts` | `/Users/vanch/mlx-Ming-omni-tts` | `vanch007/mlx-Ming-omni-tts` | design | large speech/music/sound and voice-design model |
| `moss` | `mlx_moss_tts` | `/Users/vanch/mlx-MOSS-TTS-Local-Transformer-v1.5` | `vanch007/mlx-MOSS-TTS-Local-Transformer-v1.5` | yes | multilingual clone, style, and streaming |
| `supertonic` | `mlx_supertonic` | `/Users/vanch/mlx-supertonic` | `vanch007/mlx-supertonic` | no | lightweight fixed-style on-device voices |

All 11 source repositories are public. Do not label Supertonic output as voice
cloning: its checked project path provides fixed voice styles, not arbitrary
reference speaker cloning.

## Source Recovery

Inspect all roots:

```bash
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/model_registry.py --check --json
```

Preview or restore one missing project:

```bash
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/model_registry.py \
  --ensure scenema --dry-run --json
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/model_registry.py \
  --ensure scenema
```

Restore all missing source trees:

```bash
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/model_registry.py --ensure-all
```

The recovery script refuses to overwrite a non-empty non-Git directory. Git
restores source and tracked configuration only. Model weights, Hugging Face
caches, generated audio, secrets, and local virtual environments must be
restored separately according to each project's README and `.ai_project.md`.

## Additional Backend Entrypoints

Always read the target project's current README and `.ai_project.md` before a
real generation. These commands identify the currently checked local entrypoint,
but model arguments and paths remain project-specific.

### Higgs Audio

```bash
cd /Users/vanch/mlx-higgs-audio
.venv/bin/python scripts/run_tts.py --help
```

Use for reference cloning, expressive control, or long-form redub comparison.

### dots.tts

```bash
cd /Users/vanch/mlx-dots.tts
./start.sh
```

The local project defaults to its full int8-g64 path. Keep prompt-audio and
target-text roles distinct during clone evaluation.

### ZONOS2

```bash
cd /Users/vanch/mlx-ZONOS2
./start.sh
```

The API server defaults to port 1920. Generation requires a complete local
`mlx-community/descript-audio-codec-44khz` DAC checkpoint; a source clone alone
does not satisfy this dependency.

### Scenema Audio

Use the FastAPI/Uvicorn server documented in the project. Its main speech engine
is MLX, while some post-processing uses PyTorch/MPS. Keep voice design, direct
TTS, and reference cloning as separate benchmark capabilities.

### Ming Omni TTS

```bash
cd /Users/vanch/mlx-Ming-omni-tts
python -m mlx_ming.pipeline --help
```

The checked project uses the `inclusionAI/Ming-omni-tts-16.8B-A3B` model family.
This is a large voice-design/omni-audio backend; do not assume it is a small
reference-clone replacement.

### MOSS TTS

```bash
cd /Users/vanch/mlx-MOSS-TTS-Local-Transformer-v1.5
python -m mlx_moss_tts_local.cli --help
```

The local runtime supports multilingual cloning, style, and streaming paths.
Generation requires all local `MOSS-Audio-Tokenizer-v2` shards.

### Supertonic

```bash
cd /Users/vanch/mlx-supertonic/py
uv run python example_mlx.py
```

Use for lightweight fixed-voice comparison. Voice-clone similarity is not
applicable unless the project later gains an evidenced reference-clone path.

## Benchmark Boundary

`scripts/run_backend_benchmark.py` is the validated native manifest runner for
only the original four backends: IndexTTS2, VoxCPM2, Qwen3-TTS, and OmniVoice.
It must not be presented as an 11-backend runner.

For the complete benchmark roster use:

```bash
python /Users/vanch/tts-test-project/scripts/run_local_open_tts_matrix.py --help
```

Keep direct text generation and reference voice cloning as separate test cases.
Apply speaker-similarity scores only to runs with a valid paired reference and
an actual cloning capability.
