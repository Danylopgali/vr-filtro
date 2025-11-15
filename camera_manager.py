"""Camera management utility.

Wraps basic OpenCV camera operations so other modules don't depend
on raw cv2 calls. Tries backend fallbacks on Windows (DirectShow, MediaFoundation)
to better support virtual cameras like Camo. Fails gracefully if OpenCV is not installed.
"""
from __future__ import annotations
from typing import Optional, Tuple, List, Union
import platform

try:
    import cv2  # type: ignore
except ImportError:  # pragma: no cover - environment without opencv
    cv2 = None  # type: ignore


class CameraManager:
    def __init__(self, index: int = 0, resolution: Optional[Tuple[int, int]] = None,
                 backend: Optional[Union[int, str]] = None) -> None:
        """
        Args:
            index: Camera index (e.g., 0, 1)
            resolution: Optional (width, height) to request
            backend: Optional backend selector. Examples:
                     - None: auto (on Windows tries DSHOW, MSMF, default)
                     - "dshow": Force DirectShow on Windows
                     - "msmf": Force MediaFoundation on Windows
                     - int: pass OpenCV backend constant directly (e.g., cv2.CAP_DSHOW)
        """
        self.index = index
        self.resolution = resolution
        self.backend = backend
        self._cap = None

    def open(self) -> bool:
        if cv2 is None:
            return False

        backends: List[Optional[int]] = [None]
        system = platform.system().lower()

        def to_cv_backend(name: str) -> Optional[int]:
            name = name.lower()
            if name == "dshow" and hasattr(cv2, "CAP_DSHOW"):
                return int(cv2.CAP_DSHOW)
            if name == "msmf" and hasattr(cv2, "CAP_MSMF"):
                return int(cv2.CAP_MSMF)
            if name == "avfoundation" and hasattr(cv2, "CAP_AVFOUNDATION"):
                return int(cv2.CAP_AVFOUNDATION)
            return None

        if isinstance(self.backend, int):
            backends = [int(self.backend)]
        elif isinstance(self.backend, str):
            b = to_cv_backend(self.backend)
            backends = [b] if b is not None else [None]
        else:
            # Auto mode: try platform-specific backends then default
            if system.startswith("win"):
                tried: List[Optional[int]] = []
                if hasattr(cv2, "CAP_DSHOW"):
                    tried.append(int(cv2.CAP_DSHOW))
                if hasattr(cv2, "CAP_MSMF"):
                    tried.append(int(cv2.CAP_MSMF))
                tried.append(None)  # default
                backends = tried
            elif system.startswith("darwin"):
                tried: List[Optional[int]] = []
                if hasattr(cv2, "CAP_AVFOUNDATION"):
                    tried.append(int(cv2.CAP_AVFOUNDATION))
                tried.append(None)
                backends = tried

        # Try opening with candidate backends
        last_cap = None
        for b in backends:
            cap = cv2.VideoCapture(self.index, b) if b is not None else cv2.VideoCapture(self.index)
            if cap is not None and cap.isOpened():
                self._cap = cap
                last_cap = cap
                break
            if cap is not None:
                cap.release()

        if self._cap is None:
            return False

        if self.resolution:
            w, h = self.resolution
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        return True

    def read(self):
        if self._cap is None:
            return False, None
        return self._cap.read()

    def release(self) -> None:
        if self._cap is not None:
            try:
                self._cap.release()
            finally:
                self._cap = None

    def __enter__(self) -> "CameraManager":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.release()
