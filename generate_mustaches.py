#!/usr/bin/env python3
"""
Genera varios mostachos PNG de diferentes estilos para probar el sistema de múltiples assets.
"""
from PIL import Image, ImageDraw
import os

# Crear directorio assets si no existe
os.makedirs("assets", exist_ok=True)

def create_mustache(filename, color, style="classic"):
    """Crea un mostacho PNG con transparencia.
    
    Args:
        filename: Nombre del archivo a guardar
        color: Tupla RGB (ej: (0, 0, 0) para negro)
        style: Estilo del mostacho ('classic', 'thin', 'thick')
    """
    # Tamaño de la imagen
    width, height = 300, 150
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center_x = width // 2
    center_y = height // 2
    
    if style == "classic":
        # Mostacho clásico grueso
        # Lado izquierdo
        draw.ellipse([20, center_y - 30, center_x - 10, center_y + 30], 
                     fill=color + (255,), outline=color + (255,))
        # Lado derecho
        draw.ellipse([center_x + 10, center_y - 30, width - 20, center_y + 30], 
                     fill=color + (255,), outline=color + (255,))
        # Centro (puente)
        draw.rectangle([center_x - 15, center_y - 15, center_x + 15, center_y + 20], 
                      fill=color + (255,))
        
    elif style == "thin":
        # Mostacho fino tipo Salvador Dalí
        # Líneas finas curvas
        draw.ellipse([30, center_y - 10, center_x - 15, center_y + 10], 
                     fill=color + (255,))
        draw.ellipse([center_x + 15, center_y - 10, width - 30, center_y + 10], 
                     fill=color + (255,))
        # Puntas hacia arriba
        draw.ellipse([10, center_y - 40, 60, center_y - 5], 
                     fill=color + (255,))
        draw.ellipse([width - 60, center_y - 40, width - 10, center_y - 5], 
                     fill=color + (255,))
        
    elif style == "thick":
        # Mostacho muy grueso estilo "handlebar"
        draw.ellipse([10, center_y - 40, center_x - 5, center_y + 35], 
                     fill=color + (255,))
        draw.ellipse([center_x + 5, center_y - 40, width - 10, center_y + 35], 
                     fill=color + (255,))
        # Puente grueso
        draw.rectangle([center_x - 20, center_y - 20, center_x + 20, center_y + 25], 
                      fill=color + (255,))
    
    img.save(f"assets/{filename}")
    print(f"✓ {filename} creado ({style}, color RGB{color})")

# Generar varios mostachos
print("Generando mostachos...")
create_mustache("mustache_black_classic.png", (0, 0, 0), "classic")
create_mustache("mustache_brown_classic.png", (101, 67, 33), "classic")
create_mustache("mustache_red_thin.png", (200, 0, 0), "thin")
create_mustache("mustache_white_thick.png", (255, 255, 255), "thick")
create_mustache("mustache_blue_classic.png", (0, 100, 200), "classic")

print(f"\n✓ Generados 5 mostachos en assets/")
print("Uso en main.py:")
print('  nose_filter = OverlayFilter(["assets/mustache_black_classic.png", "assets/mustache_brown_classic.png", ...], scale=0.5)')
print("  Presiona 'c' para cambiar entre mostachos")
