import unittest
from pathlib import Path
import sys

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from model_registry import PROJECTS, resolve_project
from model_router import route


class Drama3SkillTests(unittest.TestCase):
    def test_registry_contains_drama3(self):
        keys = [p.key for p in PROJECTS]
        self.assertIn("drama3", keys)
        self.assertEqual(len(PROJECTS), 16)

    def test_resolve_aliases(self):
        for alias in ("drama3", "drama_3", "drama-3", "mlx-drama3", "mlx_drama3", "drama3_mlx", "fish_speech", "fishaudio"):
            proj = resolve_project(alias)
            self.assertEqual(proj.key, "drama3")
            self.assertEqual(proj.project_id, "mlx_drama3")
            self.assertEqual(proj.root, "/Users/vanch/drama-3-mlx")

    def test_route_drama3_keywords(self):
        r = route(text="<|speaker:0|> 你好 <|speaker:1|> [laughs] 很高兴见到你", task_type="dialogue")
        self.assertEqual(r.backend, "drama3")
        self.assertEqual(r.suggested_profile, "4bit")

    def test_reference_file_exists(self):
        ref = Path(__file__).resolve().parents[1] / "references" / "drama3.md"
        self.assertTrue(ref.exists())


if __name__ == "__main__":
    unittest.main()
