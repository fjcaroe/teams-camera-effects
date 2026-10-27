import queue
import threading
import time
from contextlib import ExitStack

import cv2
import mediapipe as mp
import pyvirtualcam

from .effects import Effects
from .gestures import GestureLatch, classify
from .capture import BackgroundCapture
from .settings import DEFAULT_ENABLED


class CameraEngine:
    def __init__(self, camera=0, virtual=True, enabled=None):
        self.camera, self.virtual = camera, virtual
        self.enabled = set(DEFAULT_ENABLED if enabled is None else enabled)
        self.commands = queue.Queue()
        self.frames = queue.Queue(maxsize=1)
        self.events = queue.Queue()
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.run, daemon=True, name="camera-effects")
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def run(self):
        cap = None
        try:
            with ExitStack() as stack:
                cap = cv2.VideoCapture(self.camera, cv2.CAP_DSHOW)
                if not cap.isOpened():
                    raise RuntimeError("No se pudo abrir la webcam. Prueba otro indice o cierra otras apps que la usen.")
                stack.callback(cap.release)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
                cap.set(cv2.CAP_PROP_FPS, 24)
                hands = stack.enter_context(mp.solutions.hands.Hands(max_num_hands=2, model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5))
                face = stack.enter_context(mp.solutions.face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=False))
                segment = stack.enter_context(mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1))
                fx, latch = Effects(), GestureLatch()
                fx.set_enabled(self.enabled)
                virtual_cam = None
                virtual_attempted = False
                capture = BackgroundCapture()
                last_face, last_face_at = None, -100.0
                gestures_enabled = True
                previous = time.monotonic()
                fps = 0.0
                failures = 0
                self.events.put("Webcam lista. Captura el fondo para teletransportarte.")
                while not self.stop_event.is_set():
                    begin = time.monotonic()
                    ok, frame = cap.read()
                    if not ok:
                        failures += 1
                        if failures > 15:
                            raise RuntimeError("Se perdio la webcam. Reconectala y pulsa Iniciar.")
                        self.stop_event.wait(0.05)
                        continue
                    failures = 0
                    frame = cv2.resize(frame, (960, 540))
                    now = time.monotonic()
                    while not self.commands.empty():
                        action = self.commands.get_nowait()
                        if isinstance(action, tuple) and action[0] == "enabled":
                            fx.set_enabled(action[1])
                            latch = GestureLatch()
                            self.events.put("Seleccion de efectos actualizada")
                        elif action == "capture":
                            capture.start(now)
                            self.events.put("Apartate de la camara: capturando el fondo en 5 segundos.")
                        elif action == "gestures":
                            gestures_enabled = not gestures_enabled
                            latch = GestureLatch()
                            self.events.put("Gestos activados" if gestures_enabled else "Gestos pausados · controles manuales disponibles")
                        else:
                            self.events.put(fx.trigger(action, now))
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    rgb.flags.writeable = False
                    hand_result = hands.process(rgb)
                    face_result = face.process(rgb)
                    hand_points = [h.landmark for h in (hand_result.multi_hand_landmarks or [])]
                    face_points = face_result.multi_face_landmarks[0].landmark if face_result.multi_face_landmarks else None
                    if face_points is not None:
                        last_face, last_face_at = face_points, now
                    # Brief occlusion by the Goku hand should not erase the head location.
                    tracked_face = last_face if now - last_face_at < 0.8 else None
                    gesture, palm = classify(hand_points, tracked_face)
                    fx.palm = palm
                    if capture.active:
                        background = capture.update(frame, now)
                        if background is not None:
                            fx.capture(background)
                            latch = GestureLatch()
                            self.events.put("FONDO LISTO. Vuelve al encuadre. Prueba el boton Teletransporte o dos dedos en la frente.")
                    elif gestures_enabled:
                        fired = latch.update(gesture if fx.gesture_allowed(gesture) else None, now)
                        if fired:
                            self.events.put(fx.trigger(fired, now))
                    mask = segment.process(rgb).segmentation_mask if fx.mode in ("clones", "aura") and not fx.hidden else None
                    output = fx.render(frame, mask, now)
                    if not virtual_attempted and self.virtual:
                        virtual_attempted = True
                        try:
                            virtual_cam = stack.enter_context(pyvirtualcam.Camera(width=960, height=540, fps=24, fmt=pyvirtualcam.PixelFormat.BGR, backend="obs"))
                            self.events.put("Salida activa: OBS Virtual Camera. Seleccionala en Teams.")
                        except RuntimeError:
                            self.events.put("Vista previa activa. Para enviar a Teams instala OBS Studio, cierra su camara virtual y reinicia esta captura.")
                    if virtual_cam is not None:
                        virtual_cam.send(output)
                    fps = fps * 0.9 + 0.1 / max(0.001, now - previous)
                    previous = now
                    countdown = capture.countdown(now)
                    tracking = f"Manos: {len(hand_points)} | Rostro: {'detectado' if face_points else 'reciente' if tracked_face else 'no detectado'} | Gesto: {gesture or 'ninguno'}"
                    if gesture and not fx.gesture_allowed(gesture):
                        tracking += " (ignorado)"
                    snapshot = (output, fps, fx.hidden, fx.mode, fx.background is not None, latch.progress(now), countdown, virtual_cam is not None, tracking)
                    if self.frames.full():
                        try:
                            self.frames.get_nowait()
                        except queue.Empty:
                            pass
                    self.frames.put_nowait(snapshot)
                    self.stop_event.wait(max(0, 1 / 24 - (time.monotonic() - begin)))
        except Exception as exc:
            self.events.put(f"Error: {exc}")
        finally:
            # ExitStack also releases models / virtual camera on failure.
            if cap is not None:
                cap.release()
            self.events.put("__stopped__")
