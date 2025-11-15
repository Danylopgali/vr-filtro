"""Base class for AR filters.

Implementations should override `apply(frame, detections)` and return the
modified frame. `detections` is a list of (x, y, w, h) tuples for faces.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Tuple

Detection = Tuple[int, int, int, int]


class BaseFilter(ABC):
    name: str = "BaseFilter"

    @abstractmethod
    def apply(self, frame: Any, detections: List[Detection]) -> Any:
        """Apply the filter on the given frame using detections.

        Args:
            frame: BGR image (e.g., a NumPy array from OpenCV).
            detections: List of face bounding boxes (x, y, w, h).
        Returns:
            The modified frame. Implementations can modify in-place or return a new frame.
        """
        raise NotImplementedError
