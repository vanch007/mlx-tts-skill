from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from model_registry import resolve_project  # noqa: E402
from model_router import route  # noqa: E402


class IndexTTS25SkillTests(unittest.TestCase):
    def test_registry_accepts_v25_alias_and_documents_five_languages(self) -> None:
        project = resolve_project("indextts2.5")
        self.assertEqual("indextts", project.key)
        for language in ("zh", "en", "ja", "es", "ar"):
            self.assertIn(language, project.notes)

    def test_new_languages_route_to_v25(self) -> None:
        for language in ("ja", "es", "ar"):
            with self.subTest(language=language):
                result = route(text="test", task_type="single", language=language)
                self.assertEqual("indextts", result.backend)
                self.assertEqual("v25", result.suggested_profile)

    def test_four_backend_runner_accepts_v25_profile(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "run_backend_benchmark.py"), "--help"],
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("v25", completed.stdout)
        self.assertIn("2.5", completed.stdout)

    def test_reference_separates_v25_from_vietnamese_v20(self) -> None:
        reference = (ROOT / "references" / "indextts.md").read_text(encoding="utf-8")
        self.assertIn("models/mlx-IndexTTS-2.5-8bit", reference)
        self.assertIn("models/mlx-indexTTS2-vietnamese-8bit", reference)
        self.assertIn("--max-text-tokens 20", reference)


if __name__ == "__main__":
    unittest.main()
