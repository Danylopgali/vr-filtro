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
from camera_manager import CameraManager
from face_detector import FaceDetector
import argparse
try:
    from face_mesh import FaceMeshDetector  # type: ignore
except Exception:
    FaceMeshDetector = None  # type: ignore
import cv2  # type: ignore


def main() -> None:
    # CLI options
    parser = argparse.ArgumentParser(description="filtros-ar preview")
    parser.add_argument("--index", "-i", type=int, default=0, help="Índice de cámara (0,1,2...)")
    parser.add_argument("--backend", type=str, default="auto", choices=["auto", "default", "dshow", "msmf"],
                        help="Backend de cámara en Windows: auto intenta dshow->msmf->default")
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

    detector = FaceDetector()
    mesh = FaceMeshDetector(max_faces=1) if FaceMeshDetector is not None else None

    print("[filtros-ar] Vista previa iniciada. Presiona 'q' para salir.")
    print("[filtros-ar] Controles: q = salir | m = toggle malla | f = toggle rectángulos | n = nariz")

    show_mesh = False
    show_boxes = True
    show_nose = False

    try:
        while True:
            ret, frame = cam.read()
            if not ret or frame is None:
                print("[filtros-ar] No se pudo leer un frame de la cámara.")
                break

            faces = detector.detect(frame)

            if show_boxes:
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            hud_text = f"faces:{len(faces)}"
            if mesh is not None and mesh.available() and (show_mesh or show_nose):
                face_pts = mesh.detect(frame)
                if show_mesh:
                    mesh.draw(frame, face_pts)
                # Nose circle: use landmark index 1 (tip of nose in MediaPipe)
                if show_nose and face_pts:
                    nose_idx = 1
                    if 0 <= nose_idx < len(face_pts[0]):
                        nx, ny = face_pts[0][nose_idx]
                        cv2.circle(frame, (nx, ny), 8, (0, 0, 255), -1)
                hud_text = f"faces:{len(face_pts)} landmarks:{len(face_pts[0]) if face_pts else 0}"
            cv2.putText(frame, hud_text, (10, 24), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow("filtros-ar", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('m'):
                show_mesh = not show_mesh
            elif key == ord('f'):
                show_boxes = not show_boxes
            elif key == ord('n'):
                show_nose = not show_nose
    finally:
        cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
