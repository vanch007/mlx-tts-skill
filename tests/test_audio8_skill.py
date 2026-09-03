import unittest
from pathlib import Path
import sys

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from model_registry import PROJECTS, resolve_project
from model_router import route


class Audio8SkillTests(unittest.TestCase):
    def test_registry_contains_audio8(self):
        keys = [p.key for p in PROJECTS]
        self.assertIn("audio8", keys)
        self.assertEqual(len(PROJECTS), 15)

    def test_resolve_aliases(self):
        for alias in ("audio8", "audio8_tts", "mlx-audio8-tts", "mlx_audio8_tts", "arktts", "ark_tts"):
            proj = resolve_project(alias)
            self.assertEqual(proj.key, "audio8")
            self.assertEqual(proj.project_id, "mlx_audio8_tts")
            self.assertEqual(proj.root, "/Users/vanch/mlx-audio8-tts")

    def test_route_audio8_keywords(self):
        r = route(text="使用 44.1kHz DualAR 模型进行零样本克隆 audio8", task_type="single")
        self.assertEqual(r.backend, "audio8")
        self.assertEqual(r.suggested_profile, "8bit")

    def test_reference_file_exists(self):
        ref = Path(__file__).resolve().parents[1] / "references" / "audio8.md"
        self.assertTrue(ref.exists())


if __name__ == "__main__":
    unittest.main()
