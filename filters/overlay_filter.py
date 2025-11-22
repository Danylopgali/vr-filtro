"""Overlay filter example.

Places an image (PNG with transparency) over the top portion of each detected face.
Requires OpenCV and a PNG asset.
"""
from __future__ import annotations
import os
from typing import List, Tuple, Union

from filters.base_filter import BaseFilter, Detection

try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    cv2 = None  # type: ignore
    np = None  # type: ignore


class OverlayFilter(BaseFilter):
    name = "OverlayFilter"

    def __init__(self, asset_path: Union[str, List[str]], scale: float = 1.2):
        """Inicializa el filtro con uno o varios assets (imágenes PNG).
        
        Args:
            asset_path: Ruta a un PNG o lista de rutas para múltiples PNGs
            scale: Factor de escala para redimensionar la imagen
        """
        self.scale = scale
        self.offset_x = 0  # Desplazamiento horizontal en píxeles
        self.offset_y = 0  # Desplazamiento vertical en píxeles
        
        # ========== CARGAR ASSETS (UNO O VARIOS) ==========
        # Si se pasa un string, convertir a lista de un elemento
        if isinstance(asset_path, str):
            asset_path = [asset_path]
        
        # Lista de assets cargados (imágenes PNG con transparencia)
        self.assets: List[np.ndarray] = []
        self.asset_paths: List[str] = []
        
        # Cargar cada PNG de la lista
        if cv2 is not None:
            for path in asset_path:
                if os.path.exists(path):
                    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                    if img is not None and len(img.shape) >= 2:
                        # Agregar canal alpha si no tiene (convertir a BGRA)
                        if img.shape[2] == 3:
                            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
                        self.assets.append(img)
                        self.asset_paths.append(path)
        
        # Índice del asset actualmente activo
        self.asset_index = 0 if self.assets else -1
        
        # Compatibilidad con código antiguo
        self._overlay = self.assets[0] if self.assets else None
        self.asset_path = self.asset_paths[0] if self.asset_paths else asset_path[0] if asset_path else ""
    
    def next_asset(self) -> None:
        """Avanza al siguiente PNG de la lista de assets.
        
        Si está en el último asset, vuelve al primero (comportamiento circular).
        Útil para cambiar entre diferentes mostachos, gafas, sombreros, etc.
        """
        if len(self.assets) > 1:
            self.asset_index = (self.asset_index + 1) % len(self.assets)
            self._overlay = self.assets[self.asset_index]
            print(f"[OverlayFilter] Cambiando a asset {self.asset_index + 1}/{len(self.assets)}: {self.asset_paths[self.asset_index]}")
    
    def add_offset_x(self, dx: int) -> None:
        """Ajusta el desplazamiento horizontal del overlay.
        
        Args:
            dx: Píxeles a desplazar (positivo = derecha, negativo = izquierda)
        
        Ejemplo:
            filter.add_offset_x(10)   # Mover 10px a la derecha
            filter.add_offset_x(-5)   # Mover 5px a la izquierda
        """
        self.offset_x += dx
        print(f"[OverlayFilter] Offset X: {self.offset_x}px")
    
    def add_offset_y(self, dy: int) -> None:
        """Ajusta el desplazamiento vertical del overlay.
        
        Args:
            dy: Píxeles a desplazar (positivo = abajo, negativo = arriba)
        """
        self.offset_y += dy
        print(f"[OverlayFilter] Offset Y: {self.offset_y}px")
    
    def reset_offset(self) -> None:
        """Reinicia los desplazamientos a cero (posición original)."""
        self.offset_x = 0
        self.offset_y = 0
        print("[OverlayFilter] Offsets reiniciados")

    def apply(self, frame, detections: List[Detection]):
        """Aplica la imagen PNG sobre las detecciones en el frame.
        
        Args:
            frame: Imagen BGR de la cámara (numpy array)
            detections: Lista de tuplas (x, y, w, h) donde colocar el overlay
                       x, y = esquina superior izquierda
                       w, h = ancho y alto del área objetivo
        """
        if self._overlay is None or cv2 is None or np is None:
            return frame
            
        # Procesar cada detección (puede haber múltiples caras/narices)
        for (x, y, w, h) in detections:
            # ========== CALCULAR TAMAÑO DEL OVERLAY ==========
            # Redimensionar la imagen según el ancho de la detección
            target_w = int(w * self.scale)  # scale controla qué tan grande se ve
            
            # Mantener proporción de la imagen (aspect ratio)
            aspect = self._overlay.shape[0] / self._overlay.shape[1]  # alto / ancho
            target_h = int(target_w * aspect)
            
            # ========== CALCULAR POSICIÓN ==========
            # Centrar la imagen en el área detectada
            oy = max(0, y - target_h // 2 + self.offset_y)  # Posición Y + offset vertical
            ox = max(0, x - (target_w - w) // 2 + self.offset_x)  # Posición X + offset horizontal
            
            # ========== REDIMENSIONAR IMAGEN ==========
            resized = cv2.resize(self._overlay, (target_w, target_h), 
                               interpolation=cv2.INTER_AREA)
            
            # ========== SUPERPONER CON TRANSPARENCIA ==========
            # Mezcla la imagen PNG con el frame usando el canal alpha
            self._blend_rgba(frame, resized, ox, oy)
        return frame

    def _blend_rgba(self, frame, rgba, ox, oy):
        """Mezcla una imagen RGBA con transparencia en el frame.
        
        Args:
            frame: Frame de video BGR (modificado in-place)
            rgba: Imagen PNG con canal alpha (transparencia)
            ox, oy: Posición donde colocar la imagen (esquina superior izquierda)
        """
        h, w = frame.shape[:2]  # Alto y ancho del frame de la cámara
        rh, rw = rgba.shape[:2]  # Alto y ancho de la imagen overlay
        
        # Verificar que no está completamente fuera del frame
        if ox >= w or oy >= h:
            return
            
        # ========== RECORTAR SI SE SALE DEL BORDE ==========
        # Ajustar dimensiones si la imagen se sale del frame
        rh_clipped = min(rh, h - oy)  # Recortar altura si toca el borde inferior
        rw_clipped = min(rw, w - ox)  # Recortar ancho si toca el borde derecho
        
        if rh_clipped <= 0 or rw_clipped <= 0:
            return
            
        # ========== EXTRAER REGIÓN DEL FRAME ==========
        # Área del frame donde se colocará el overlay
        region = frame[oy:oy+rh_clipped, ox:ox+rw_clipped]
        
        # Componentes RGB de la imagen overlay (sin canal alpha)
        rgb = rgba[:rh_clipped, :rw_clipped, :3]
        
        # ========== APLICAR TRANSPARENCIA (ALPHA BLENDING) ==========
        if rgba.shape[2] == 4:  # Si tiene canal alpha (4 canales: BGRA)
            # Normalizar alpha de 0-255 a 0.0-1.0
            alpha = rgba[:rh_clipped, :rw_clipped, 3] / 255.0
            
            # Mezclar cada canal de color (B, G, R)
            # Fórmula: resultado = (1 - alpha) * fondo + alpha * overlay
            for c in range(3):  # Para cada canal (Blue, Green, Red)
                region[:, :, c] = (1 - alpha) * region[:, :, c] + alpha * rgb[:, :, c]
        else:
            # Si no tiene transparencia, simplemente reemplazar
            region[:] = rgb

__all__ = ["OverlayFilter"]
