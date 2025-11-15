"""Simple face detection wrapper.

Uses OpenCV Haar cascades. If OpenCV or the cascade file is unavailable,
returns an empty list.
"""
from __future__ import annotations
from typing import List, Tuple
import os

try:
    import cv2  # type: ignore
except ImportError:  # pragma: no cover
    cv2 = None  # type: ignore


class FaceDetector:
    def __init__(self) -> None:
        self._cascade = None
        self._loaded_path = None
        if cv2 is not None:
            # Try to load default haarcascade from cv2 data if available
            try:
                base = getattr(cv2, 'data').haarcascades  # type: ignore[attr-defined]
            except Exception:
                base = None
            candidates = []
            if base:
                candidates = [
                    os.path.join(base, "haarcascade_frontalface_default.xml"),
                    os.path.join(base, "haarcascade_frontalface_alt2.xml"),
                    os.path.join(base, "haarcascade_frontalface_alt.xml"),
                ]
            for p in candidates:
                if p and os.path.exists(p):
                    c = cv2.CascadeClassifier(p)
                    if not c.empty():
                        self._cascade = c
                        self._loaded_path = p
                        break
        if self._cascade is None:
            print("[FaceDetector] Advertencia: no se pudo cargar Haar Cascade. No habrá detección de rostros.")
        else:
            print(f"[FaceDetector] Cascade cargado: {self._loaded_path}")

    def detect(self, frame) -> List[Tuple[int, int, int, int]]:
        if cv2 is None or self._cascade is None:
            return []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Improve contrast for low light
        try:
            gray = cv2.equalizeHist(gray)
        except Exception:
            pass
        faces = self._cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
        )
        if len(faces) == 0:
            # Fallback pass: slightly more sensitive
            faces = self._cascade.detectMultiScale(
                gray, scaleFactor=1.05, minNeighbors=4, minSize=(30, 30)
            )
        return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]
