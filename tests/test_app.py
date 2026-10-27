"""Exercise actual Tk callbacks with synthetic frames, without opening a camera."""
import queue
import tkinter as tk
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import numpy as np
from app import App


class CaptureUiTest(unittest.TestCase):
    @patch("app.save_enabled")
    @patch("app.load_enabled", return_value={"teleport"})
    def test_selected_techniques_appear_and_trigger_from_sidebar(self, load, save):
        root = tk.Tk()
        try:
            app = App(root)
            root.geometry("1000x720")
            root.update_idletasks()
            self.assertEqual(set(app.effect_buttons), {"teleport", "clones", "rasengan", "aura", "matrix"})
            self.assertEqual(app.effect_buttons["aura"].winfo_manager(), "")
            app.choose_effects()
            app.engine = SimpleNamespace(commands=queue.Queue())
            for variable in app.effect_vars.values():
                variable.set(True)
            app.update_selection()
            root.update_idletasks()
            self.assertEqual(app.techniques_title.cget("text"), "TUS TECNICAS (5)")
            self.assertTrue(all(button.winfo_manager() == "grid" for button in app.effect_buttons.values()))
            app.engine.commands.get_nowait()
            app.effect_buttons["aura"].invoke()
            self.assertEqual(app.engine.commands.get_nowait(), "aura")
            app.effect_buttons["matrix"].invoke()
            self.assertEqual(app.engine.commands.get_nowait(), "matrix")
            side = app.gesture_button.master
            self.assertLessEqual(app.gesture_button.winfo_y() + app.gesture_button.winfo_height(), side.winfo_height())
            app.only_goku()
            self.assertEqual(app.effect_buttons["aura"].winfo_manager(), "")
            self.assertEqual(app.effect_buttons["teleport"].winfo_manager(), "grid")
            for variable in app.effect_vars.values():
                variable.set(False)
            app.update_selection()
            self.assertEqual(app.no_techniques.winfo_manager(), "grid")
        finally:
            root.destroy()

    @patch("app.save_enabled")
    @patch("app.load_enabled", return_value={"teleport"})
    def test_effect_dialog_updates_engine_and_only_goku(self, load, save):
        root = tk.Tk()
        root.withdraw()
        try:
            app = App(root)
            engine = SimpleNamespace(commands=queue.Queue())
            app.engine = engine
            app.choose_effects()
            self.assertFalse(app.effect_vars["rasengan"].get())
            self.assertEqual(app.effect_buttons["rasengan"].cget("state"), "disabled")
            app.effect_vars["rasengan"].set(True)
            app.update_selection()
            self.assertEqual(engine.commands.get_nowait(), ("enabled", ["rasengan", "teleport"]))
            self.assertEqual(app.effect_buttons["rasengan"].cget("state"), "normal")
            app.only_goku()
            self.assertEqual(app.enabled, {"teleport"})
            self.assertEqual(engine.commands.get_nowait(), ("enabled", ["teleport"]))
            app.command("rasengan")
            self.assertTrue(engine.commands.empty())
            save.assert_called_with({"teleport"})
        finally:
            root.destroy()

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
