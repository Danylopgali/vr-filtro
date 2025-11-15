"""Utilidad para listar cámaras disponibles y abrir una.

Uso:
    python list_cameras.py

- Intenta abrir índices desde 0 hasta max_index-1.
- Muestra las cámaras detectadas.
- Permite elegir una y visualizar el feed.
- Presiona ESC para salir.

Nota: Si usas aplicaciones como 'Camo' o 'DroidCam', aparecerán como
una cámara adicional (normalmente con un índice > 0).
"""
from __future__ import annotations

try:
    import cv2  # type: ignore
except ImportError:
    cv2 = None  # type: ignore


def listar_camaras(max_index: int = 10):
    """Devuelve una lista de índices de cámaras disponibles.

    En Windows intenta abrir con backends alternativos (DirectShow, MediaFoundation)
    para soportar cámaras virtuales como Camo.
    """
    if cv2 is None:
        print("OpenCV no está instalado. Instala con: pip install opencv-python")
        return []
    camaras_disponibles = []
    import platform
    system = platform.system().lower()

    backend_candidates = [None]
    if system.startswith("win"):
        if hasattr(cv2, "CAP_DSHOW"):
            backend_candidates.insert(0, int(cv2.CAP_DSHOW))
        if hasattr(cv2, "CAP_MSMF"):
            backend_candidates.insert(1, int(cv2.CAP_MSMF))
    elif system.startswith("darwin"):
        if hasattr(cv2, "CAP_AVFOUNDATION"):
            backend_candidates.insert(0, int(cv2.CAP_AVFOUNDATION))

    for i in range(max_index):
        for b in backend_candidates:
            cap = cv2.VideoCapture(i, b) if (b is not None) else cv2.VideoCapture(i)
            if cap is not None and cap.isOpened():
                camaras_disponibles.append(i)
                cap.release()
                break
            if cap is not None:
                cap.release()
    return sorted(set(camaras_disponibles))


def elegir_indice(camaras):
    while True:
        valor = input(f"Elige cámara {camaras} (ENTER para la primera): ").strip()
        if valor == "" and camaras:
            return camaras[0]
        try:
            idx = int(valor)
        except ValueError:
            print("Ingresa un número válido.")
            continue
        if idx in camaras:
            return idx
        print("Índice fuera de la lista.")


def ver_feed(indice: int):
    cap = cv2.VideoCapture(indice)
    if not cap.isOpened():
        print(f"No se pudo abrir la cámara {indice}.")
        return
    print("Mostrando feed. Presiona ESC para salir.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame no válido, saliendo.")
            break
        cv2.imshow(f"Cámara {indice}", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
    cap.release()
    cv2.destroyAllWindows()


def main():
    camaras = listar_camaras()
    print("Cámaras detectadas:", camaras)
    if not camaras:
        print("No se detectaron cámaras.")
        return
    indice = elegir_indice(camaras)
    ver_feed(indice)


if __name__ == "__main__":
    main()
