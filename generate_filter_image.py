#!/usr/bin/env python3
"""
Genera una imagen PNG simple de gafas de sol para usar con OverlayFilter.
"""
import numpy as np
try:
    import cv2
except ImportError:
    print("Instala opencv-python primero: pip install opencv-python")
    exit(1)

# Crear imagen 400x200 con transparencia (BGRA)
width, height = 400, 200
img = np.zeros((height, width, 4), dtype=np.uint8)

# Dibujar dos círculos oscuros (lentes) con borde
center_y = height // 2
left_x = width // 3
right_x = 2 * width // 3
radius = 60

# Lentes oscuros
cv2.circle(img, (left_x, center_y), radius, (30, 30, 30, 255), -1)
cv2.circle(img, (right_x, center_y), radius, (30, 30, 30, 255), -1)

# Bordes blancos
cv2.circle(img, (left_x, center_y), radius, (255, 255, 255, 255), 4)
cv2.circle(img, (right_x, center_y), radius, (255, 255, 255, 255), 4)

# Puente entre los lentes
cv2.line(img, (left_x + radius, center_y), (right_x - radius, center_y), 
         (255, 255, 255, 255), 4)

# Patillas (brazos)
cv2.line(img, (left_x - radius, center_y), (10, center_y - 10), 
         (255, 255, 255, 255), 4)
cv2.line(img, (right_x + radius, center_y), (width - 10, center_y - 10), 
         (255, 255, 255, 255), 4)

# Guardar
output_path = "assets/sunglasses.png"
cv2.imwrite(output_path, img)
print(f"✓ Imagen generada: {output_path}")
