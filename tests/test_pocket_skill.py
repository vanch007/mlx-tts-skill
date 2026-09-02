from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from model_registry import PROJECTS, resolve_project  # noqa: E402


class PocketSkillTests(unittest.TestCase):
    def test_registry_contains_pocket(self) -> None:
        self.assertEqual(len(PROJECTS), 14)
        project = resolve_project("pocket")
        self.assertEqual(project.key, "pocket")
        self.assertEqual(project.project_id, "mlx_pocket_tts")
        self.assertEqual(project.github, "vanch007/mlx-pocket-tts")
        self.assertEqual(project.root, "/Users/vanch/mlx-pocket-tts")
        self.assertEqual(project.voice_clone, "yes")
        self.assertTrue((ROOT / project.reference).is_file())

    def test_pocket_aliases(self) -> None:
        for alias in ("pocket", "pocket_tts", "mlx-pocket-tts", "mlx_pocket_tts", "kyutai_pocket"):
            self.assertEqual(resolve_project(alias).key, "pocket")
