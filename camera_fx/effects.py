"""Frame compositing. All images are BGR uint8; no camera access here."""
import math
import cv2
import numpy as np


class Effects:
    def __init__(self):
        self.background = None
        self.hidden = False
        self.mode = "normal"
        self.flash_at = -100.0
        self.palm = None

    def capture(self, frame):
        self.background = frame.copy()
        self.hidden = False

    def trigger(self, action, now):
        if action == "teleport":
            if self.background is None:
                return "Primero captura el fondo vacio."
            self.hidden = not self.hidden
            self.flash_at = now
            return "Invisible · repite el gesto para volver" if self.hidden else "De vuelta en escena"
        if action == "clones":
            if self.background is None:
                return "Captura el fondo para crear clones."
            self.hidden = False
            self.mode = "normal" if self.mode == "clones" else "clones"
            self.flash_at = now
        elif action == "rasengan":
            self.mode = "normal" if self.mode == "rasengan" else "rasengan"
        elif action == "reset":
            self.hidden, self.mode, self.flash_at = False, "normal", -100.0
        return {"normal": "Camara normal", "clones": "Kage Bunshin activado", "rasengan": "Rasengan activado · muestra la palma"}[self.mode]

    def render(self, frame, mask, now):
        h, w = frame.shape[:2]
        if self.hidden and self.background is not None:
            output = self.background.copy()
        elif self.mode == "clones" and self.background is not None and mask is not None:
            alpha = cv2.GaussianBlur(np.clip((mask - 0.15) / 0.7, 0, 1), (9, 9), 0)[..., None]
            output = self.background.astype(np.float32)
            for shift, opacity in ((-int(w * 0.27), 0.8), (int(w * 0.27), 0.8), (0, 1.0)):
                transform = np.float32([[1, 0, shift], [0, 1, 0]])
                shifted = cv2.warpAffine(frame, transform, (w, h)).astype(np.float32)
                a = cv2.warpAffine(alpha, transform, (w, h))
                if a.ndim == 2:
                    a = a[..., None]
                a = a * opacity
                output = shifted * a + output * (1 - a)
            output = output.clip(0, 255).astype(np.uint8)
        else:
            output = frame.copy()
        if self.mode == "rasengan" and self.palm is not None and not self.hidden:
            x, y = int(self.palm[0] * w), int(self.palm[1] * h)
            radius = max(20, int(w * 0.055))
            glow = np.zeros_like(output)
            cv2.circle(glow, (x, y), radius, (255, 155, 30), -1, cv2.LINE_AA)
            glow = cv2.GaussianBlur(glow, (0, 0), radius * 0.4)
            output = cv2.addWeighted(output, 1, glow, 1.4, 0)
            for i in range(7):
                angle = now * 220 + i * 180 / 7
                cv2.ellipse(output, (x, y), (radius, max(5, radius // 3)), angle, 0, 285, (255, 230, 160), 2, cv2.LINE_AA)
            cv2.circle(output, (x, y), radius // 4, (255, 255, 245), -1, cv2.LINE_AA)
        elapsed = now - self.flash_at
        if 0 <= elapsed < 0.5:
            strength = (1 - elapsed / 0.5) * 0.8
            output = cv2.addWeighted(output, 1 - strength, np.full_like(output, 255), strength, 0)
            # Speed lines suggest instant transmission without imported assets.
            for i in range(28):
                x = int((i + 0.5) * w / 28)
                length = int(h * (0.1 + 0.2 * abs(math.sin(i * 2.3))))
                cv2.line(output, (x, h // 2 - length), (x, h // 2 + length), (245, 235, 205), 1)
        return output
