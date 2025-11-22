#!/usr/bin/env python3
"""
Entry point for the filtros-ar project.

- Opens the selected camera
- Detects faces (Haar) and optionally shows face mesh (MediaPipe)
- Draws bounding boxes and/or landmarks on the video stream

Requirements (when running):
- opencv-python
- mediapipe (optional, for mesh)

Usage:
- python main.py --index 0 --backend dshow --resolution 640x480
- Press 'q' to quit, 'm' to toggle mesh, 'f' to toggle rectangles.
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple
from camera_manager import CameraManager
from face_detector import FaceDetector
from filters.overlay_filter import OverlayFilter
from filters.filter_manager import FilterManager
from filters.model_3d_filter import Model3DFilter
import argparse
import os
try:
    from face_mesh import FaceMeshDetector  # type: ignore
except Exception:
    FaceMeshDetector = None  # type: ignore
import cv2  # type: ignore


@dataclass
class AppConfig:
    """Configuración de la aplicación de filtros AR.
    
    Attributes:
        camera_index: Índice de la cámara (0, 1, 2, ...)
        backend: Backend de OpenCV ('auto', 'avfoundation', 'dshow', etc.)
        resolution: Tupla (ancho, alto) opcional para resolución de cámara
        mustache_path: Ruta al PNG del bigote
        mustache_scale: Factor de escala para el bigote (0.0-2.0)
    """
    camera_index: int = 0
    backend: Optional[str] = "auto"
    resolution: Optional[Tuple[int, int]] = None
    mustache_path: str = "bigite.png"
    mustache_scale: float = 0.8


@dataclass
class AppState:
    """Estado actual de la aplicación durante la ejecución.
    
    Attributes:
        show_mesh: Mostrar malla facial completa (468 landmarks)
        show_boxes: Mostrar rectángulos de detección facial
        show_mustache: Mostrar filtro de bigote
        running: Si la aplicación está ejecutándose
    """
    show_mesh: bool = False
    show_boxes: bool = True
    show_mustache: bool = True
    running: bool = True


def main() -> None:
    # CLI options
    parser = argparse.ArgumentParser(description="filtros-ar preview")
    parser.add_argument("--index", "-i", type=int, default=0, help="Índice de cámara (0,1,2...)")
    parser.add_argument("--backend", type=str, default="auto", choices=["auto", "default", "dshow", "msmf", "avfoundation"],
                        help=(
                            "Backend de cámara: en Windows 'dshow'/'msmf'; en macOS 'avfoundation'. "
                            "'auto' intentará el mejor backend para la plataforma"
                        ))
    parser.add_argument("--resolution", "-r", type=str, default=None, help="WxH, ej: 1280x720 o 640x480")
    args = parser.parse_args()

    resolution = None
    if args.resolution:
        try:
            w, h = map(int, args.resolution.lower().split("x"))
            resolution = (w, h)
        except Exception:
            print("[filtros-ar] Formato de resolución inválido. Usa 1280x720 o 640x480.")

    backend = None if args.backend == "auto" else (args.backend if args.backend != "default" else None)

    cam = CameraManager(index=args.index, resolution=resolution, backend=backend)
    if not cam.open():
        print("[filtros-ar] No se pudo abrir la cámara. Asegúrate de tener opencv-python instalado.")
        return

    # ========== INICIALIZACIÓN DE COMPONENTES ==========
    detector = FaceDetector()
    mesh = FaceMeshDetector(max_faces=1) if FaceMeshDetector is not None else None
    
    # ========== GESTOR DE FILTROS MÚLTIPLES ==========
    filter_manager = FilterManager()
    
    # Cargar bigotes desde assets/ (Filtros 2D)
    mustache_files = [
        ("assets/mustache_black_classic.png", "Bigote Negro", 0.8),
        ("assets/mustache_brown_classic.png", "Bigote Café", 0.75),
        ("assets/mustache_red_thin.png", "Bigote Rojo", 0.6)
    ]
    
    active_filter_index = 0
    loaded_filters = []
    filter_types = []  # Para rastrear si es 2D o 3D
    
    for i, (path, name, scale) in enumerate(mustache_files):
        if os.path.exists(path):
            filter_obj = OverlayFilter(path, scale=scale)
            # Solo el primer filtro estará activo inicialmente
            is_enabled = (i == active_filter_index)
            filter_manager.add(name, filter_obj, enabled=is_enabled, z_order=1)
            loaded_filters.append(name)
            filter_types.append("2D")
            if is_enabled:
                print(f"✓ Filtro activo: {name} (2D)")
        else:
            print(f"⚠️  {path} no encontrado")
    
    # Cargar modelo 3D desde 3d.obj
    model_3d_path = "3d.obj"
    if os.path.exists(model_3d_path):
        model_filter = Model3DFilter(
            model_path=model_3d_path,
            color=(80, 170, 255),  # Color naranja-azulado
            alpha=0.7,
            face_mesh_detector=mesh
        )
        filter_manager.add("Modelo 3D", model_filter, enabled=False, z_order=2)
        loaded_filters.append("Modelo 3D")
        filter_types.append("3D")
        print(f"✓ Filtro 3D cargado: {model_3d_path}")
    else:
        print(f"⚠️  {model_3d_path} no encontrado")
    
    # Mostrar filtros cargados
    filter_manager.list_filters()
    
    # Estado de la aplicación usando dataclass
    state = AppState(
        show_mesh=False,
        show_boxes=True,
        show_mustache=True,
        running=True
    )

    print("[filtros-ar] Vista previa iniciada. Presiona 'q' para salir.")
    print("[filtros-ar] Controles:")
    print("  q = salir")
    print("  m = toggle malla facial (468 puntos)")
    print("  f = toggle rectángulos de detección")
    print("  b = toggle mostrar filtros")
    print("  n = cambiar al siguiente filtro (2D/3D)")
    print("  2 = activar solo filtros 2D (bigotes)")
    print("  3 = activar solo filtro 3D (modelo .obj)")
    print("  l = listar filtros cargados")

    try:
        while state.running:
            ret, frame = cam.read()
            if not ret or frame is None:
                print("[filtros-ar] No se pudo leer un frame de la cámara.")
                break

            faces = detector.detect(frame)

            if state.show_boxes:
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            hud_text = f"faces:{len(faces)}"
            
            # ========== DETECCIÓN DE PUNTOS FACIALES (LANDMARKS) ==========
            # MediaPipe detecta 468 puntos en la cara (ojos, nariz, boca, etc.)
            if mesh is not None and mesh.available() and (state.show_mesh or state.show_mustache):
                face_pts = mesh.detect(frame)  # Retorna lista de caras, cada una con 468 puntos (x,y)
                
                # Dibujar todos los puntos faciales si está activado
                if state.show_mesh:
                    mesh.draw(frame, face_pts)
                
                # ========== APLICAR TODOS LOS FILTROS ACTIVOS ==========
                if state.show_mustache and face_pts and filter_manager.get_active_count() > 0:
                    # Landmarks útiles: 13 (labio superior centro), 61 y 291 (comisuras)
                    upper_lip_idx = 2  # Punto justo debajo de la nariz, sobre el labio
                    
                    # Verificar que el rostro tiene suficientes landmarks
                    if 0 <= upper_lip_idx < len(face_pts[0]):
                        # Obtener coordenadas (x, y) en píxeles del labio superior
                        mx, my = face_pts[0][upper_lip_idx]
                        
                        # Calcular ancho del bigote basado en distancia entre comisuras de la boca
                        # Landmarks 61 (izquierda) y 291 (derecha) son las comisuras
                        if len(face_pts[0]) > 291:
                            left_corner = face_pts[0][61]
                            right_corner = face_pts[0][291]
                            mouth_width = abs(right_corner[0] - left_corner[0])
                        else:
                            mouth_width = 100  # Ancho por defecto
                        
                        # OverlayFilter espera una lista de detecciones en formato (x, y, w, h)
                        # donde x,y = esquina superior izquierda, w,h = ancho y alto
                        filter_width = int(mouth_width * 1.3)
                        filter_height = int(filter_width * 0.4)
                        
                        # Calcular esquina superior izquierda para centrar el filtro
                        x_top_left = mx - filter_width // 2
                        y_top_left = my - filter_height // 2
                        
                        # Crear pseudo-detección: (x, y, ancho, alto)
                        pseudo_detection = [(x_top_left, y_top_left, filter_width, filter_height)]
                        
                        # ========== APLICAR TODOS LOS FILTROS CON FilterManager ==========
                        # Aplica bigote (z=1) y lentes (z=2) en orden sobre el mismo frame
                        frame = filter_manager.apply(frame, pseudo_detection)
                hud_text = f"faces:{len(face_pts)} landmarks:{len(face_pts[0]) if face_pts else 0}"
            cv2.putText(frame, hud_text, (10, 24), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow("filtros-ar", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                state.running = False
                print("\n👋 Cerrando aplicación...")
            elif key == ord('m'):
                state.show_mesh = not state.show_mesh
                print(f"Malla facial: {'ON ✓' if state.show_mesh else 'OFF ✗'}")
            elif key == ord('f'):
                state.show_boxes = not state.show_boxes
                print(f"Rectángulos: {'ON ✓' if state.show_boxes else 'OFF ✗'}")
            elif key == ord('b'):
                # Toggle mostrar/ocultar todos los filtros
                state.show_mustache = not state.show_mustache
                print(f"Filtros: {'ON ✓' if state.show_mustache else 'OFF ✗'}")
            elif key == ord('n'):
                # Cambiar al siguiente filtro
                if loaded_filters:
                    # Desactivar filtro actual
                    filter_manager.toggle(loaded_filters[active_filter_index])
                    # Avanzar al siguiente
                    active_filter_index = (active_filter_index + 1) % len(loaded_filters)
                    # Activar nuevo filtro
                    filter_manager.toggle(loaded_filters[active_filter_index])
                    filter_type = filter_types[active_filter_index]
                    print(f"🎭 Filtro cambiado a: {loaded_filters[active_filter_index]} ({filter_type})")
            elif key == ord('2'):
                # Activar solo filtros 2D (bigotes)
                print("\n📸 Cambiando a filtros 2D (bigotes)...")
                for i, name in enumerate(loaded_filters):
                    filter_item = filter_manager.get_filter_by_name(name)
                    if filter_item:
                        if filter_types[i] == "2D":
                            if not filter_item.enabled:
                                filter_manager.toggle(name)
                            active_filter_index = i
                            print(f"✓ Activado: {name}")
                        else:
                            if filter_item.enabled:
                                filter_manager.toggle(name)
                            print(f"✗ Desactivado: {name}")
            elif key == ord('3'):
                # Activar solo filtro 3D
                print("\n🎲 Cambiando a filtro 3D (modelo .obj)...")
                for i, name in enumerate(loaded_filters):
                    filter_item = filter_manager.get_filter_by_name(name)
                    if filter_item:
                        if filter_types[i] == "3D":
                            if not filter_item.enabled:
                                filter_manager.toggle(name)
                            active_filter_index = i
                            print(f"✓ Activado: {name}")
                        else:
                            if filter_item.enabled:
                                filter_manager.toggle(name)
                            print(f"✗ Desactivado: {name}")
            elif key == ord('l'):
                # Listar todos los filtros cargados
                print("\n" + "="*50)
                filter_manager.list_filters()
                print("="*50)
    finally:
        cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
