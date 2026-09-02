import unittest
from pathlib import Path
import sys

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from model_registry import PROJECTS, resolve_project
from model_router import route


class BreezeSkillTests(unittest.TestCase):
    def test_registry_contains_breeze(self):
        keys = [p.key for p in PROJECTS]
        self.assertIn("breeze", keys)
        self.assertEqual(len(PROJECTS), 14)

    def test_resolve_aliases(self):
        for alias in ("breeze", "breeze_tts", "breeze_tts2", "breeze2", "mlx-breeze-tts2", "mlx_breeze_tts2", "sirocco"):
            proj = resolve_project(alias)
            self.assertEqual(proj.key, "breeze")
            self.assertEqual(proj.project_id, "mlx_breeze_tts2")
            self.assertEqual(proj.root, "/Users/vanch/mlx-breeze-tts2")

    def test_route_breeze_keywords(self):
        r = route(text="带有笑声事件的语音生成 (laugh)", task_type="single")
        self.assertEqual(r.backend, "breeze")
        self.assertEqual(r.suggested_profile, "8bit")

    def test_reference_file_exists(self):
        ref = Path(__file__).resolve().parents[1] / "references" / "breeze.md"
        self.assertTrue(ref.exists())


if __name__ == "__main__":
    unittest.main()

