# FireRedAudio (MLX Native)

Root: `/Users/vanch/mlx-FireRedAudio`

## Overview

FireRedAudio is an open-weight multi-modal audio large language model by Xiaohongshu (FireRedTeam).
The local MLX port is fully native with Apple Silicon Metal acceleration, supporting ASR, Audio QA with CoT reasoning, Zero-shot TTS, Speech Editing, and Voice Design.

## Benchmark Status & Verified Boundary (2026-08-22 Fixed Evaluation)

- Artifact ID: `mlx_fireredaudio_8bit`
- Model checkpoint: `models/FireRedAudio-8bit` (13.5 GB footprint)
- TTS Content Accuracy: **CER = 0.0000 on 10/14 formal benchmark cases** (including Chinese/English reading, numbers, same-language cloning, 3s short cloning, voice design, character cloning, and English long-form).
- Speaker Similarity: **SpeechBrain ECAPA cosine 0.71 ~ 0.94** on voice clone cases; overall speaker clone robustness score **82.235**.
- Naturalness Quality (UTMOS): **2.6 ~ 4.2** on voice clone and long-form samples.
- Generation Speed: RTF **1.4 ~ 1.8** on balanced M3 Max inference.
- Non-speech Core Strengths: ASR RTF **0.138** (7x faster than real-time); Audio QA with Chain-of-Thought thinking.

## Key Entrypoints

### Single TTS Generation (Zero-shot Voice Clone)

```bash
cd /Users/vanch/mlx-FireRedAudio
.venv/bin/python inference.py --task tts \
    --model models/FireRedAudio-8bit \
    --prompt-audio assets/examples/tts_zh_prompt.wav \
    --prompt-text "收到你的来信，我很高兴。" \
    --target-text "你好，欢迎使用 FireRedAudio MLX 版本！" \
    --language zh \
    --output outputs/tts_output.wav
```

### Voice Design (Natural Language Timbre Synthesis)

```bash
cd /Users/vanch/mlx-FireRedAudio
.venv/bin/python inference.py --task voice_design \
    --model models/FireRedAudio-8bit \
    --instruction "温柔清晰的播音女声" \
    --text "这是通过音色描述直接生成的语音。" \
    --output outputs/voice_design.wav
```

### ASR Transcription & Audio QA

```bash
cd /Users/vanch/mlx-FireRedAudio
# ASR (RTF ~ 0.14)
.venv/bin/python inference.py --task asr --model models/FireRedAudio-8bit --audio assets/examples/asr_zh_fleurs.wav

# Audio QA with Thinking
.venv/bin/python inference.py --task understand --model models/FireRedAudio-8bit \
    --audio assets/examples/two_speakers.wav --prompt "这个音频中有几个说话人？" --enable-thinking
```

### WebUI Studio

```bash
cd /Users/vanch/mlx-FireRedAudio
.venv/bin/python run_webui.py --model models/FireRedAudio-8bit --port 7860
```

