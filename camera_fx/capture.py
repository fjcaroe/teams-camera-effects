"""Explicit countdown and clean-plate acquisition without camera dependencies."""
import math
import numpy as np


class BackgroundCapture:
    def __init__(self, delay=5, samples=8):
        self.delay, self.samples = delay, samples
        self.deadline = None
        self.frames = []

    @property
    def active(self):
        return self.deadline is not None

    def start(self, now):
        self.deadline = now + self.delay
        self.frames = []

    def countdown(self, now):
        return max(0, math.ceil(self.deadline-now)) if self.active else None

    def update(self, frame, now):
        if not self.active or now < self.deadline:
            return None
        self.frames.append(frame.copy())
        if len(self.frames) < self.samples:
            return None
        background = np.mean(self.frames, axis=0).astype(np.uint8)
        self.deadline, self.frames = None, []
        return background
