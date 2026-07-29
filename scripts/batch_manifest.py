#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROLE_RE = re.compile(r"^\s*([^:：]{1,32})\s*[:：]\s*(.+?)\s*$")
FIELDNAMES = [
    "id",
    "speaker",
    "text",
    "language",
    "backend",
    "speaker_ref",
    "emotion_ref",
    "emotion",
    "instruct",
    "expected_text",
    "ref_text",
    "output_wav",
    "notes",
]


def parse_map(values: list[str] | None, option: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in values or []:
        if "=" not in raw:
            raise SystemExit(f"{option} expects ROLE=PATH, got: {raw}")
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            raise SystemExit(f"{option} expects non-empty ROLE=PATH, got: {raw}")
        out[key] = value
    return out


def read_segments(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        match = ROLE_RE.match(text)
        if match:
            rows.append((match.group(1).strip(), match.group(2).strip()))
        else:
            rows.append(("", text))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a portable MLX TTS batch manifest from dialogue/plain text.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--backend", default="")
    parser.add_argument("--language", default="auto")
    parser.add_argument("--default-speaker", default="")
    parser.add_argument("--default-speaker-ref", default="")
    parser.add_argument("--default-emotion-ref", default="")
    parser.add_argument("--speaker-ref", action="append", help="ROLE=PATH; repeatable")
    parser.add_argument("--emotion-ref", action="append", help="ROLE=PATH; repeatable")
    parser.add_argument("--instruct", default="")
    args = parser.parse_args()

    speaker_refs = parse_map(args.speaker_ref, "--speaker-ref")
    emotion_refs = parse_map(args.emotion_ref, "--emotion-ref")
    segments = read_segments(args.input)
    if not segments:
        raise SystemExit(f"No text segments found in {args.input}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for idx, (speaker, text) in enumerate(segments, start=1):
            speaker = speaker or args.default_speaker
            writer.writerow(
                {
                    "id": f"{idx:04d}",
                    "speaker": speaker,
                    "text": text,
                    "language": args.language,
                    "backend": args.backend,
                    "speaker_ref": speaker_refs.get(speaker, args.default_speaker_ref),
                    "emotion_ref": emotion_refs.get(speaker, args.default_emotion_ref),
                    "emotion": "",
                    "instruct": args.instruct,
                    "expected_text": text,
                    "ref_text": "",
                    "output_wav": "",
                    "notes": "",
                }
            )
    print(args.output)


if __name__ == "__main__":
    main()

