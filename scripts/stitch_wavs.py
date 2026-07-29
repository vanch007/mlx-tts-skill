#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import wave
from pathlib import Path


def wavs_from_manifest(path: Path) -> list[Path]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    paths: list[Path] = []
    for row in rows:
        value = row.get("output_wav") or row.get("wav_path") or row.get("audio_path") or ""
        value = value.strip()
        if value:
            p = Path(value)
            if not p.is_absolute():
                p = path.parent / p
            paths.append(p)
    return paths


def read_wav(path: Path) -> tuple[wave._wave_params, bytes]:
    with wave.open(str(path), "rb") as wf:
        params = wf.getparams()
        data = wf.readframes(wf.getnframes())
    return params, data


def silence(params: wave._wave_params, gap_ms: int) -> bytes:
    if gap_ms <= 0:
        return b""
    frames = int(params.framerate * gap_ms / 1000)
    return b"\x00" * frames * params.nchannels * params.sampwidth


def stitch(paths: list[Path], output: Path, gap_ms: int = 0) -> None:
    if not paths:
        raise SystemExit("No WAV files provided")
    params0, data0 = read_wav(paths[0])
    chunks = [data0]
    gap = silence(params0, gap_ms)
    for path in paths[1:]:
        params, data = read_wav(path)
        comparable = (params.nchannels, params.sampwidth, params.framerate, params.comptype)
        expected = (params0.nchannels, params0.sampwidth, params0.framerate, params0.comptype)
        if comparable != expected:
            raise SystemExit(f"WAV format mismatch: {path} has {comparable}, expected {expected}")
        if gap:
            chunks.append(gap)
        chunks.append(data)
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as wf:
        wf.setparams(params0)
        wf.writeframes(b"".join(chunks))


def main() -> None:
    parser = argparse.ArgumentParser(description="Stitch per-segment WAV files into one WAV.")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--gap-ms", type=int, default=0)
    parser.add_argument("wavs", nargs="*", type=Path)
    args = parser.parse_args()

    paths = list(args.wavs)
    if args.manifest:
        paths.extend(wavs_from_manifest(args.manifest))
    paths = [p for p in paths if p.exists()]
    stitch(paths, args.output, gap_ms=args.gap_ms)
    print(args.output)


if __name__ == "__main__":
    main()

