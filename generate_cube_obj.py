#!/usr/bin/env python3
"""Genera un archivo .obj simple con un cubo 3D para usar como filtro."""

def generate_cube_obj(output_path: str = "assets/cube.obj"):
    """Genera un archivo .obj con un cubo centrado en el origen.
    
    Args:
        output_path: Ruta donde guardar el archivo .obj
    """
    cube_obj_content = """# Cubo simple para filtro 3D
# Vertices (8 esquinas del cubo)
v -0.5 -0.5 -0.5
v  0.5 -0.5 -0.5
v  0.5  0.5 -0.5
v -0.5  0.5 -0.5
v -0.5 -0.5  0.5
v  0.5 -0.5  0.5
v  0.5  0.5  0.5
v -0.5  0.5  0.5

# Caras (usando índices de vértices)
# Cara frontal
f 1 2 3 4
# Cara trasera
f 5 6 7 8
# Cara izquierda
f 1 5 8 4
# Cara derecha
f 2 6 7 3
# Cara superior
f 4 3 7 8
# Cara inferior
f 1 2 6 5
"""
    
    import os
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    with open(output_path, "w") as f:
        f.write(cube_obj_content)
    
    print(f"✓ Cubo 3D generado: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_cube_obj()
