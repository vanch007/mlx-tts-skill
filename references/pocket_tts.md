# MLX Pocket TTS Reference

Root: `/Users/vanch/mlx-pocket-tts`  
GitHub: `vanch007/mlx-pocket-tts` (based on upstream `kyutai-labs/pocket-tts`)  
Hugging Face: `vanch007/mlx-pocket-tts`

## Overview

Pocket TTS is an ultra-fast, lightweight streaming text-to-speech and voice cloning model by Kyutai Labs.
The standalone Apple Silicon MLX port is native to Metal without `mlx-audio` or PyTorch inference dependencies,
featuring 8-bit FlowLM, Mimi audio codec, 26 preset voice embeddings, and high-quality zero-shot cloning.

## Key Capabilities

- **Lightweight & High Speed**: Ultra-fast generation with RTF ~0.12–0.17x on Apple Silicon.
- **Multilingual Support**: English (`en`), German (`de`), French (`fr`), Spanish (`es`), Italian (`it`), Portuguese (`pt`), and Czech (`cs`).
- **Zero-Shot Voice Cloning**: Fast reference-based cloning from arbitrary WAV/audio files (`--ref-audio`).
- **26 Preset Voices**: Built-in voice embeddings including `alba`, `marius`, `jean`, `cosette`, `fantine`, `javert`, etc.
- **Long Text & Streaming**: Native chunked streaming generation and long-form narrative stability.
- **Official Web UI & FastAPI**: Native server with in-app browser playback support.

## Command Line Usage

### Standard Preset Voice Generation

```bash
cd /Users/vanch/mlx-pocket-tts
uv run mlx-pocket-tts generate \
  --model vanch007/mlx-pocket-tts \
  --voice alba \
  --text "Hello from Pocket TTS on Apple Silicon." \
  --output outputs/hello.wav
```

### Voice Cloning

```bash
cd /Users/vanch/mlx-pocket-tts
uv run mlx-pocket-tts generate \
  --model vanch007/mlx-pocket-tts \
  --ref-audio /path/to/reference.wav \
  --text "This is a voice cloning test with Pocket TTS." \
  --output outputs/clone.wav
```

### Multilingual Generation

```bash
cd /Users/vanch/mlx-pocket-tts
uv run mlx-pocket-tts generate \
  --config configs/spanish.yaml \
  --voice alba \
  --text "¿Cómo podemos mejorar la calidad del servicio al cliente?" \
  --output outputs/spanish.wav
```

## Python API

```python
from mlx_pocket_tts import TTSModel, write_audio

model = TTSModel.load_model(language="english", quantize=True)
voice_state = model.get_state_for_audio_prompt("alba")
audio = model.generate_audio(voice_state, "Hello from Apple Silicon MLX.")
write_audio("output.wav", audio, model.sample_rate)
```

