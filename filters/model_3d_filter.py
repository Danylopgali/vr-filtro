"""Filtro 3D con seguimiento de pose facial usando solvePnP.

Este filtro carga modelos 3D (.glb o .obj) y los renderiza sobre el rostro
usando la pose calculada con MediaPipe y cv2.solvePnP.
"""
from __future__ import annotations
import os
from typing import List, Tuple, Optional, Any
import numpy as np

from filters.base_filter import BaseFilter, Detection

try:
    import cv2
except ImportError:
    cv2 = None

# ========== CONFIGURACIÓN DE PUNTOS FACIALES ==========
# Índices de MediaPipe para puntos robustos del rostro (468 landmarks)
MP_IDXS = [33, 263, 1, 61, 291, 199]
# Significado:
# 33  = ojo izquierdo (outer corner)
# 263 = ojo derecho (outer corner)
# 1   = punta de la nariz
# 61  = comisura izquierda de la boca
# 291 = comisura derecha de la boca
# 199 = mentón

# Coordenadas 3D canónicas (en "metros relativos") para los 6 puntos
# Estos valores representan un modelo 3D básico del rostro humano
CANON_FACE_3D = np.array([
    [-0.5, -0.3, 0.0],   # 33:  ojo izquierdo
    [0.5, -0.3, 0.0],    # 263: ojo derecho
    [0.0, 0.0, 0.5],     # 1:   punta nariz (proyectada hacia adelante)
    [-0.3, 0.4, 0.2],    # 61:  comisura izquierda boca
    [0.3, 0.4, 0.2],     # 291: comisura derecha boca
    [0.0, 0.8, 0.3],     # 199: mentón
], dtype=np.float64)


class Model3DFilter(BaseFilter):
    """Filtro que renderiza modelos 3D usando pose facial calculada con solvePnP.
    
    Attributes:
        model_path: Ruta al archivo del modelo 3D (.glb o .obj)
        color: Color BGR para renderizar el modelo como sólido (ej. (255,170,80))
        alpha: Opacidad del overlay (1.0 = opaco, 0.6 = semitransparente)
        mp_idxs: Índices de landmarks de MediaPipe para calcular pose
        canon_face_3d: Coordenadas 3D canónicas del rostro de referencia
    """
    name = "Model3DFilter"
    
    def __init__(
        self,
        model_path: str,
        color: Tuple[int, int, int] = (255, 170, 80),
        alpha: float = 0.6,
        face_mesh_detector: Optional[Any] = None
    ):
        """Inicializa el filtro 3D.
        
        Args:
            model_path: Ruta al modelo 3D (.glb o .obj)
            color: Color BGR para renderizar (ej. (255,170,80) para azul-naranja)
            alpha: Opacidad del overlay (1.0 = opaco; 0.6 = más transparente)
            face_mesh_detector: Instancia de FaceMeshDetector (opcional, para landmarks)
        """
        self.model_path = model_path
        self.color = color
        self.alpha = alpha
        self.face_mesh_detector = face_mesh_detector
        
        # Puntos robustos de MediaPipe
        self.mp_idxs = MP_IDXS
        self.canon_face_3d = CANON_FACE_3D
        
        # Verificar que el modelo existe
        if not os.path.exists(model_path):
            print(f"⚠️  Modelo 3D no encontrado: {model_path}")
            self.model_loaded = False
        else:
            print(f"✓ Modelo 3D cargado: {model_path}")
            self.model_loaded = True
            self._load_model()
    
    def _load_model(self) -> None:
        """Carga el modelo 3D desde el archivo.
        
        TODO: Implementar carga de .glb (usando trimesh/pygltflib) o .obj (usando PyWavefront).
        Por ahora, solo guarda la ruta para uso posterior.
        """
        # Placeholder: aquí cargarías el modelo con trimesh, pygltflib, etc.
        # Por ejemplo:
        # if self.model_path.endswith('.glb'):
        #     import trimesh
        #     self.mesh = trimesh.load(self.model_path)
        # elif self.model_path.endswith('.obj'):
        #     import pywavefront
        #     self.mesh = pywavefront.Wavefront(self.model_path)
        
        print(f"[Model3DFilter] Modelo preparado: {self.model_path}")
    
    def apply(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """Aplica el filtro 3D sobre el frame usando la pose facial.
        
        Args:
            frame: Imagen BGR de OpenCV
            detections: Lista de bounding boxes de rostros (x, y, w, h)
        
        Returns:
            Frame modificado con el modelo 3D renderizado
        """
        if cv2 is None or not self.model_loaded:
            return frame
        
        # Si no hay face_mesh_detector, no podemos calcular la pose
        if self.face_mesh_detector is None:
            return frame
        
        # Procesar cada rostro detectado
        for detection in detections:
            x, y, w, h = detection
            
            # Obtener landmarks de MediaPipe para este rostro
            landmarks = self._get_face_landmarks(frame, detection)
            if landmarks is None:
                continue
            
            # Calcular pose con solvePnP
            rvec, tvec, camera_matrix = self._calculate_pose(frame, landmarks)
            if rvec is None:
                continue
            
            # Renderizar modelo 3D con la pose calculada
            frame = self._render_3d_model(frame, rvec, tvec, camera_matrix)
        
        return frame
    
    def _get_face_landmarks(
        self, 
        frame: np.ndarray, 
        detection: Detection
    ) -> Optional[np.ndarray]:
        """Extrae landmarks 2D de MediaPipe para los puntos clave.
        
        Args:
            frame: Imagen BGR
            detection: Bounding box del rostro (x, y, w, h)
        
        Returns:
            Array (6, 2) con coordenadas (x, y) de los 6 puntos, o None si falla
        """
        # Obtener landmarks de MediaPipe (468 puntos)
        # face_mesh_detector.detect() retorna lista de rostros
        # Cada rostro es una lista de 468 tuplas (x, y) en píxeles
        results = self.face_mesh_detector.detect(frame)
        
        if not results or len(results) == 0:
            return None
        
        # Usar el primer rostro detectado
        face_landmarks = results[0]  # Lista de 468 tuplas (x, y)
        
        # Extraer solo los 6 puntos que necesitamos (MP_IDXS)
        landmarks_2d = []
        for idx in self.mp_idxs:
            if idx < len(face_landmarks):
                x, y = face_landmarks[idx]
                landmarks_2d.append([x, y])
        
        if len(landmarks_2d) != 6:
            return None
        
        return np.array(landmarks_2d, dtype=np.float64)
    
    def _calculate_pose(
        self,
        frame: np.ndarray,
        landmarks_2d: np.ndarray
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
        """Calcula la pose 3D del rostro usando cv2.solvePnP.
        
        Args:
            frame: Imagen BGR
            landmarks_2d: Array (6, 2) con coordenadas 2D de los puntos clave
        
        Returns:
            Tupla (rvec, tvec, camera_matrix):
            - rvec: Vector de rotación (3, 1)
            - tvec: Vector de translación (3, 1)
            - camera_matrix: Matriz intrínseca de la cámara (3, 3)
            Retorna (None, None, None) si falla
        """
        h, w = frame.shape[:2]
        
        # Construir matriz de cámara simplificada (focal length aproximada)
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)
        
        # Sin distorsión (simplificación)
        dist_coeffs = np.zeros((4, 1), dtype=np.float64)
        
        # Resolver PnP: encuentra rvec y tvec que mapean 3D → 2D
        success, rvec, tvec = cv2.solvePnP(
            self.canon_face_3d,    # Puntos 3D canónicos
            landmarks_2d,          # Puntos 2D detectados
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if not success:
            return None, None, None
        
        return rvec, tvec, camera_matrix
    
    def _render_3d_model(
        self,
        frame: np.ndarray,
        rvec: np.ndarray,
        tvec: np.ndarray,
        camera_matrix: np.ndarray
    ) -> np.ndarray:
        """Renderiza el modelo 3D sobre el frame usando la pose calculada.
        
        Args:
            frame: Imagen BGR
            rvec: Vector de rotación de la pose
            tvec: Vector de translación de la pose
            camera_matrix: Matriz intrínseca de la cámara
        
        Returns:
            Frame con el modelo 3D renderizado
        """
        # TODO: Implementar renderizado real del modelo 3D
        # Por ahora, dibujamos ejes de coordenadas como ejemplo
        
        # Definir ejes 3D (x, y, z) de longitud 1.0
        axis_points = np.array([
            [0, 0, 0],       # Origen
            [1.0, 0, 0],     # Eje X (rojo)
            [0, 1.0, 0],     # Eje Y (verde)
            [0, 0, 1.0],     # Eje Z (azul)
        ], dtype=np.float64)
        
        # Proyectar puntos 3D a 2D
        img_points, _ = cv2.projectPoints(
            axis_points,
            rvec,
            tvec,
            camera_matrix,
            np.zeros((4, 1))
        )
        img_points = img_points.reshape(-1, 2).astype(int)
        
        # Crear overlay con transparencia
        overlay = frame.copy()
        
        # Dibujar ejes de coordenadas
        origin = tuple(img_points[0])
        x_axis = tuple(img_points[1])
        y_axis = tuple(img_points[2])
        z_axis = tuple(img_points[3])
        
        cv2.line(overlay, origin, x_axis, (0, 0, 255), 3)    # X = rojo
        cv2.line(overlay, origin, y_axis, (0, 255, 0), 3)    # Y = verde
        cv2.line(overlay, origin, z_axis, (255, 0, 0), 3)    # Z = azul
        
        # Aplicar transparencia (alpha blending)
        cv2.addWeighted(overlay, self.alpha, frame, 1 - self.alpha, 0, frame)
        
        # TODO: Aquí renderizarías el modelo 3D real usando los vértices del mesh
        # Ejemplo conceptual:
        # for triangle in self.mesh.triangles:
        #     pts_3d = self.mesh.vertices[triangle]
        #     pts_2d, _ = cv2.projectPoints(pts_3d, rvec, tvec, camera_matrix, dist_coeffs)
        #     cv2.fillPoly(frame, [pts_2d.astype(int)], self.color)
        
        return frame
