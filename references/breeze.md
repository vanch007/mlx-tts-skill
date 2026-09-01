# MLX Breeze TTS 2 Reference

Root: `/Users/vanch/mlx-breeze-tts2`  
GitHub: `vanch007/mlx-breeze-tts2` (based on upstream `BreezeBlue/Breeze-TTS-2`)

## Overview

Breeze TTS 2 is a high-quality Chinese and English speech generation model by MediaTek Research.
The standalone MLX port is native to Apple Silicon Metal without `mlx-audio` dependencies,
featuring T5Gemma2 text encoding, an autoregressive Qwen3 backbone for Codebook 0, and a LLaMA-style depth decoder for the remaining codec codebooks.

## Key Capabilities

- **Voice design**: natural language timbre description prompt (`--instruction`).
- **Zero-shot voice cloning**: prompt audio with exact transcript (`--ref-audio` + `--ref-text`).
- **Voice direction**: combines reference voice identity with stylistic instruction.
- **Paralinguistic speech events**: English `(laugh)` / `(cough)` / `(clears throat)` / `(sigh)` and Chinese `[笑]` / `[咳嗽]` / `[清嗓子]` / `[叹气]`.
- **Long text stability**: multi-sentence continuity without dropped clauses.
- **Fast streaming & non-streaming generation**.

## Command Line Usage

### Voice Design

```bash
cd /Users/vanch/mlx-breeze-tts2
.venv/bin/python -m mlx_breeze_tts.cli generate \
  --model models/breeze-8bit-sensitive-bf16-v2 \
  --text "欢迎来到今晚的故事时间。" \
  --instruction "一位温柔自信的年轻女性，声音清晰，语气亲切。" \
  --output outputs/voice_design.wav
```

### Voice Clone

```bash
cd /Users/vanch/mlx-breeze-tts2
.venv/bin/python -m mlx_breeze_tts.cli generate \
  --model models/breeze-8bit-sensitive-bf16-v2 \
  --ref-audio /path/to/reference.wav \
  --ref-text "参考音频的准确文本" \
  --text "请使用参考音色清晰自然地朗读这段内容。" \
  --output outputs/voice_clone.wav
```

### Speech Events

```bash
cd /Users/vanch/mlx-breeze-tts2
.venv/bin/python -m mlx_breeze_tts.cli generate \
  --model models/breeze-8bit-sensitive-bf16-v2 \
  --text "(laugh) You really got me. I did not see that coming at all." \
  --output outputs/event_laugh.wav
```

