#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def _load_catalog(path: Path, *, library_root: Path | None = None) -> dict[str, str]:
    mapping: dict[str, str] = {}
    root = library_root or path.parent
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            sentence = (row.get("sentence") or "").strip()
            clip_path = (row.get("clip_path") or "").strip()
            if not sentence or not clip_path:
                continue
            candidates = {clip_path, Path(clip_path).name}
            resolved = (root / clip_path).resolve()
            candidates.add(str(resolved))
            for key in candidates:
                mapping[key] = sentence
    return mapping


def _lookup_ref_text(ref_audio: str, mapping: dict[str, str]) -> str:
    if not ref_audio:
        return ""
    path = Path(ref_audio)
    candidates = [ref_audio, str(path.resolve()) if path.exists() else ref_audio, path.name]
    for key in candidates:
        text = mapping.get(key)
        if text:
            return text
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add exact ref_text from an emotion/reference library catalog to a TTS manifest."
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--library-root", type=Path)
    parser.add_argument("--ref-column", default="ref_audio")
    parser.add_argument("--text-column", default="ref_text")
    parser.add_argument("--strict", action="store_true", help="Fail if any ref audio cannot be matched")
    args = parser.parse_args()

    mapping = _load_catalog(args.catalog, library_root=args.library_root)
    with args.manifest.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if args.text_column not in fieldnames:
        fieldnames.append(args.text_column)

    missing: list[str] = []
    matched = 0
    for row in rows:
        if str(row.get(args.text_column) or "").strip():
            continue
        ref_audio = str(row.get(args.ref_column) or "").strip()
        text = _lookup_ref_text(ref_audio, mapping)
        if text:
            row[args.text_column] = text
            matched += 1
        elif ref_audio:
            missing.append(ref_audio)

    if args.strict and missing:
        preview = "\n".join(missing[:20])
        raise SystemExit(f"Missing ref_text for {len(missing)} refs:\n{preview}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    unique_missing = sorted(set(missing))
    print(f"rows={len(rows)} matched={matched} missing={len(unique_missing)} output={args.output}")
    if unique_missing:
        print("missing_preview=" + " | ".join(unique_missing[:5]))


if __name__ == "__main__":
    main()
