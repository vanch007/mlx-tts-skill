---
name: mlx-tts
description: "Unified Apple Silicon MLX speech workflow and source registry for 13 local projects: IndexTTS 2.5/2.0, VoxCPM2, Qwen3-TTS, OmniVoice, Higgs Audio, dots.tts, ZONOS2, Scenema Audio, Ming Omni TTS, MOSS TTS, Supertonic, FireRedAudio, and Breeze TTS 2. Use for local MLX TTS generation, voice cloning or design, audio understanding/QA, speech editing, speech events, multilingual speech, dialogue, batch work, ASR/leakage validation, RTF and listening benchmarks, backend selection, project inventory, or restoring a missing source checkout from GitHub. Do not use for cloud TTS or music-only work with no speech requirement."
---

# MLX TTS Unified Workflow

Default priority: **content fidelity > voice similarity > emotion naturalness > speed**.

Use this skill to preserve each backend's native strengths instead of forcing every task into one generic API.

## Canonical Model Registry

The skill covers exactly 11 benchmark projects. Read
`references/model_catalog.md` for the complete root/GitHub/capability table and
backend entrypoints. Query the machine-readable registry with:

```bash
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/model_registry.py --check --json
```

Canonical keys are: `indextts`, `voxcpm2`, `qwen_tts`, `omnivoice`, `higgs`,
`dots`, `zonos2`, `scenema`, `ming`, `moss`, and `supertonic`.

Before executing a non-trivial task, read the target project's `.ai_project.md` and `.ai_memory.md` if present.

## Backend Status and Evidence Boundary

- Production/default: `mlx-indextts2`, `mlx-omnivoice`.
- `mlx-indextts2` defaults non-Vietnamese work to IndexTTS 2.5 GPT 8-bit at
  `models/mlx-IndexTTS-2.5-8bit` (HF revision
  `d0aa86e75bb6f3437f3831e95056fa72842d89ef`). Its evidenced languages are
  Chinese, English, Japanese, Spanish, and Arabic. Vietnamese remains a
  separate IndexTTS 2.0 local-extension profile and evaluation artifact.
- Performance-verified candidate: `mlx-voxcpm2` native official rebuild.
- Official-lineage candidate: `mlx-qwen3-tts` Base, CustomVoice, and VoiceDesign
  int8 conversions. Use it for comparison, Qwen-style cloning, CustomVoice
  preset speakers, VoiceDesign experiments, and fast replay after ASR/leakage
  checks. Do not silently promote it over IndexTTS2/OmniVoice when separated
  emotion control is required.
- Multi-modal Audio LLM candidate: `mlx-FireRedAudio` (ASR, audio QA with CoT,
  zero-shot TTS, speech editing, voice design).
- Paralinguistic speech events and voice direction candidate: `mlx-breeze-tts2`
  (voice design, voice clone, voice direction, speech events laugh/cough/sigh, streaming).
- The target for VoxCPM2/Qwen3-TTS is: official project inference behavior, official checkpoint component conversion, local MLX runtime, full feature preservation, no `mlx-audio` production runtime.
- The other eight projects are registered operational backends, not implied
  quality winners. Use the shared 13-project evaluation before making ranking
  claims. Supertonic has no evidenced arbitrary reference-clone path, so its
  clone similarity is `not applicable`, not zero.
- Git recovery restores tracked source/configuration only. It does not restore
  weights, caches, virtual environments, generated audio, or secrets.

## Common Control Surface

Extract these fields from the user request or manifest. Do not invent missing file paths.

- `task_type`: `single`, `batch`, `dialogue`, `novel`, `benchmark`, `compare`, `optimize`, `emotion_library`, `asr_check`
- `backend`: one of the 11 canonical registry keys, an accepted alias, or `compare`
- `model_override`: exact model directory, registry id, or CLI model flag
- `language`: `zh`, `en`, `ja`, `es`, `ar`, `vi`, `mixed`, or `auto`
- `speaker_ref`: voice reference audio, speaker cache, or per-row manifest column
- `emotion_ref`: separate emotion reference audio, emotion vector, Qwen auto emotion, or per-row manifest column
- `batch_manifest`: CSV/JSON/text file containing segment rows
- `quality_goal`: `content`, `voice`, `emotion`, `speed`, or weighted custom goal
- `validation`: ASR回读, leakage detection, RTF, manual listening notes
- `output_policy`: per-segment WAVs, merged WAV, manifest CSV, metrics table

Backend-specific options must pass through to the native project. Keep explicit user overrides even if the router would choose a different default.

## Routing Rules

1. If `model_override` or explicit backend is provided, use it unless the request is impossible or unsafe.
2. If the user asks to compare, benchmark, or is unsure, run compare mode across feasible backends.
3. Vietnamese with tone marks routes to `mlx-indextts2` Vietnamese profile.
4. Japanese, Spanish, or Arabic IndexTTS requests use the 2.5 profile with an
   explicit `--language`; English and Spanish auto-detection is ambiguous.
5. Chinese dialogue/crosstalk where text accuracy is the main risk routes to `mlx-indextts2` or `mlx-omnivoice` first; include `mlx-voxcpm2` when the user asks for speed/content-fidelity comparison or accepts candidate audio review.
6. Chinese crosstalk/stage-dialogue where the goal is natural相声 cadence, two-speaker replay, or OmniVoice-specific comparison routes to `mlx-omnivoice`.
7. Voice cloning with Qwen-style ICL, CustomVoice preset speakers, VoiceDesign
   natural-language voice design, replay, or high speed can include
   `mlx-qwen3-tts`; run ASR/leakage checks before production use.
8. Emotion control, separated speaker/emotion references, Vietnamese, novel planning, emotion2vec libraries, and Qwen text emotion route to `mlx-indextts2`.
9. If content fidelity is unknown, generate a short pilot and run ASR回读 before scaling to the full batch.
10. Music/sound effects with speech route to `ming`; explicit quality/speaking-rate
   conditioning routes to `zonos2`; lightweight fixed-style on-device speech
   routes to `supertonic`.

Use `scripts/model_router.py` for deterministic routing notes:

```bash
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/model_router.py \
  --text "你好，今天我们说一段相声。" --task-type dialogue --language zh

python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/model_router.py \
  --list-backends
```

## Workflow

1. Identify task and constraints from the common control surface.
2. Route to a backend or compare mode.
3. Load only the relevant backend reference:
   - IndexTTS: `references/indextts.md`
   - VoxCPM2: `references/voxcpm2.md`
   - Qwen TTS: `references/qwen_tts.md`
   - OmniVoice: `references/omnivoice.md`
   - All 11 projects and source recovery: `references/model_catalog.md`
   - Full loop: `references/workflow.md`
4. Prepare clean references. For cloned voices, prefer vocal-isolated, short, dry speech without music or room noise.
5. For batches, create a manifest and keep segment WAVs plus a merged WAV.
6. Run ASR回读 and leakage checks whenever content fidelity matters.
7. Compare RTF, content score, voice score, emotion score, and failure notes before recommending a final backend.

## Batch Contract

Preferred manifest columns:

```csv
id,speaker,text,language,backend,speaker_ref,emotion_ref,emotion,instruct,expected_text,ref_text,output_wav,notes
```

Use `scripts/batch_manifest.py` to convert dialogue text into a CSV manifest. Use `scripts/stitch_wavs.py` to merge segment WAVs after generation.

Before Qwen3-TTS or OmniVoice clone benchmarks, use
`scripts/enrich_ref_text.py` to add exact `ref_text` from a reference library
catalog. Do not use target text as reference text except for a parser smoke.

```bash
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/enrich_ref_text.py \
  --manifest batch_manifest.csv \
  --catalog /Users/vanch/mlx-indextts2/outputs/fjymb_library_final/catalog.csv \
  --output batch_manifest.with_ref_text.csv \
  --strict
```

Use `scripts/run_backend_benchmark.py` for fair replay through the four
validated backend-native batch CLIs only:

```bash
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/run_backend_benchmark.py \
  --manifest /Users/vanch/mlx-indextts2/outputs/groupchat_crosstalk_20260509_scene_ref/audio/manifest.csv \
  --output-root /Users/vanch/tts_benchmarks/mlx_four_backend_pilot \
  --backends indextts voxcpm2 qwen_tts omnivoice \
  --limit 4 \
  --dry-run
```

When a backend requires a different reference strategy, keep the same text rows
but pass a backend-specific manifest, for example Qwen3-TTS clean ICL refs:

```bash
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/run_backend_benchmark.py \
  --manifest shared_manifest.csv \
  --qwen-manifest /Users/vanch/mlx-qwen3-tts/outputs/official_int8_replay_manifest_icl_cleanrefs_v4.json \
  --output-root outputs/compare_with_qwen_cleanrefs \
  --backends indextts voxcpm2 qwen_tts omnivoice
```

Validated smoke outputs:

- VoxCPM2 native batch:
  `/Users/vanch/tts_benchmarks/mlx_runner_voxcpm2_smoke_20260512/summary.json`
- Four-backend runner, 1-row smoke:
  `/Users/vanch/tts_benchmarks/mlx_four_backend_smoke2_20260512/summary.json`
- Four-backend 8-row pilot with ASR report:
  `/Users/vanch/tts_benchmarks/mlx_four_backend_pilot8_fixed_20260512/report.md`

For the complete 11-project benchmark roster, use the benchmark project rather
than extending the four-backend runner ad hoc:

```bash
python /Users/vanch/tts-test-project/scripts/run_local_open_tts_matrix.py --help
```

Direct text generation and reference voice cloning are separate capabilities
and test cases. Compute speaker similarity only when a valid reference is paired
with a backend that actually performs reference cloning.

IndexTTS evaluation must use `mlx_indextts2_v25_8bit` for the 2.5 artifact and
`mlx_indextts2_vietnamese_8bit` for Vietnamese 2.0. Never relabel historical
`mlx_indextts2_standard_8bit` rows as 2.5 without regeneration.

## Missing Project Recovery

Preview recovery before writing:

```bash
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/model_registry.py \
  --ensure scenema --dry-run --json
```

Clone one missing source tree, or every missing source tree:

```bash
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/model_registry.py --ensure scenema
python /Users/vanch/.skills-manager/skills/mlx-tts/scripts/model_registry.py --ensure-all
```

The script never overwrites a non-empty non-Git directory. All 11 registered
source repositories are public as of the latest registry review.

## Optimization Loop

Use the smallest loop that can prove the improvement:

1. Pilot: one short segment per speaker/emotion.
2. Diagnose: ASR mismatch, leaked reference text, wrong speaker, emotion bleed, noise tail, pause, RTF.
3. Change exactly one axis: backend, model variant, reference cleanup, segment length, sampling params, emotion source, or stitching.
4. Rerun pilot and compare metrics.
5. Scale to batch only after the pilot passes.

Never solve generated silence or wrong text by simply trimming output unless the root cause is already identified. Trimming is only a post-process cleanup step.

## Fair Benchmark Rules

- Use the same script/manifest, reference set, row count, and generation mode
  when comparing backends.
- Do not compare IndexTTS2 `emotion_ref_audio` runs against speaker-only
  Qwen/VoxCPM2/OmniVoice runs as if they were the same workload.
- For OmniVoice/VoxCPM2, only use exact `ref_text` for the paired `ref_audio`;
  approximate prompt transcripts can create extra spoken content.
- For VoxCPM2, strip per-line `instruct` during normal voice-cloning
  benchmarks; otherwise the run is not comparable to the verified clean-ref
  replay.
- Report whether RTF includes warmup/model loading/reference preprocessing. For
  short batches, also report steady-state RTF after the first 3-5 rows.
- Prefer validated backend-native replay paths over ad hoc scripts for final
  benchmark numbers.

## Output Requirements

For generation tasks, report:

- backend and model path/variant
- reference files used and whether cleanup was applied
- output directory, merged WAV path, and manifest path
- RTF and audio duration when available
- ASR/leakage result when run
- unresolved risks or skipped validation

For project recovery tasks, report the repository, destination, checked-out
commit, and explicitly state that model weights were not restored by Git.

## Skill Governance

- Owner: `vanch`
- Trigger: Apple Silicon MLX speech generation, cloning/design, batch,
  comparison, validation, project inventory, and source recovery for the 11
  registered projects.
- Non-trigger: ASR-only tasks, cloud TTS, non-MLX speech stacks, and music-only
  generation without a speech requirement.
- Output contract: selected backend/model, inputs/references, output paths,
  timing/validation evidence, and unresolved risks; recovery tasks additionally
  report repository/destination/commit and weight status.
- Resources: backend references, `references/model_catalog.md`, registry/router,
  manifest, stitching, ASR, comparison, and four-backend runner scripts.
- Evals: skill unit tests plus the external shared benchmark/listening report.
- Trust boundary: local files and GitHub source are inspectable evidence; model
  capability and quality claims require backend tests and benchmark evidence.
- Maturity: local operational. Individual backend quality remains evidence-bound
  and may be `pending` when weights or evaluation data are missing.
- Review cadence: after any benchmark-roster change and at least quarterly.
- Target platform: Apple Silicon macOS with Codex and backend-native runtimes.
