#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


ROOTS = {
    "indextts": Path("/Users/vanch/mlx-indextts2"),
    "voxcpm2": Path("/Users/vanch/mlx-voxcpm2"),
    "qwen_tts": Path("/Users/vanch/mlx-qwen3-tts"),
    "omnivoice": Path("/Users/vanch/mlx-omnivoice"),
}


@dataclass
class BackendPlan:
    backend: str
    cwd: Path
    command: list[str]
    env: dict[str, str]
    output_dir: Path


def _python(root: Path, fallback: Path | None = None) -> str:
    candidate = root / ".venv/bin/python"
    if candidate.exists():
        return str(candidate)
    if fallback and fallback.exists():
        return str(fallback)
    return "python3"


def _load_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def _write_subset(source: Path, output: Path, limit: int | None) -> Path:
    if source.suffix.lower() == ".json":
        rows = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise SystemExit(f"JSON manifest must be a list: {source}")
        if limit is not None:
            rows = rows[:limit]
        output = output.with_suffix(".json")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        return output
    if source.suffix.lower() == ".jsonl":
        rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
        if limit is not None:
            rows = rows[:limit]
        output = output.with_suffix(".jsonl")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
        return output

    fieldnames, rows = _load_csv_rows(source)
    if limit is not None:
        rows = rows[:limit]
    output = output.with_suffix(".csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return output


def _to_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value) if value not in (None, "") else default
    except (TypeError, ValueError):
        return default


def _summarize_manifest(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    durations = [_to_float(row.get("duration_s")) for row in rows]
    elapsed = [_to_float(row.get("elapsed_s")) for row in rows]
    rtfs = [_to_float(row.get("rtf")) for row in rows if _to_float(row.get("rtf")) > 0]
    audio_duration = sum(durations)
    generation_elapsed = sum(elapsed)
    return {
        "rows": len(rows),
        "audio_duration_s": round(audio_duration, 4),
        "generation_elapsed_s": round(generation_elapsed, 4),
        "generation_rtf": round(generation_elapsed / audio_duration, 4) if audio_duration > 0 else None,
        "avg_row_rtf": round(sum(rtfs) / len(rtfs), 4) if rtfs else None,
    }


def _summarize_output_dir(path: Path) -> dict[str, object]:
    summary: dict[str, object] = {}
    report_path = path / "report.json"
    if report_path.exists():
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
            summary.update(report)
        except json.JSONDecodeError:
            summary["report_parse_error"] = str(report_path)
    for name in ("manifest.csv", "summary.csv"):
        manifest_path = path / name
        if manifest_path.exists():
            summary.setdefault("manifest_path", str(manifest_path))
            summary.update(_summarize_manifest(manifest_path))
            break
    combined_path = path / "combined.wav"
    if combined_path.exists():
        summary.setdefault("combined_path", str(combined_path))
    return summary


def _add_common_ref_args(command: list[str], args: argparse.Namespace) -> None:
    if args.ref_audio:
        command.extend(["--ref-audio", args.ref_audio])
    if args.ref_text and "--ref-text" not in command:
        command.extend(["--ref-text", args.ref_text])


def _plan_indextts(manifest: Path, output_dir: Path, args: argparse.Namespace) -> BackendPlan:
    root = ROOTS["indextts"]
    command = [
        _python(root),
        "-m",
        "mlx_indextts.cli",
        "batch",
        "--input",
        str(manifest),
        "--output-dir",
        str(output_dir),
        "--profile",
        args.indextts_profile,
        "--max-tokens",
        str(args.indextts_max_tokens),
        "--max-text-tokens",
        str(args.indextts_max_text_tokens),
        "--diffusion-steps",
        str(args.indextts_diffusion_steps),
        "--tokens-per-char",
        str(args.indextts_tokens_per_char),
        "--min-max-tokens",
        str(args.indextts_min_max_tokens),
        "--combine-silence-ms",
        str(int(args.combine_silence_ms)),
    ]
    if not args.indextts_dynamic_max_tokens:
        command.append("--no-dynamic-max-tokens")
    if args.combine:
        command.append("--combine")
    if args.no_denoise_refs:
        command.extend(["--no-denoise-ref", "--no-denoise-emotion-ref"])
    if args.indextts_model:
        command.extend(["--model", args.indextts_model])
    if args.ref_audio:
        command.extend(["--ref-audio", args.ref_audio])
    return BackendPlan("indextts", root, command, os.environ.copy(), output_dir)


def _plan_voxcpm2(manifest: Path, output_dir: Path, args: argparse.Namespace) -> BackendPlan:
    root = ROOTS["voxcpm2"]
    fallback_python = ROOTS["indextts"] / ".venv/bin/python"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root)
    command = [
        _python(root, fallback=fallback_python),
        "-m",
        "mlx_voxcpm2.cli",
        "batch",
        "--model-dir",
        args.voxcpm2_model_dir,
        "--input",
        str(manifest),
        "--output-dir",
        str(output_dir),
        "--backend",
        args.voxcpm2_backend,
        "--max-len",
        str(args.voxcpm2_max_len),
        "--inference-timesteps",
        str(args.voxcpm2_inference_timesteps),
        "--cfg-value",
        str(args.voxcpm2_cfg_value),
        "--max-len-per-char",
        str(args.voxcpm2_max_len_per_char),
        "--min-dynamic-max-len",
        str(args.voxcpm2_min_dynamic_max_len),
        "--combine-silence-ms",
        str(args.combine_silence_ms),
    ]
    if not args.voxcpm2_dynamic_max_len:
        command.append("--no-dynamic-max-len")
    if args.combine:
        command.append("--combine")
    if args.ref_audio:
        command.extend(["--reference-wav-path", args.ref_audio])
    if args.no_denoise_refs:
        command.extend(["--denoise-method", "none"])
    return BackendPlan("voxcpm2", root, command, env, output_dir)


def _plan_qwen(manifest: Path, output_dir: Path, args: argparse.Namespace) -> BackendPlan:
    root = ROOTS["qwen_tts"]
    command = [
        _python(root),
        "-m",
        "mlx_qwen_tts.cli",
        "batch",
        "--model",
        args.qwen_model,
        "--input",
        str(manifest),
        "--output-dir",
        str(output_dir),
        "--max-tokens",
        str(args.qwen_max_tokens),
        "--tokens-per-char",
        str(args.qwen_tokens_per_char),
        "--min-max-tokens",
        str(args.qwen_min_max_tokens),
        "--temperature",
        str(args.qwen_temperature),
        "--combine",
        "--crossfade-ms",
        str(args.crossfade_ms),
        "--require-official",
    ]
    if not args.combine:
        command.remove("--combine")
    _add_common_ref_args(command, args)
    if args.qwen_voice:
        command.extend(["--voice", args.qwen_voice])
    if args.qwen_instruct:
        command.extend(["--instruct", args.qwen_instruct])
    return BackendPlan("qwen_tts", root, command, os.environ.copy(), output_dir)


def _plan_omnivoice(manifest: Path, output_dir: Path, args: argparse.Namespace) -> BackendPlan:
    root = ROOTS["omnivoice"]
    command = [
        _python(root),
        "-m",
        "mlx_omnivoice.cli",
        "batch",
        "--model",
        args.omnivoice_model,
        "--input",
        str(manifest),
        "--output-dir",
        str(output_dir),
        "--num-step",
        str(args.omnivoice_num_step),
        "--guidance-scale",
        str(args.omnivoice_guidance_scale),
        "--combine-silence-ms",
        str(args.combine_silence_ms),
    ]
    if args.combine:
        command.append("--combine")
    _add_common_ref_args(command, args)
    if args.omnivoice_instruct:
        command.extend(["--instruct", args.omnivoice_instruct])
    return BackendPlan("omnivoice", root, command, os.environ.copy(), output_dir)


def _build_plan(backend: str, manifest: Path, output_dir: Path, args: argparse.Namespace) -> BackendPlan:
    if backend == "indextts":
        return _plan_indextts(manifest, output_dir, args)
    if backend == "voxcpm2":
        return _plan_voxcpm2(manifest, output_dir, args)
    if backend == "qwen_tts":
        return _plan_qwen(manifest, output_dir, args)
    if backend == "omnivoice":
        return _plan_omnivoice(manifest, output_dir, args)
    raise SystemExit(f"unknown backend: {backend}")


def _backend_manifest_source(backend: str, args: argparse.Namespace) -> Path:
    overrides = {
        "indextts": args.indextts_manifest,
        "voxcpm2": args.voxcpm2_manifest,
        "qwen_tts": args.qwen_manifest,
        "omnivoice": args.omnivoice_manifest,
    }
    value = overrides.get(backend)
    return Path(value) if value else args.manifest


def _run(plan: BackendPlan) -> dict[str, object]:
    start = time.perf_counter()
    result = subprocess.run(
        plan.command,
        cwd=plan.cwd,
        env=plan.env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    elapsed = time.perf_counter() - start
    log_path = plan.output_dir / "run.log"
    plan.output_dir.mkdir(parents=True, exist_ok=True)
    log_path.write_text(result.stdout, encoding="utf-8")
    return {
        "backend": plan.backend,
        "returncode": result.returncode,
        "elapsed_s": round(elapsed, 4),
        "output_dir": str(plan.output_dir),
        "log": str(log_path),
        "command": plan.command,
        "metrics": _summarize_output_dir(plan.output_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a fair manifest benchmark across MLX TTS backends.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--indextts-manifest", type=Path)
    parser.add_argument("--voxcpm2-manifest", type=Path)
    parser.add_argument("--qwen-manifest", type=Path)
    parser.add_argument("--omnivoice-manifest", type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument(
        "--backends",
        nargs="+",
        default=["indextts", "voxcpm2", "qwen_tts", "omnivoice"],
        choices=["indextts", "voxcpm2", "qwen_tts", "omnivoice"],
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--combine", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--combine-silence-ms", type=float, default=80.0)
    parser.add_argument("--crossfade-ms", type=float, default=35.0)
    parser.add_argument("--ref-audio")
    parser.add_argument("--ref-text")
    parser.add_argument("--no-denoise-refs", action="store_true")

    parser.add_argument("--indextts-model", default="")
    parser.add_argument("--indextts-profile", default="auto", choices=["auto", "v25", "2.5", "standard", "vietnamese", "vi"])
    parser.add_argument("--indextts-max-tokens", type=int, default=900)
    parser.add_argument("--indextts-max-text-tokens", type=int, default=80)
    parser.add_argument("--indextts-diffusion-steps", type=int, default=16)
    parser.add_argument("--indextts-dynamic-max-tokens", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--indextts-tokens-per-char", type=float, default=14.0)
    parser.add_argument("--indextts-min-max-tokens", type=int, default=320)

    parser.add_argument("--voxcpm2-model-dir", default="models/VoxCPM2-official-mlx-int8-components")
    parser.add_argument("--voxcpm2-backend", default="native", choices=["native", "legacy"])
    parser.add_argument("--voxcpm2-max-len", type=int, default=96)
    parser.add_argument("--voxcpm2-inference-timesteps", type=int, default=4)
    parser.add_argument("--voxcpm2-cfg-value", type=float, default=2.0)
    parser.add_argument("--voxcpm2-dynamic-max-len", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--voxcpm2-max-len-per-char", type=float, default=1.8)
    parser.add_argument("--voxcpm2-min-dynamic-max-len", type=int, default=24)

    parser.add_argument("--qwen-model", default="qwen3_tts_8bit")
    parser.add_argument("--qwen-max-tokens", type=int, default=1024)
    parser.add_argument("--qwen-tokens-per-char", type=float, default=4.0)
    parser.add_argument("--qwen-min-max-tokens", type=int, default=48)
    parser.add_argument("--qwen-temperature", type=float, default=0.9)
    parser.add_argument("--qwen-voice", default="")
    parser.add_argument("--qwen-instruct", default="")

    parser.add_argument("--omnivoice-model", default="omnivoice_8bit")
    parser.add_argument("--omnivoice-num-step", type=int, default=24)
    parser.add_argument("--omnivoice-guidance-scale", type=float, default=2.0)
    parser.add_argument("--omnivoice-instruct", default="")
    args = parser.parse_args()

    args.output_root.mkdir(parents=True, exist_ok=True)
    plans = []
    for name in args.backends:
        source = _backend_manifest_source(name, args)
        subset_manifest = _write_subset(source, args.output_root / f"input_{name}", args.limit)
        plans.append(_build_plan(name, subset_manifest, args.output_root / name, args))
    plan_payload = [
        {
            "backend": plan.backend,
            "cwd": str(plan.cwd),
            "output_dir": str(plan.output_dir),
            "command": plan.command,
            "input": str(plan.command[plan.command.index("--input") + 1]) if "--input" in plan.command else "",
        }
        for plan in plans
    ]
    (args.output_root / "plan.json").write_text(json.dumps(plan_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.dry_run:
        print(json.dumps({"plans": plan_payload}, ensure_ascii=False, indent=2))
        return

    results = [_run(plan) for plan in plans]
    summary_path = args.output_root / "summary.json"
    summary_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"summary": str(summary_path), "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
