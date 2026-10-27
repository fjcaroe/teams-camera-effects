"""Frame compositing. All images are BGR uint8; no camera access here."""
import math
import cv2
import numpy as np
from .settings import CATALOG


class Effects:
    def __init__(self):
        self.background = None
        self.hidden = False
        self.mode = "normal"
        self.flash_at = -100.0
        self.palm = None
        self.enabled = set(CATALOG)

    def set_enabled(self, enabled):
        self.enabled = set(enabled) & CATALOG.keys()
        if "teleport" not in self.enabled:
            self.hidden = False
        if self.mode not in self.enabled:
            self.mode = "normal"

    def gesture_allowed(self, gesture):
        # While invisible, only Goku can change the scene automatically.
        return gesture in self.enabled and (not self.hidden or gesture == "teleport")

    def capture(self, frame):
        self.background = frame.copy()
        self.hidden = False

    def trigger(self, action, now):
        if action in CATALOG and action not in self.enabled:
            return "Efecto desactivado. Habilitalo en Elegir efectos."
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
        elif action in ("rasengan", "aura", "matrix"):
            self.mode = "normal" if self.mode == action else action
        elif action == "reset":
            self.hidden, self.mode, self.flash_at = False, "normal", -100.0
        return {"normal": "Camara normal", "clones": "Kage Bunshin activado", "rasengan": "Rasengan activado · muestra la palma", "aura": "Aura Super Saiyan activada", "matrix": "Matrix activado"}[self.mode]

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
        if self.mode == "aura" and mask is not None and not self.hidden:
            silhouette = (mask > 0.5).astype(np.uint8)
            radius = max(5, w // 65)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (radius * 2 + 1, radius * 2 + 1))
            edge = cv2.dilate(silhouette, kernel) - cv2.erode(silhouette, kernel)
            glow = cv2.GaussianBlur(edge.astype(np.float32), (0, 0), radius)
            tint = np.array([15, 190, 255], np.float32)
            output = np.clip(output.astype(np.float32) + glow[..., None] * tint * (1.2 + 0.3 * math.sin(now * 8)), 0, 255).astype(np.uint8)
        if self.mode == "matrix" and not self.hidden:
            gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
            output = np.stack((gray // 6, gray * 0.65, gray // 8), axis=-1).astype(np.uint8)
            step = max(16, w // 38)
            for column, x in enumerate(range(0, w, step)):
                head = int((now * (65 + column % 5 * 17) + column * 89) % (h + step * 10))
                for trail in range(10):
                    y = head - trail * step
                    glyph = str((column * 7 + trail + int(now * 5)) % 2)
                    cv2.putText(output, glyph, (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (40, max(40, 255-trail*20), 40), 1, cv2.LINE_AA)
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
