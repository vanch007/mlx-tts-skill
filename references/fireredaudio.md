# MLX FireRedAudio Reference

Root: `/Users/vanch/mlx-FireRedAudio`  
GitHub: `vanch007/mlx-FireRedAudio` (based on upstream `FireRedTeam/FireRedAudio`)

## Overview

FireRedAudio is a general-purpose audio language model with decoupled continuous
representations for understanding and generation. It integrates ASR, audio understanding /
QA (with optional CoT thinking), zero-shot voice cloning (TTS), speech editing (acoustic /
semantic), and natural language voice design into a single MLX-native model.

## Model Architecture

- **LLM Backbone**: Qwen3.5 hybrid architecture with GatedDeltaNet + Attention layers (9B parameters).
- **Audio Tokenizer / Codec**: RedAE (continuous representation audio autoencoder) with MLX-native ISTFT decoder (24 kHz).
- **Patch Encoder**: Projects continuous VAE latents to LLM embedding space.
- **DiT Flow Matching**: Continuous diffusion transformer for speech synthesis.
- **Inference Runtime**: 100% native Apple Silicon MLX Metal kernels; zero PyTorch / CUDA runtime dependencies.

## Models and Checkpoints

- **8-bit (Recommended baseline)**: `models/FireRedAudio-8bit` (~13.5 GB)
- **4-bit (Ultra-lightweight)**: `models/FireRedAudio-4bit` (~9.8 GB)
- **BF16 (Original)**: `models/FireRedAudio` (~20.5 GB)

## Capabilities & Usage

### 1. ASR (Speech Recognition)

High-accuracy multilingual speech transcription with Greedy/Beam search:

```bash
cd /Users/vanch/mlx-FireRedAudio
.venv/bin/python inference.py --task asr --model models/FireRedAudio-8bit --audio input.wav
```

### 2. Audio Understanding / QA (with CoT Thinking)

Audio reasoning and question answering:

```bash
cd /Users/vanch/mlx-FireRedAudio
.venv/bin/python inference.py --task understand --model models/FireRedAudio-8bit \
    --audio two_speakers.wav --prompt "这个音频中有几个说话人？" --enable-thinking
```

### 3. Zero-shot Voice Cloning (TTS)

In-context learning voice cloning from prompt audio and transcript:

```bash
cd /Users/vanch/mlx-FireRedAudio
.venv/bin/python inference.py --task tts --model models/FireRedAudio-8bit \
    --prompt-audio prompt.wav --prompt-text "提示音频的转写文本" \
    --target-text "需要合成的目标文本" --language zh --output output.wav
```

### 4. Voice Design

Natural language timbre description guided synthesis without reference audio:

```bash
cd /Users/vanch/mlx-FireRedAudio
.venv/bin/python inference.py --task voice_design --model models/FireRedAudio-8bit \
    --instruction "温柔清晰的播音女声" --text "需要朗读的文本" --output output.wav
```

### 5. Speech Editing

Acoustic (speed/pitch/volume) or semantic text rewrite:

```bash
cd /Users/vanch/mlx-FireRedAudio
.venv/bin/python inference.py --task edit --model models/FireRedAudio-8bit \
    --audio input.wav --instruction "adjust the speed to 0.5" --edit-type acoustic
```

## WebUI Studio

FastAPI + React 18 / Vite SPA with real-time SSE streaming:

```bash
cd /Users/vanch/mlx-FireRedAudio
.venv/bin/python run_webui.py --model models/FireRedAudio-8bit --port 7860
```

## Benchmark Findings & Evaluation Boundary (2026-08-22)

- **ASR & Audio Understanding**: Highly capable, accurate transcription and reasoning on Apple Silicon M3 Max.
- **TTS Generation**: In the current 8-bit MLX port, continuous DiT generation exhibits semantic drift / hallucination on arbitrary long text benchmarks; ASR CER is high (~0.92-1.0).
- **Primary Use**: Best suited for speech transcription, audio reasoning, and experimental voice design / editing workflows; for production high-accuracy TTS, prefer dedicated TTS models like IndexTTS 2.5, VoxCPM2, or Higgs Audio.

