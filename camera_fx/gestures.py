"""Geometry and gesture debounce, independent of camera / MediaPipe runtime."""
from dataclasses import dataclass
import math


def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def extended(hand, tip, pip, mcp):
    # Depth matters when pointing the fingers toward the forehead / camera.
    def d(a, b):
        return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2 + (getattr(a, "z", 0)-getattr(b, "z", 0))**2)
    return d(hand[tip], hand[0]) > d(hand[pip], hand[0]) * 1.08 and d(hand[tip], hand[mcp]) > d(hand[pip], hand[mcp]) * 1.2


def fingers(hand):
    return [extended(hand, *indices) for indices in ((8, 6, 5), (12, 10, 9), (16, 14, 13), (20, 18, 17))]


def classify(hands, face):
    """Return exclusive gesture plus palm position (normalized)."""
    for hand in hands:
        index, middle, ring, pinky = fingers(hand)
        if face and index and middle and not ring and not pinky:
            # Forehead and temples: tolerate either side and natural finger spacing.
            forehead = face[10]
            brow = face[168]
            head_width = distance(face[234], face[454])
            tips = (hand[8], hand[12])
            if any(min(distance(t, forehead), distance(t, brow)) < max(0.09, head_width * 0.8) for t in tips):
                return "teleport", None
    if len(hands) == 2:
        if all(fingers(h)[0] for h in hands) and distance(hands[0][8], hands[1][8]) < 0.18:
            return "clones", None
    for hand in hands:
        if all(fingers(hand)):
            return "rasengan", (hand[9].x, hand[9].y)
    return None, None


@dataclass
class GestureLatch:
    hold: float = 0.6
    release: float = 0.35
    cooldown: float = 1.8
    candidate: str | None = None
    since: float = 0.0
    latched: bool = False
    released_at: float | None = None
    last_fire: float = -100.0
    dropout_grace: float = 0.18

    def update(self, gesture, now):
        if gesture is None:
            if self.released_at is None:
                self.released_at = now
            if now - self.released_at >= self.dropout_grace:
                self.candidate = None
            if now - self.released_at >= self.release:
                self.latched = False
            return None
        if self.released_at is not None and now - self.released_at >= self.dropout_grace:
            self.candidate = None
        self.released_at = None
        if gesture != self.candidate:
            self.candidate, self.since = gesture, now
        if not self.latched and now - self.since >= self.hold and now - self.last_fire >= self.cooldown:
            self.latched, self.last_fire = True, now
            return gesture
        return None

    def progress(self, now):
        return 0.0 if self.candidate is None or self.latched else min(1.0, (now - self.since) / self.hold)
