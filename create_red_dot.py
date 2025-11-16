#!/usr/bin/env python3
"""Genera punto rojo PNG para overlay en nariz."""
from PIL import Image, ImageDraw

# Imagen 100x100 RGBA (transparente)
size = 100
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Círculo rojo en el centro
center = size // 2
radius = 30
draw.ellipse(
    [center - radius, center - radius, center + radius, center + radius],
    fill=(255, 0, 0, 255),  # Rojo opaco
    outline=(200, 0, 0, 255),
    width=2
)

img.save('assets/red_dot.png')
print("✓ assets/red_dot.png creado")
