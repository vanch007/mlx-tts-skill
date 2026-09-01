import unittest
from pathlib import Path
import sys

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from model_registry import PROJECTS, resolve_project
from model_router import route


class FireRedAudioSkillTests(unittest.TestCase):
    def test_registry_contains_fireredaudio(self):
        keys = [p.key for p in PROJECTS]
        self.assertIn("fireredaudio", keys)
        self.assertEqual(len(PROJECTS), 13)

    def test_resolve_aliases(self):
        for alias in ("fireredaudio", "firered", "firered_audio", "mlx-fireredaudio", "mlx_fireredaudio"):
            proj = resolve_project(alias)
            self.assertEqual(proj.key, "fireredaudio")
            self.assertEqual(proj.project_id, "mlx_fireredaudio")
            self.assertEqual(proj.root, "/Users/vanch/mlx-FireRedAudio")

    def test_route_fireredaudio_keywords(self):
        r = route(text="帮我做语音编辑", task_type="edit")
        self.assertEqual(r.backend, "fireredaudio")
        self.assertEqual(r.suggested_profile, "8bit")

    def test_reference_file_exists(self):
        ref = Path(__file__).resolve().parents[1] / "references" / "fireredaudio.md"
        self.assertTrue(ref.exists())


if __name__ == "__main__":
    unittest.main()
