#!/usr/bin/env python3
"""
Demo: show face mesh landmarks over live camera.

Usage:
  python face_mesh_demo.py --index 0
  python face_mesh_demo.py --list-cameras

Press 'q' to quit.
"""
from __future__ import annotations
import argparse
from typing import List

from camera_manager import CameraManager
from face_mesh import FaceMeshDetector

try:
    from list_cameras import listar_camaras  # type: ignore
except Exception:
    listar_camaras = None  # type: ignore

try:
    import cv2  # type: ignore
except ImportError:
    cv2 = None  # type: ignore


def parse_args():
    p = argparse.ArgumentParser(description="Face mesh demo")
    p.add_argument("--index", "-i", type=int, default=None, help="Camera index to open")
    p.add_argument("--list-cameras", action="store_true", help="List cameras and exit")
    p.add_argument("--resolution", "-r", type=str, default=None, help="WxH, e.g. 1280x720")
    p.add_argument("--backend", type=str, default="auto", choices=["auto", "default", "dshow", "msmf", "avfoundation"],
                   help=(
                       "Camera backend: Windows uses 'dshow'/'msmf'; macOS uses 'avfoundation'. "
                       "'auto' tries best backend for the platform"
                   ))
    return p.parse_args()


def main():
    args = parse_args()

    if args.list_cameras:
        if listar_camaras is None:
            print("No camera lister available; run list_cameras.py")
            return
        cams = listar_camaras()
        print("Cámaras detectadas:", cams)
        return

    resolution = None
    if args.resolution:
        try:
            w, h = map(int, args.resolution.lower().split("x"))
            resolution = (w, h)
        except Exception:
            print("Formato resolución inválido. Usa 1280x720, 640x480, etc.")

    candidate = [args.index] if args.index is not None else [0, 1, 2]

    backend = None if args.backend == "auto" else (args.backend if args.backend != "default" else None)

    cam = None
    for idx in candidate:
        cm = CameraManager(index=idx, resolution=resolution, backend=backend)
        if cm.open():
            cam = cm
            print(f"Cámara abierta en índice {idx}")
            break
    if cam is None:
        print("No se pudo abrir ninguna cámara. En WSL puede no haber acceso a webcam.")
        return

    mesh = FaceMeshDetector(max_faces=1)
    if not mesh.available():
        print("[face_mesh_demo] MediaPipe no está disponible o no se inicializó.\n"
              "Asegúrate de haber instalado 'mediapipe' en este entorno (pip install mediapipe).")

    print("Demo corriendo. Presiona 'q' para salir.")
    while True:
        ret, frame = cam.read()
        if not ret or frame is None:
            print("Frame inválido; saliendo.")
            break
        faces: List[List[tuple[int,int]]] = mesh.detect(frame)
        mesh.draw(frame, faces)
        # Overlay simple HUD
        if cv2 is not None:
            text = f"faces: {len(faces)}"
            if faces:
                text += f" | landmarks: {len(faces[0])}"
            else:
                text += " | no landmarks"
            cv2.putText(frame, text, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)
        if cv2 is not None:
            cv2.imshow("Face Mesh", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        else:
            # No OpenCV GUI available; break to avoid infinite loop
            break

    cam.release()
    if cv2 is not None:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
