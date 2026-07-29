#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_input(raw: str) -> tuple[str, Path]:
    if "=" not in raw:
        raise SystemExit(f"--input expects BACKEND=CSV, got: {raw}")
    name, path = raw.split("=", 1)
    return name.strip(), Path(path.strip())


def to_float(value: str | None, default: float = 0.0) -> float:
    try:
        return float(value) if value not in (None, "") else default
    except ValueError:
        return default


def average(values: list[float], default: float = 0.0) -> float:
    return sum(values) / len(values) if values else default


def load_scores(path: Path) -> dict[str, float]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return {"content": 0.0, "voice": 0.0, "emotion": 0.0, "rtf": 999.0, "rows": 0}
    return {
        "content": average([to_float(r.get("content_score")) for r in rows]),
        "voice": average([to_float(r.get("voice_score")) for r in rows], default=0.5),
        "emotion": average([to_float(r.get("emotion_score")) for r in rows], default=0.5),
        "rtf": average([to_float(r.get("rtf"), 999.0) for r in rows], default=999.0),
        "rows": len(rows),
    }


def score(row: dict[str, float], weights: dict[str, float]) -> float:
    speed_score = 1.0 / max(row["rtf"], 0.05)
    speed_score = min(speed_score, 1.0)
    return (
        row["content"] * weights["content"]
        + row["voice"] * weights["voice"]
        + row["emotion"] * weights["emotion"]
        + speed_score * weights["speed"]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare MLX TTS backend output metrics.")
    parser.add_argument("--input", action="append", required=True, help="BACKEND=metrics.csv; repeatable")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--content-weight", type=float, default=0.45)
    parser.add_argument("--voice-weight", type=float, default=0.25)
    parser.add_argument("--emotion-weight", type=float, default=0.20)
    parser.add_argument("--speed-weight", type=float, default=0.10)
    args = parser.parse_args()

    weights = {
        "content": args.content_weight,
        "voice": args.voice_weight,
        "emotion": args.emotion_weight,
        "speed": args.speed_weight,
    }
    rows = []
    for raw in args.input:
        backend, path = parse_input(raw)
        metrics = load_scores(path)
        metrics["backend"] = backend
        metrics["score"] = score(metrics, weights)
        rows.append(metrics)
    rows.sort(key=lambda item: item["score"], reverse=True)

    lines = [
        "| rank | backend | score | content | voice | emotion | rtf | rows |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(rows, start=1):
        lines.append(
            f"| {idx} | {row['backend']} | {row['score']:.4f} | {row['content']:.4f} | "
            f"{row['voice']:.4f} | {row['emotion']:.4f} | {row['rtf']:.4f} | {int(row['rows'])} |"
        )
    table = "\n".join(lines)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(table + "\n", encoding="utf-8")
    print(table)


if __name__ == "__main__":
    main()

