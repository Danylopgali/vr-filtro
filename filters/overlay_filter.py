"""Overlay filter example.

Places an image (PNG with transparency) over the top portion of each detected face.
Requires OpenCV and a PNG asset.
"""
from __future__ import annotations
import os
from typing import List, Tuple

from filters.base_filter import BaseFilter, Detection

try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    cv2 = None  # type: ignore
    np = None  # type: ignore


class OverlayFilter(BaseFilter):
    name = "OverlayFilter"

    def __init__(self, asset_path: str, scale: float = 1.2):
        self.scale = scale
        self._overlay = None
        if cv2 is not None and os.path.exists(asset_path):
            img = cv2.imread(asset_path, cv2.IMREAD_UNCHANGED)
            if img is not None and img.shape[2] in (3, 4):
                self._overlay = img
        self.asset_path = asset_path

    def apply(self, frame, detections: List[Detection]):
        if self._overlay is None or cv2 is None or np is None:
            return frame
        for (x, y, w, h) in detections:
            # Compute overlay size (relative to face width)
            target_w = int(w * self.scale)
            aspect = self._overlay.shape[0] / self._overlay.shape[1]
            target_h = int(target_w * aspect)
            # Position above the face (like sunglasses/hat)
            oy = max(0, y - target_h // 2)
            ox = max(0, x - (target_w - w) // 2)
            resized = cv2.resize(self._overlay, (target_w, target_h), interpolation=cv2.INTER_AREA)
            self._blend_rgba(frame, resized, ox, oy)
        return frame

    def _blend_rgba(self, frame, rgba, ox, oy):
        h, w = frame.shape[:2]
        rh, rw = rgba.shape[:2]
        if ox >= w or oy >= h:
            return
        # Clip if goes outside
        rh_clipped = min(rh, h - oy)
        rw_clipped = min(rw, w - ox)
        if rh_clipped <= 0 or rw_clipped <= 0:
            return
        region = frame[oy:oy+rh_clipped, ox:ox+rw_clipped]
        rgb = rgba[:rh_clipped, :rw_clipped, :3]
        if rgba.shape[2] == 4:
            alpha = rgba[:rh_clipped, :rw_clipped, 3] / 255.0
            for c in range(3):
                region[:, :, c] = (1 - alpha) * region[:, :, c] + alpha * rgb[:, :, c]
        else:
            region[:] = rgb

__all__ = ["OverlayFilter"]
