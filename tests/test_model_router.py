from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from model_router import route  # noqa: E402


class ModelRouterTests(unittest.TestCase):
    def test_explicit_aliases_are_canonicalized_for_all_projects(self) -> None:
        expected = {
            "mlx_indextts2": "indextts",
            "mlx_voxcpm2": "voxcpm2",
            "mlx_qwen3_tts": "qwen_tts",
            "mlx_omnivoice": "omnivoice",
            "mlx_higgs_audio": "higgs",
            "mlx_dots_tts": "dots",
            "mlx_zonos2": "zonos2",
            "mlx_scenema_audio": "scenema",
            "mlx_ming_omni_tts": "ming",
            "mlx_moss_tts": "moss",
            "mlx_supertonic": "supertonic",
        }
        for alias, canonical in expected.items():
            with self.subTest(alias=alias):
                result = route(text="test", task_type="single", backend=alias)
                self.assertEqual(canonical, result.backend)

    def test_unknown_explicit_backend_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown MLX TTS project"):
            route(text="test", task_type="single", backend="imaginary_tts")

    def test_new_backend_heuristics_are_conservative(self) -> None:
        cases = (
            ("generate speech with sound effects", "single", "ming"),
            ("use speaking rate conditioning", "single", "zonos2"),
            ("lightweight fixed voice", "single", "supertonic"),
        )
        for text, task_type, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(expected, route(text=text, task_type=task_type).backend)


if __name__ == "__main__":
    unittest.main()
