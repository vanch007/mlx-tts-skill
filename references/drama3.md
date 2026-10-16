# MLX Drama 3 (Fish Audio) Reference

Root: `/Users/vanch/drama-3-mlx`  
GitHub: `vanch007/drama-3-mlx` (based on upstream `fishaudio/fish-speech` & `fishaudio/drama-3`)  
Hugging Face: `vanch007/Drama-3-MLX-4bit` (also 8-bit & BF16 releases)

## Overview

Drama 3 is Fish Audio's next-generation conversational text-to-speech model featuring a **35B parameter (3B active)** Mixture-of-Experts (MoE) text backbone with hybrid linear/full attention and a **10-codebook Codebook-MTP audio decoder**.
The standalone Apple Silicon MLX port is native to Metal with zero PyTorch dependencies at runtime, featuring affine 4-bit quantization, 44.1kHz Modded DAC audio codec, multi-speaker conversational dialogue, and in-text emotional point tags.

## Key Capabilities

- **35B MoE Hybrid Architecture**: 40 layers (30 linear attention GatedDeltaNet + 10 full attention layers), 256 experts top-8 with shared expert.
- **Codebook-MTP Audio Decoder**: 10 codebooks predicted via 13-layer causal Transformer tower (4 shared layers + 9 residual codebook layers) with RAS (Repetition-Aware Sampling).
- **44.1kHz Modded DAC Neural Codec**: High-fidelity broadcast-grade audio output.
- **Zero-Shot Voice Cloning**: Prompt-conditioned voice cloning from arbitrary reference WAV and transcript.
- **Multi-Speaker Characters**: Supports native tags `<|speaker:0|>` through `<|speaker:15|>` allowing up to 16 distinct character voices within one seamless dialogue.
- **Paralinguistic & Emotion Point Tags**: In-text cues such as `[sighs]`, `[laughs]`, `[whispers]`, `[giggles]`, `[yawns]`, `[groans]`.
- **Multilingual Coverage**: Chinese (`zh`), English (`en`), Japanese (`ja`), Korean (`ko`), Spanish (`es`), French (`fr`), German (`de`), Italian (`it`), Russian (`ru`), Portuguese (`pt`), Cantonese (`yue`), and Chinese-English code-switching (`zh_en`).
- **Streaming & HTTP Serving**: Chunked streaming generation, CLI, and dual OpenAI (`/v1/audio/speech`) + Fish Audio (`/v1/tts`) API server.

## Command Line Usage

### Plain Text-to-Speech

```bash
cd /Users/vanch/drama-3-mlx
.venv/bin/drama3-mlx tts \
  --model models/drama-3-mlx-4bit \
  --text "你好，这是 Fish Audio Drama 3 在 Apple Silicon 上的纯 MLX 推理测试。" \
  --output outputs/sample.wav
```

### Zero-Shot Voice Cloning

```bash
cd /Users/vanch/drama-3-mlx
.venv/bin/drama3-mlx tts \
  --model models/drama-3-mlx-4bit \
  --text "Please read this sentence with the exact timbre and style of the reference speaker." \
  --ref-audio /path/to/reference.wav \
  --ref-text "Exact transcript of reference audio." \
  --output outputs/cloned.wav
```

### Multi-Speaker Dialogue

```bash
cd /Users/vanch/drama-3-mlx
.venv/bin/drama3-mlx tts \
  --model models/drama-3-mlx-4bit \
  --text "<|speaker:0|> 侦探先生，你觉得凶手会是谁？ <|speaker:1|> [sighs] 从现场的痕迹来看，事情绝不简单。" \
  --output outputs/dialogue.wav
```

## Python API

```python
from drama3_mlx.model import Drama3Model
import soundfile as sf

model = Drama3Model.from_pretrained("models/drama-3-mlx-4bit")
audio = model.tts(
    "<|speaker:0|> Hello world! <|speaker:1|> [laughs] It works amazingly well!",
    ref_audio="data/ref.wav",
    ref_text="Reference text.",
)
sf.write("output.wav", audio, 44100)
```
