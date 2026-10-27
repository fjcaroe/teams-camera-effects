import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as Point
import numpy as np
from camera_fx.effects import Effects
from camera_fx.gestures import classify
from camera_fx.settings import CATALOG, load_enabled, save_enabled


def shape(extended):
    hand = [Point(x=0.5, y=0.8) for _ in range(21)]
    for up, mcp, pip, tip in zip(extended, (5, 9, 13, 17), (6, 10, 14, 18), (8, 12, 16, 20)):
        hand[mcp] = Point(x=0.5, y=0.65)
        hand[pip] = Point(x=0.5, y=0.5)
        hand[tip] = Point(x=0.5, y=0.25 if up else 0.66)
    return hand


class SelectionTests(unittest.TestCase):
    def test_only_goku_ignores_open_palm_and_blocks_manual_rasengan(self):
        fx = Effects()
        fx.set_enabled({"teleport"})
        gesture, _ = classify([shape([True] * 4)], None)
        self.assertEqual(gesture, "rasengan")
        self.assertFalse(fx.gesture_allowed(gesture))
        fx.trigger("rasengan", 1)
        self.assertEqual(fx.mode, "normal")
        fx.capture(np.zeros((10, 10, 3), np.uint8))
        fx.trigger("teleport", 2)
        self.assertTrue(fx.hidden)

    def test_disabling_active_effect_stops_it_and_teleport_returns_person(self):
        fx = Effects()
        fx.trigger("matrix", 0)
        fx.set_enabled({"teleport"})
        self.assertEqual(fx.mode, "normal")
        fx.capture(np.zeros((10, 10, 3), np.uint8))
        fx.trigger("teleport", 1)
        fx.set_enabled(set())
        self.assertFalse(fx.hidden)
        self.assertFalse(any(fx.gesture_allowed(key) for key in CATALOG))

    def test_other_gestures_do_not_activate_while_invisible(self):
        fx = Effects()
        fx.capture(np.zeros((10, 10, 3), np.uint8))
        fx.trigger("teleport", 0)
        self.assertTrue(fx.gesture_allowed("teleport"))
        self.assertFalse(fx.gesture_allowed("rasengan"))
        self.assertFalse(fx.gesture_allowed("aura"))

    def test_new_gestures(self):
        self.assertEqual(classify([shape([False] * 4)], None)[0], "aura")
        self.assertEqual(classify([shape([True, False, False, True])], None)[0], "matrix")

    def test_new_effects_render_and_toggle(self):
        frame = np.full((90, 160, 3), 60, np.uint8)
        mask = np.zeros((90, 160), np.float32)
        mask[15:80, 60:100] = 1
        for action in ("aura", "matrix"):
            with self.subTest(action=action):
                fx = Effects()
                fx.trigger(action, 0)
                output = fx.render(frame, mask, 1)
                self.assertEqual(output.shape, frame.shape)
                self.assertEqual(output.dtype, np.uint8)
                self.assertFalse(np.array_equal(output, frame))
                fx.trigger(action, 2)
                np.testing.assert_array_equal(fx.render(frame, mask, 3), frame)

    def test_preferences_survive_restart_including_no_effects(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            self.assertEqual(load_enabled(path), {"teleport"})
            save_enabled({"matrix", "aura", "unknown"}, path)
            self.assertEqual(load_enabled(path), {"matrix", "aura"})
            save_enabled(set(), path)
            self.assertEqual(load_enabled(path), set())
            path.write_text("broken", encoding="utf-8")
            self.assertEqual(load_enabled(path), {"teleport"})


if __name__ == "__main__":
    unittest.main()
