#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass

from model_registry import PROJECTS, resolve_project


VI_RE = re.compile(
    r"[ăâđêôơưĂÂĐÊÔƠƯáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩị"
    r"óòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵÁÀẢÃẠẤẦẨẪẬẮẰẲẴẶ"
    r"ÉÈẺẼẸẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢÚÙỦŨỤỨỪỬỮỰÝỲỶỸỴ]"
)
CJK_RE = re.compile(r"[\u4e00-\u9fff]")


@dataclass
class Route:
    backend: str
    confidence: float
    reason: str
    suggested_profile: str = ""
    suggested_checks: tuple[str, ...] = ()


def detect_language(text: str, explicit: str = "auto") -> str:
    if explicit and explicit != "auto":
        return explicit
    if VI_RE.search(text):
        return "vi"
    if CJK_RE.search(text):
        return "zh"
    return "en"


def route(
    *,
    text: str,
    task_type: str,
    language: str = "auto",
    backend: str = "",
    model_override: str = "",
    quality_goal: str = "content",
    needs_emotion: bool = False,
    compare: bool = False,
    omnivoice_requested: bool = False,
) -> Route:
    if model_override:
        explicit_backend = backend or "explicit"
        if backend:
            explicit_backend = resolve_project(backend).key
        return Route(
            backend=explicit_backend,
            confidence=1.0,
            reason=f"explicit model_override: {model_override}",
            suggested_checks=("asr", "leakage", "rtf"),
        )
    if backend:
        try:
            canonical_backend = resolve_project(backend).key
        except ValueError:
            if backend != "compare":
                raise
            canonical_backend = backend
        return Route(
            backend=canonical_backend,
            confidence=1.0,
            reason="explicit backend override",
            suggested_checks=("asr", "leakage", "rtf"),
        )
    normalized_task = task_type.lower()
    if compare or normalized_task in {"compare", "benchmark"}:
        return Route(
            backend="compare",
            confidence=1.0,
            reason="comparison or benchmark requested",
            suggested_checks=("asr", "voice", "emotion", "rtf"),
        )
    if normalized_task in {"optimize", "asr_check"}:
        return Route(
            backend="compare",
            confidence=0.86,
            reason="optimization starts with diagnostics before changing backend or parameters",
            suggested_checks=("asr", "leakage", "voice", "emotion", "rtf"),
        )

    lang = detect_language(text, language)
    task = normalized_task
    goal = quality_goal.lower()

    combined = f"{text} {task} {goal}".lower()
    if any(token in combined for token in ("sound effect", "sfx", "音效", "music", "音乐")):
        return Route(
            backend="ming",
            confidence=0.88,
            reason="omni-audio speech/music/sound request routes to Ming",
            suggested_checks=("asr", "rtf", "manual_listening"),
        )
    if any(token in combined for token in ("quality conditioning", "speaking rate", "质量条件", "语速条件")):
        return Route(
            backend="zonos2",
            confidence=0.84,
            reason="explicit conditioning-control request routes to ZONOS2",
            suggested_checks=("asr", "voice", "rtf"),
        )
    if any(token in combined for token in ("lightweight", "fixed voice", "on-device", "轻量", "固定音色")):
        return Route(
            backend="supertonic",
            confidence=0.82,
            reason="lightweight fixed-style on-device request routes to Supertonic",
            suggested_checks=("asr", "rtf"),
        )

    if omnivoice_requested or "omnivoice" in goal:
        return Route(
            backend="omnivoice",
            confidence=0.95,
            reason="OmniVoice was explicitly requested or selected as the quality goal",
            suggested_checks=("asr", "leakage", "rtf"),
        )
    if lang == "vi":
        return Route(
            backend="indextts",
            confidence=0.95,
            reason="Vietnamese tone-mark text routes to mlx-indextts2 Vietnamese profile",
            suggested_profile="vietnamese",
            suggested_checks=("asr", "rtf"),
        )
    if needs_emotion or task in {"novel", "emotion_library", "emotion"}:
        return Route(
            backend="indextts",
            confidence=0.9,
            reason="emotion reference, Qwen text emotion, or emotion library support is native in mlx-indextts2",
            suggested_profile="auto",
            suggested_checks=("asr", "emotion", "rtf"),
        )
    if task == "batch" and language == "auto" and not text.strip():
        return Route(
            backend="indextts",
            confidence=0.7,
            reason="unknown-language batch defaults to mlx-indextts2 because it has the most complete batch/combine/planning workflow",
            suggested_profile="auto",
            suggested_checks=("asr", "leakage", "rtf"),
        )
    if lang == "zh" and task in {"dialogue", "crosstalk", "batch"} and goal == "content":
        return Route(
            backend="compare",
            confidence=0.82,
            reason="VoxCPM2 is candidate-only until the official-to-local MLX rebuild passes parity; compare production backends first",
            suggested_checks=("asr", "leakage", "rtf"),
        )
    if lang == "zh" and task in {"crosstalk", "dialogue"} and goal in {
        "voice",
        "naturalness",
        "style",
        "stage",
        "crosstalk",
    }:
        return Route(
            backend="omnivoice",
            confidence=0.8,
            reason="Chinese crosstalk/stage dialogue naturalness routes to the dedicated OmniVoice runtime",
            suggested_checks=("asr", "leakage", "rtf"),
        )
    if task in {"voice_clone", "replay"} or goal == "speed":
        return Route(
            backend="compare",
            confidence=0.78,
            reason="Qwen3-TTS is candidate-only until official-to-local rebuild; use compare mode before production",
            suggested_checks=("asr", "leakage", "rtf"),
        )
    if lang == "zh":
        return Route(
            backend="compare",
            confidence=0.72,
            reason="Chinese content fidelity is prioritized, but VoxCPM2 is not production-ready until standalone rebuild",
            suggested_checks=("asr", "leakage", "rtf"),
        )
    return Route(
        backend="indextts",
        confidence=0.65,
        reason="default non-Vietnamese route avoids candidate-only Qwen3-TTS until official-to-local rebuild is complete",
        suggested_checks=("asr", "leakage", "rtf"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Route an MLX TTS task to the best local backend.")
    parser.add_argument("--text", default="")
    parser.add_argument("--task-type", default="single")
    parser.add_argument("--language", default="auto")
    parser.add_argument("--backend", default="")
    parser.add_argument("--model-override", default="")
    parser.add_argument("--quality-goal", default="content")
    parser.add_argument("--needs-emotion", action="store_true")
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--omnivoice-requested", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--list-backends", action="store_true")
    args = parser.parse_args()

    if args.list_backends:
        payload = [{"key": project.key, "project_id": project.project_id} for project in PROJECTS]
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            for row in payload:
                print(f"{row['key']}: {row['project_id']}")
        return

    result = route(
        text=args.text,
        task_type=args.task_type,
        language=args.language,
        backend=args.backend,
        model_override=args.model_override,
        quality_goal=args.quality_goal,
        needs_emotion=args.needs_emotion,
        compare=args.compare,
        omnivoice_requested=args.omnivoice_requested,
    )
    payload = asdict(result)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"backend={result.backend}")
        print(f"confidence={result.confidence:.2f}")
        print(f"reason={result.reason}")
        if result.suggested_profile:
            print(f"profile={result.suggested_profile}")
        if result.suggested_checks:
            print("checks=" + ",".join(result.suggested_checks))


if __name__ == "__main__":
    main()
