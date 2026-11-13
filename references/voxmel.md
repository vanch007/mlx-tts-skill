# VoxMel (MLX)

## Architecture & Method

- Project: `mlx-voxmel` (GitHub: `vanch007/mlx-voxmel`)
- Model Lineage: VoxDance-Lab/VoxMel (0.6B GRPO & 0.3B)
- Acoustic Modeling: Wavelet-Factorized Continuous Autoregressive Mel-Spectrogram Modeling
- Frontend: Qwen2.5 Tokenizer
- Mel Decomposition: Fixed 2-axis Haar wavelet transform (temporal & frequency splits) into Coarse-Mel, Temporal Residual, and Frequency Residual tiers
- Backbone: Qwen2 causal transformer + Continuous FlowMatchingHead
- Residual Prediction: UpsampleTier with Bidirectional Attention + Flow Matching
- Vocoder: Pure MLX Vocos 24kHz ISTFT neural vocoder (zero PyTorch/torchcodec dependency)
- Features: 100-channel log-mel, 1024-point FFT/window, 256 hop length at 24 kHz

## Supported Capabilities

- **Zero-Shot Voice Cloning**: High-fidelity cloning from prompt audio and exact prompt transcript
- **Supported Languages**: Chinese (`zh`) and English (`en`)
- **Cross-Lingual Voice Transfer**: Chinese speaker speaking English (`zh -> en`), English speaker speaking Chinese (`en -> zh`)
- **Dual-Guidance Flow Matching**: Independent text guidance (`cfg_text_strength`, default 3.5) and speaker guidance (`cfg_spk_strength`, default 3.0)
- **Bounded Duration**: Dynamic min/max duration control (`min_seconds`, `max_seconds`) and trained `stop_token_head` stopping prediction
- **Real-Time Factor (RTF)**:
  - 8-bit quantization achieves **0.67 - 0.80 RTF** on Apple Silicon Metal GPU unified memory
  - 100% text accuracy verified by local ASR (`Confucius4-R2T2-8bit`)

## CLI & Entrypoint

```bash
cd /Users/vanch/mlx-voxmel
python inference.py \
  --model models/VoxMel-0.6B-8bit \
  --prompt-audio demo_samples/zh_test_01/prompt.wav \
  --prompt-text "对,这就是我万人敬仰的太乙真人" \
  --text "我身上的肉，是为了掩饰我爆棚的魅力，懂不懂？" \
  --output out.wav \
  --steps 32 --up-steps 32
```

