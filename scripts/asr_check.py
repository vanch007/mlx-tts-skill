#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from difflib import SequenceMatcher
from pathlib import Path


PUNCT_RE = re.compile(r"[\s，。！？、,.!?;:：；「」『』“”\"'（）()【】\[\]《》<>…—_-]+")


def norm(text: str) -> str:
    return PUNCT_RE.sub("", (text or "").lower())


def similarity(a: str, b: str) -> float:
    aa = norm(a)
    bb = norm(b)
    if not aa and not bb:
        return 1.0
    if not aa or not bb:
        return 0.0
    return SequenceMatcher(None, aa, bb).ratio()


def run_asr(command_template: str, audio: str) -> str:
    command = command_template.format(audio=audio)
    result = subprocess.run(command, shell=True, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Score ASR content fidelity and reference-text leakage for TTS manifests.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--asr-command", help="Optional shell template with {audio}; stdout must be transcript")
    parser.add_argument("--content-threshold", type=float, default=0.85)
    parser.add_argument("--leakage-threshold", type=float, default=0.65)
    args = parser.parse_args()

    with args.manifest.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit("manifest has no rows")

    scored = []
    for row in rows:
        audio = (row.get("output_wav") or row.get("wav_path") or row.get("audio_path") or "").strip()
        expected = row.get("expected_text") or row.get("text") or ""
        ref_text = row.get("ref_text") or row.get("reference_text") or ""
        asr_text = row.get("asr_text") or ""
        if args.asr_command and audio and not asr_text:
            asr_text = run_asr(args.asr_command, audio)
        content_score = similarity(expected, asr_text)
        leakage_score = similarity(ref_text, asr_text) if ref_text else 0.0
        out = dict(row)
        out.update(
            {
                "asr_text": asr_text,
                "content_score": f"{content_score:.4f}",
                "leakage_score": f"{leakage_score:.4f}",
                "content_pass": str(content_score >= args.content_threshold),
                "leakage_pass": str(leakage_score < args.leakage_threshold or not ref_text),
            }
        )
        scored.append(out)

    content_values = [float(row["content_score"]) for row in scored]
    leakage_values = [float(row["leakage_score"]) for row in scored]
    summary = {
        "rows": len(scored),
        "avg_content_score": sum(content_values) / len(content_values),
        "max_leakage_score": max(leakage_values) if leakage_values else 0.0,
        "content_failures": sum(row["content_pass"] == "False" for row in scored),
        "leakage_failures": sum(row["leakage_pass"] == "False" for row in scored),
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(scored[0].keys()))
            writer.writeheader()
            writer.writerows(scored)
    if args.json:
        print(json.dumps({"summary": summary, "rows": scored}, ensure_ascii=False, indent=2))
    else:
        print(
            "rows={rows} avg_content_score={avg_content_score:.4f} "
            "max_leakage_score={max_leakage_score:.4f} "
            "content_failures={content_failures} leakage_failures={leakage_failures}".format(**summary)
        )


if __name__ == "__main__":
    main()

