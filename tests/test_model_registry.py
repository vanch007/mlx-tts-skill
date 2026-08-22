from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from model_registry import PROJECTS, ensure_project, resolve_project  # noqa: E402


class ModelRegistryTests(unittest.TestCase):
    def test_registry_has_exactly_12_unique_projects(self) -> None:
        self.assertEqual(12, len(PROJECTS))
        self.assertEqual(12, len({project.key for project in PROJECTS}))
        self.assertEqual(12, len({project.github for project in PROJECTS}))
        self.assertTrue(all(Path(project.root).is_absolute() for project in PROJECTS))

    def test_aliases_resolve_to_canonical_keys(self) -> None:
        expected = {
            "mlx_indextts2": "indextts",
            "mlx-voxcpm2": "voxcpm2",
            "qwen3_tts": "qwen_tts",
            "mlx_omnivoice": "omnivoice",
            "mlx_higgs_audio": "higgs",
            "mlx-dots-tts": "dots",
            "mlx_zonos2": "zonos2",
            "mlx_scenema_audio": "scenema",
            "mlx-ming-omni-tts": "ming",
            "mlx_moss_tts": "moss",
            "mlx-supertonic": "supertonic",
            "mlx_fireredaudio": "fireredaudio",
        }
        for alias, key in expected.items():
            with self.subTest(alias=alias):
                self.assertEqual(key, resolve_project(alias).key)

    def test_dry_run_clone_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "scenema"
            result = ensure_project(resolve_project("scenema"), root=destination, dry_run=True)
            self.assertEqual("would_clone", result["action"])
            self.assertFalse(destination.exists())
            self.assertFalse(result["weights_restored"])

    def test_nonempty_destination_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir)
            (destination / "keep.txt").write_text("user data", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "refusing to overwrite"):
                ensure_project(resolve_project("scenema"), root=destination, dry_run=True)

    def test_cli_json_lists_12_projects(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPTS / "model_registry.py"), "--json"],
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(12, len(json.loads(completed.stdout)))


if __name__ == "__main__":
    unittest.main()
