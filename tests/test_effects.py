import unittest
from types import SimpleNamespace as Point
import numpy as np
from camera_fx.effects import Effects
from camera_fx.gestures import GestureLatch, classify


def hand(open_fingers=(True, True, False, False), offset=0):
    points = [Point(x=0.5 + offset, y=0.8) for _ in range(21)]
    for is_open, mcp, pip, tip in zip(open_fingers, (5, 9, 13, 17), (6, 10, 14, 18), (8, 12, 16, 20)):
        x = 0.45 + offset + mcp * 0.002
        points[mcp] = Point(x=x, y=0.65)
        points[pip] = Point(x=x, y=0.5)
        points[tip] = Point(x=x, y=0.25 if is_open else 0.66)
    return points


class GestureTests(unittest.TestCase):
    def test_teleport_needs_two_fingers_and_forehead(self):
        face = [Point(x=0.5, y=0.25) for _ in range(468)]
        face[234], face[454] = Point(x=0.35, y=0.4), Point(x=0.65, y=0.4)
        self.assertEqual(classify([hand()], face)[0], "teleport")
        self.assertIsNone(classify([hand(offset=0.4)], face)[0])
        self.assertIsNone(classify([hand()], None)[0])
        self.assertEqual(classify([hand((True,) * 4)], face)[0], "rasengan")

    def test_two_hands_trigger_clones(self):
        self.assertEqual(classify([hand(), hand(offset=0.05)], None)[0], "clones")
        self.assertIsNone(classify([hand(), hand(offset=0.4)], None)[0])

    def test_hold_release_and_cooldown(self):
        latch = GestureLatch()
        self.assertIsNone(latch.update("teleport", 0))
        self.assertIsNone(latch.update("teleport", 0.3))
        self.assertEqual(latch.update("teleport", 0.7), "teleport")
        self.assertIsNone(latch.update("teleport", 5))
        latch.update(None, 5.1)
        latch.update(None, 5.5)
        latch.update("teleport", 5.6)
        self.assertEqual(latch.update("teleport", 6.3), "teleport")

    def test_detection_flicker_does_not_rearm(self):
        latch = GestureLatch()
        latch.update("teleport", 0)
        latch.update("teleport", 1)
        latch.update(None, 3)
        latch.update("teleport", 3.1)
        self.assertIsNone(latch.update("teleport", 4))


class CompositingTests(unittest.TestCase):
    def setUp(self):
        self.fx = Effects()
        self.background = np.full((90, 160, 3), 25, np.uint8)
        self.frame = self.background.copy()
        self.frame[15:80, 60:100] = (50, 180, 210)

    def test_no_background_no_disappearance(self):
        self.fx.trigger("teleport", 0)
        self.assertFalse(self.fx.hidden)

    def test_hidden_output_ignores_live_person_and_returns(self):
        self.fx.capture(self.background)
        self.fx.trigger("teleport", 0)
        np.testing.assert_array_equal(self.fx.render(self.frame, None, 1), self.background)
        self.fx.trigger("teleport", 2)
        np.testing.assert_array_equal(self.fx.render(self.frame, None, 3), self.frame)

    def test_background_is_copied(self):
        self.fx.capture(self.background)
        self.background[:] = 0
        self.assertEqual(int(self.fx.background[0, 0, 0]), 25)

    def test_clone_creates_people_on_both_sides(self):
        self.fx.capture(self.background)
        self.fx.trigger("clones", 0)
        mask = np.zeros(self.frame.shape[:2], np.float32)
        mask[15:80, 60:100] = 1
        output = self.fx.render(self.frame, mask, 1)
        self.assertGreater(int(output[40, 40, 1]), 25)
        self.assertGreater(int(output[40, 120, 1]), 25)
        self.assertEqual(output.dtype, np.uint8)

    def test_rasengan_and_reset(self):
        self.fx.trigger("rasengan", 0)
        self.fx.palm = (0.5, 0.5)
        self.assertFalse(np.array_equal(self.fx.render(self.frame, None, 1), self.frame))
        self.fx.trigger("reset", 2)
        np.testing.assert_array_equal(self.fx.render(self.frame, None, 3), self.frame)


if __name__ == "__main__":
    unittest.main()
