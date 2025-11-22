#!/usr/bin/env python3
"""
Genera una imagen PNG simple de un punto rojo con transparencia.
Salida: assets/red_dot.png
"""
from PIL import Image, ImageDraw

# Crear imagen 200x200 con canal alpha
size = 200
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Dibujar círculo rojo en el centro
center = size // 2
radius = 200
draw.ellipse(
    [center - radius, center - radius, center + radius, center + radius],
    fill=(255, 0, 0, 255),
    outline=None
)

img.save('assets/red_dot.png')
print("[generate_red_dot] assets/red_dot.png creado.")
