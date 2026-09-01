#!/usr/bin/env python3
"""Canonical registry and safe source recovery for local MLX TTS projects.

The recovery command restores Git-tracked source and configuration only. Model
weights and Hugging Face caches remain backend-specific external dependencies.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ModelProject:
    key: str
    project_id: str
    aliases: tuple[str, ...]
    root: str
    github: str
    default_branch: str
    reference: str
    voice_clone: str
    notes: str

    @property
    def clone_url(self) -> str:
        return f"https://github.com/{self.github}.git"


PROJECTS: tuple[ModelProject, ...] = (
    ModelProject("indextts", "mlx_indextts2", ("indextts2", "indextts25", "indextts2.5", "mlx-indextts2", "mlx_indextts2"), "/Users/vanch/mlx-indextts2", "vanch007/mlx-indextts2", "main", "references/indextts.md", "yes", "IndexTTS 2.5 zh/en/ja/es/ar plus separate Vietnamese 2.0; cloning, emotion, duration, streaming, and batch planning."),
    ModelProject("voxcpm2", "mlx_voxcpm2", ("mlx-voxcpm2", "mlx_voxcpm2", "voxcpm"), "/Users/vanch/mlx-voxcpm2", "vanch007/mlx-voxcpm2", "main", "references/voxcpm2.md", "yes", "Native MLX voice cloning and content-fidelity comparison backend."),
    ModelProject("qwen_tts", "mlx_qwen3_tts", ("qwen", "qwen3", "qwen3_tts", "mlx-qwen3-tts", "mlx_qwen3_tts"), "/Users/vanch/mlx-qwen3-tts", "vanch007/mlx-qwen3-tts", "main", "references/qwen_tts.md", "yes", "Base ICL cloning, CustomVoice, and VoiceDesign variants."),
    ModelProject("omnivoice", "mlx_omnivoice", ("omni", "mlx-omnivoice", "mlx_omnivoice"), "/Users/vanch/mlx-omnivoice", "vanch007/mlx-omnivoice", "main", "references/omnivoice.md", "yes", "Chinese dialogue and crosstalk-oriented cloning runtime."),
    ModelProject("higgs", "mlx_higgs_audio", ("higgs_audio", "mlx-higgs-audio", "mlx_higgs_audio"), "/Users/vanch/mlx-higgs-audio", "vanch007/mlx-higgs-audio", "main", "references/model_catalog.md", "yes", "Reference cloning, expressive controls, and long-form redubbing."),
    ModelProject("dots", "mlx_dots_tts", ("dots_tts", "mlx-dots-tts", "mlx_dots_tts"), "/Users/vanch/mlx-dots.tts", "vanch007/mlx-dots-tts", "main", "references/model_catalog.md", "yes", "Prompt-audio cloning and long-text generation."),
    ModelProject("zonos2", "mlx_zonos2", ("zonos", "mlx-zonos2", "mlx_zonos2"), "/Users/vanch/mlx-ZONOS2", "vanch007/mlx-ZONOS2", "main", "references/model_catalog.md", "yes", "Voice cloning and conditioning; requires a local DAC checkpoint."),
    ModelProject("scenema", "mlx_scenema_audio", ("scenema_audio", "mlx-scenema-audio", "mlx_scenema_audio"), "/Users/vanch/mlx-scenema-audio", "vanch007/mlx-scenema-audio", "main", "references/model_catalog.md", "yes", "MLX speech engine with voice design, cloning, and action tags."),
    ModelProject("ming", "mlx_ming_omni_tts", ("ming_omni", "mlx-ming-omni-tts", "mlx_ming_omni_tts"), "/Users/vanch/mlx-Ming-omni-tts", "vanch007/mlx-Ming-omni-tts", "main", "references/model_catalog.md", "design", "Large voice-design, speech, music, and sound generation model."),
    ModelProject("moss", "mlx_moss_tts", ("moss_tts", "mlx-moss-tts", "mlx_moss_tts"), "/Users/vanch/mlx-MOSS-TTS-Local-Transformer-v1.5", "vanch007/mlx-MOSS-TTS-Local-Transformer-v1.5", "main", "references/model_catalog.md", "yes", "Multilingual cloning/style/streaming; requires local audio-tokenizer shards."),
    ModelProject("supertonic", "mlx_supertonic", ("mlx-supertonic", "mlx_supertonic"), "/Users/vanch/mlx-supertonic", "vanch007/mlx-supertonic", "main", "references/model_catalog.md", "no", "Lightweight fixed-style voices; no official arbitrary reference cloning."),
    ModelProject("fireredaudio", "mlx_fireredaudio", ("firered", "firered_audio", "mlx-fireredaudio", "mlx_fireredaudio"), "/Users/vanch/mlx-FireRedAudio", "vanch007/mlx-FireRedAudio", "main", "references/fireredaudio.md", "yes", "General-purpose audio LLM with ASR, QA, Voice Cloning (TTS), Speech Editing, and Voice Design."),
    ModelProject("breeze", "mlx_breeze_tts2", ("breeze_tts", "breeze_tts2", "breeze2", "mlx-breeze-tts2", "mlx_breeze_tts2", "sirocco"), "/Users/vanch/mlx-breeze-tts2", "vanch007/mlx-breeze-tts2", "main", "references/breeze.md", "yes", "Breeze TTS 2 with voice design, cloning, voice direction, speech events laugh/cough/sigh, and streaming."),
)


def _normalize(value: str) -> str:
    return value.strip().lower().replace(".", "_")


def project_map() -> dict[str, ModelProject]:
    result: dict[str, ModelProject] = {}
    for project in PROJECTS:
        for alias in (project.key, project.project_id, *project.aliases):
            result[_normalize(alias)] = project
    return result


def resolve_project(value: str) -> ModelProject:
    try:
        return project_map()[_normalize(value)]
    except KeyError as exc:
        choices = ", ".join(project.key for project in PROJECTS)
        raise ValueError(f"unknown MLX TTS project {value!r}; choose one of: {choices}") from exc


def inspect_project(project: ModelProject, root: Path | None = None) -> dict[str, object]:
    destination = root or Path(project.root)
    payload: dict[str, object] = {
        "key": project.key,
        "project_id": project.project_id,
        "root": str(destination),
        "github": project.github,
        "exists": destination.exists(),
        "is_git": (destination / ".git").exists(),
    }
    if payload["is_git"]:
        for field, args in (
            ("head", ["rev-parse", "HEAD"]),
            ("branch", ["branch", "--show-current"]),
            ("origin", ["remote", "get-url", "origin"]),
        ):
            completed = subprocess.run(
                ["git", "-C", str(destination), *args],
                text=True,
                capture_output=True,
                check=False,
            )
            payload[field] = completed.stdout.strip() if completed.returncode == 0 else None
    return payload


def ensure_project(
    project: ModelProject,
    *,
    root: Path | None = None,
    dry_run: bool = False,
    depth: int | None = None,
) -> dict[str, object]:
    destination = root or Path(project.root)
    if (destination / ".git").exists():
        return {"key": project.key, "action": "present", "root": str(destination)}
    if destination.exists() and any(destination.iterdir()):
        raise RuntimeError(f"refusing to overwrite non-empty destination: {destination}")

    command = ["git", "clone", "--branch", project.default_branch]
    if depth:
        command.extend(["--depth", str(depth)])
    command.extend([project.clone_url, str(destination)])
    result: dict[str, object] = {
        "key": project.key,
        "action": "would_clone" if dry_run else "cloned",
        "root": str(destination),
        "command": command,
        "weights_restored": False,
    }
    if dry_run:
        return result
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(command, check=True)
    result["head"] = inspect_project(project, destination).get("head")
    return result


def _serialize(projects: Iterable[ModelProject]) -> list[dict[str, object]]:
    rows = []
    for project in projects:
        row = asdict(project)
        row["clone_url"] = project.clone_url
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="List, inspect, or safely restore the 13 local MLX TTS source projects.")
    parser.add_argument("--model", help="Show one model project by key or alias.")
    parser.add_argument("--check", action="store_true", help="Inspect all registered local roots.")
    parser.add_argument("--ensure", metavar="MODEL", help="Clone one missing source project.")
    parser.add_argument("--ensure-all", action="store_true", help="Clone every missing source project.")
    parser.add_argument("--root", type=Path, help="Override destination for --ensure only.")
    parser.add_argument("--depth", type=int, help="Optional shallow-clone depth.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.root and not args.ensure:
        parser.error("--root requires --ensure")
    if sum(bool(value) for value in (args.model, args.check, args.ensure, args.ensure_all)) > 1:
        parser.error("choose only one of --model, --check, --ensure, or --ensure-all")

    try:
        if args.ensure:
            payload: object = ensure_project(resolve_project(args.ensure), root=args.root, dry_run=args.dry_run, depth=args.depth)
        elif args.ensure_all:
            payload = [ensure_project(project, dry_run=args.dry_run, depth=args.depth) for project in PROJECTS]
        elif args.check:
            payload = [inspect_project(project) for project in PROJECTS]
        elif args.model:
            payload = _serialize((resolve_project(args.model),))[0]
        else:
            payload = _serialize(PROJECTS)
    except (ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        raise SystemExit(str(exc)) from exc

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif isinstance(payload, list):
        for row in payload:
            print(f"{row['key']}: {row.get('root', '')} -> {row.get('github', row.get('action', ''))}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
