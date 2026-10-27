"""Exercise actual Tk callbacks with synthetic frames, without opening a camera."""
import queue
import tkinter as tk
import unittest
from types import SimpleNamespace
import numpy as np
from app import App


class CaptureUiTest(unittest.TestCase):
    def test_capture_button_countdown_and_ready_confirmation(self):
        root = tk.Tk()
        root.withdraw()
        try:
            app = App(root)
            engine = SimpleNamespace(commands=queue.Queue(), events=queue.Queue(), frames=queue.Queue(), thread=SimpleNamespace(is_alive=lambda: True))
            app.engine = engine
            app.capture_button.invoke()
            self.assertEqual(engine.commands.get_nowait(), "capture")
            frame = np.zeros((90, 160, 3), np.uint8)
            engine.frames.put((frame, 24, False, "normal", False, 0, 5, False, "Manos: 0"))
            app.poll()
            self.assertIn("5", app.countdown_overlay.cget("text"))
            self.assertEqual(app.capture_button.cget("state"), "disabled")
            engine.events.put("FONDO LISTO")
            engine.frames.put((frame, 24, False, "normal", True, 0, None, False, "Manos: 1"))
            app.poll()
            self.assertIn("FONDO LISTO", app.background_status.cget("text"))
            self.assertEqual(app.capture_button.cget("state"), "normal")
            self.assertEqual(app.countdown_overlay.winfo_manager(), "")
            self.assertEqual(app.status.get(), "FONDO LISTO")
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
