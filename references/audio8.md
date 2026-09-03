# MLX Audio8 TTS (ArkTTS) Reference

Root: `/Users/vanch/mlx-audio8-tts`  
GitHub: `vanch007/mlx-audio8-tts` (based on upstream `Audio8-AI/Audio8_TTS`)  
Hugging Face: `vanch007/Audio8-TTS-MLX-8bit`

## Overview

Audio8 TTS (ArkTTS) is a lightweight 0.6B dual autoregressive (DualAR) speech generation model with a native 44.1 kHz 10-codebook residual neural codec.
The standalone Apple Silicon MLX port runs natively on Metal without `mlx-audio` runtime dependencies, featuring affine 8-bit quantization (`sensitive-bf16` policy) and high-fidelity zero-shot voice cloning.

## Key Capabilities

- **High Sample Rate & Fidelity**: Native 44.1 kHz audio output reconstructed via 10-codebook residual neural codec.
- **Multilingual Support**: Cantonese (粤语 `yue`), Chinese (`zh`), English (`en`), Japanese (`ja`), Korean (`ko`), French (`fr`), German (`de`), Spanish (`es`), Italian (`it`), Dutch (`nl`), Polish (`pl`), and Chinese-English code-switching (`zh_en`).
- **Zero-Shot Voice Cloning**: High-similarity voice cloning from a reference audio prompt (`--ref-audio`) and transcript (`--ref-text`).
- **Cross-Lingual Synthesis**: Clone voice timbre across languages (e.g. English reference speaking Spanish or Japanese).
- **Fast 8-bit Quantization**: 827 MiB LM (2.08 GiB total weights), real-time factor ~0.79–0.98x on Apple Silicon M3 Max.
- **Streaming & Non-Streaming**: Chunked audio generation, CLI, and OpenAI-compatible FastAPI server (`/v1/audio/speech`).

## Command Line Usage

### Voice Cloning (Chinese)

```bash
cd /Users/vanch/mlx-audio8-tts
.venv/bin/python -m mlx_audio8_tts.cli generate \
  --model models/Audio8-TTS-Preview-0.6b-8bit \
  --text "今天下午三点半，上海到北京的高铁票价是553元，订单号是A17-9002。" \
  --ref-audio /Users/vanch/tts-test-project/data/reference_audio/dots_seedtts_zh_ref.wav \
  --ref-text "冬天对于田野和河流来说，是一个放松休息的季节。" \
  --output outputs/zh_numbers.wav
```

### Voice Cloning (English)

```bash
cd /Users/vanch/mlx-audio8-tts
.venv/bin/python -m mlx_audio8_tts.cli generate \
  --model models/Audio8-TTS-Preview-0.6b-8bit \
  --text "The quick brown fox jumps over the lazy dog." \
  --ref-audio /Users/vanch/tts-test-project/data/reference_audio/dots_seedtts_en_ref.wav \
  --ref-text "The CrossLand acquisition gave Washington Mutual a toe hold entry into Oregon via Portland." \
  --output outputs/en_quick.wav
```

### Cantonese Dialect Generation

```bash
cd /Users/vanch/mlx-audio8-tts
.venv/bin/python -m mlx_audio8_tts.cli generate \
  --model models/Audio8-TTS-Preview-0.6b-8bit \
  --text "唔該，我想問下呢度附近有無地鐵站呀？" \
  --ref-audio /Users/vanch/tts-test-project/data/reference_audio/dots_seedtts_zh_ref.wav \
  --ref-text "冬天对于田野和河流来说，是一个放松休息的季节。" \
  --output outputs/cantonese.wav
```

## Python API

```python
from mlx_audio8_tts import Audio8TTS

model = Audio8TTS.from_pretrained("models/Audio8-TTS-Preview-0.6b-8bit")
audio = model.generate(
    text="你好，欢迎使用 Audio8 语音生成模型。",
    ref_audio_path="data/reference.wav",
    ref_text="参考音频文本",
)
model.save_audio("outputs/demo.wav", audio)
```
