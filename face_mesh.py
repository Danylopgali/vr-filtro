"""Face mesh detector using MediaPipe.

Provides a simple wrapper to obtain facial landmarks.
Falls back gracefully if mediapipe or OpenCV are not installed.
"""
from __future__ import annotations
from typing import List, Tuple

try:
    import cv2  # type: ignore
except ImportError:  # pragma: no cover
    cv2 = None  # type: ignore

try:
    import mediapipe as mp  # type: ignore
except ImportError:  # pragma: no cover
    mp = None  # type: ignore


class FaceMeshDetector:
    def __init__(self, max_faces: int = 1, refine_landmarks: bool = True):
        self._mesh = None
        if mp is not None:
            self._mesh = mp.solutions.face_mesh.FaceMesh(
                max_num_faces=max_faces,
                refine_landmarks=refine_landmarks,
                static_image_mode=False,
            )
        # Store drawing utils only if available
        self._draw = mp.solutions.drawing_utils if mp is not None else None
        self._spec = mp.solutions.drawing_styles.get_default_face_mesh_tesselation_style() if mp is not None else None
        self._available = self._mesh is not None and cv2 is not None

    def available(self) -> bool:
        """Return True if mediapipe and opencv are available and initialized."""
        return bool(self._available)

    def detect(self, frame) -> List[List[Tuple[int, int]]]:
        """Detecta rostros y retorna sus landmarks (puntos faciales).
        
        MediaPipe Face Mesh detecta 468 puntos en cada rostro:
        - Landmark 1: punta de la nariz
        - Landmarks 33, 133, 362, 263: esquinas de ojos
        - Landmarks 61, 291: comisuras de labios
        - Y muchos más...
        
        Returns:
            Lista de rostros. Cada rostro es una lista de 468 tuplas (x, y) en píxeles.
            Ejemplo: [[(x1, y1), (x2, y2), ..., (x468, y468)]]
        """
        if self._mesh is None or cv2 is None:
            return []
            
        # ========== PREPARAR IMAGEN PARA MEDIAPIPE ==========
        h, w = frame.shape[:2]  # Alto y ancho del frame
        
        # MediaPipe requiere RGB, OpenCV usa BGR
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # ========== PROCESAR FRAME ==========
        # MediaPipe detecta rostros y calcula 468 landmarks por rostro
        result = self._mesh.process(rgb)
        
        # ========== CONVERTIR LANDMARKS A PÍXELES ==========
        faces: List[List[Tuple[int, int]]] = []
        
        if result.multi_face_landmarks:  # Si se detectó al menos un rostro
            for lm in result.multi_face_landmarks:  # Para cada rostro detectado
                # MediaPipe retorna coordenadas normalizadas (0.0 - 1.0)
                # Las convertimos a píxeles multiplicando por ancho/alto
                pts = [(int(p.x * w), int(p.y * h)) for p in lm.landmark]
                faces.append(pts)
                
        return faces

    def draw(self, frame, faces: List[List[Tuple[int, int]]]) -> None:
        if cv2 is None or self._draw is None or mp is None:
            return
        h, w = frame.shape[:2]
        for face_points in faces:
            # MediaPipe original structure is required for built-in drawing; we reconstruct minimal proto
            # Instead, we can just draw small circles for simplicity.
            for (x, y) in face_points:
                cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)


def bounding_box_from_landmarks(landmarks: List[Tuple[int, int]]):
    if not landmarks:
        return None
    xs = [x for x, _ in landmarks]
    ys = [y for _, y in landmarks]
    return min(xs), min(ys), max(xs), max(ys)

__all__ = ["FaceMeshDetector", "bounding_box_from_landmarks"]
