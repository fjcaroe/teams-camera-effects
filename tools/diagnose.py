"""Model / optional hardware smoke check. Never saves webcam frames."""
import argparse
import queue
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, help="Prueba webcam unos segundos sin grabar")
    parser.add_argument("--virtual", action="store_true", help="Prueba salida OBS; sin --camera envia imagen sintetica")
    args = parser.parse_args()
    if args.camera is not None:
        from camera_fx.engine import CameraEngine
        engine = CameraEngine(args.camera, virtual=args.virtual)
        engine.start()
        count, virtual = 0, False
        deadline = time.monotonic() + 15
        try:
            while time.monotonic() < deadline and engine.thread.is_alive():
                try:
                    snapshot = engine.frames.get(timeout=0.5)
                    count += 1
                    virtual = snapshot[-1]
                    if count >= 12:
                        break
                except queue.Empty:
                    pass
        finally:
            engine.stop()
            engine.thread.join(timeout=10)
        while not engine.events.empty():
            print(engine.events.get())
        print(f"Frames procesados: {count}; salida virtual: {virtual}")
        return 0 if count > 0 and (not args.virtual or virtual) and not engine.thread.is_alive() else 1
    import mediapipe as mp
    import numpy as np
    import pyvirtualcam
    image = np.zeros((240, 320, 3), np.uint8)
    with mp.solutions.hands.Hands(model_complexity=0) as hands, mp.solutions.face_mesh.FaceMesh() as face, mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1) as segment:
        hands.process(image)
        face.process(image)
        assert segment.process(image).segmentation_mask.shape == (240, 320)
    print("Modelos locales: OK (manos, rostro, segmentacion)")
    if args.virtual:
        with pyvirtualcam.Camera(width=320, height=240, fps=24, fmt=pyvirtualcam.PixelFormat.BGR, backend="obs") as cam:
            for _ in range(24):
                cam.send(image)
                cam.sleep_until_next_frame()
            print(f"Camara virtual: OK ({cam.device})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
