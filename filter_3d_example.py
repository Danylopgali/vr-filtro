"""Ejemplo de uso del filtro 3D con pose facial.

Este script demuestra cómo usar Model3DFilter para renderizar
un modelo 3D sobre el rostro usando solvePnP.
"""
from filters.model_3d_filter import Model3DFilter
from face_mesh import FaceMeshDetector

# Ejemplo 1: Filtro 3D básico con ejes de coordenadas (sin modelo real)
print("=" * 60)
print("EJEMPLO 1: Filtro 3D con seguimiento de pose")
print("=" * 60)

# Crear detector de face mesh (necesario para los landmarks)
face_mesh = FaceMeshDetector()

# Crear filtro 3D (por ahora solo dibuja ejes XYZ)
filter_3d = Model3DFilter(
    model_path="assets/mascara.glb",  # Ruta al modelo 3D
    color=(255, 170, 80),              # Color BGR (azul-naranja)
    alpha=0.6,                         # 60% de opacidad
    face_mesh_detector=face_mesh       # Pasar detector para landmarks
)

print(f"\n✓ Filtro creado: {filter_3d.name}")
print(f"  - Modelo: {filter_3d.model_path}")
print(f"  - Color BGR: {filter_3d.color}")
print(f"  - Opacidad: {filter_3d.alpha}")
print(f"  - Puntos MediaPipe: {filter_3d.mp_idxs}")

# Mostrar coordenadas 3D canónicas
print(f"\n📐 Coordenadas 3D canónicas del rostro (CANON_FACE_3D):")
print(f"  Índice MP | Punto          | Coordenadas (X, Y, Z)")
print(f"  ----------|----------------|----------------------")
point_names = [
    "Ojo izquierdo",
    "Ojo derecho",
    "Punta nariz",
    "Comisura izq",
    "Comisura der",
    "Mentón"
]
for i, (idx, name) in enumerate(zip(filter_3d.mp_idxs, point_names)):
    coords = filter_3d.canon_face_3d[i]
    print(f"  {idx:3d}       | {name:14} | ({coords[0]:5.1f}, {coords[1]:5.1f}, {coords[2]:5.1f})")


# Ejemplo 2: Parámetros de configuración
print("\n" + "=" * 60)
print("EJEMPLO 2: Configuración de parámetros")
print("=" * 60)

print("\nPARAMETROS PRINCIPALES:")
print("  • MODEL_PATH: ruta del modelo (mascara.glb o .obj)")
print("  • COLOR: color BGR con el que pintamos el sólido")
print("    Ejemplos: (255,170,80), (0,255,0), (255,0,0)")
print("  • ALPHA: opacidad del overlay")
print("    1.0 = opaco; 0.6 = más transparente; 0.3 = muy transparente")

print("\nPUNTOS FACIALES (MP_IDXS):")
print("  [33, 263, 1, 61, 291, 199]")
print("  • 33:  Ojo izquierdo (outer corner)")
print("  • 263: Ojo derecho (outer corner)")
print("  • 1:   Punta de la nariz")
print("  • 61:  Comisura izquierda de la boca")
print("  • 291: Comisura derecha de la boca")
print("  • 199: Mentón")

print("\nCANON_FACE_3D:")
print("  Coordenadas 3D canónicas aproximadas (en 'metros relativos')")
print("  para esos 6 puntos. Se usan como 'modelo 3D' del rostro para")
print("  que solvePnP pueda calcular la pose real (rotación y translación).")


# Ejemplo 3: Integración en main.py
print("\n" + "=" * 60)
print("EJEMPLO 3: Integración en main.py")
print("=" * 60)

print("\nPara usar el filtro 3D en tu aplicación, agrega en main.py:")
print("""
# Importar el filtro
from filters.model_3d_filter import Model3DFilter

# Crear instancia con el face_mesh_detector
filter_3d = Model3DFilter(
    model_path="assets/mascara.glb",
    color=(255, 170, 80),
    alpha=0.6,
    face_mesh_detector=face_mesh_detector  # Pasar la instancia existente
)

# Agregar al filter_manager
filter_manager.add(
    name="Máscara 3D",
    filter_obj=filter_3d,
    enabled=True,
    z_order=2  # Renderizar encima de otros filtros
)
""")

print("\n💡 PRÓXIMOS PASOS:")
print("  1. Agregar carga real de modelos .glb (con trimesh o pygltflib)")
print("  2. Implementar renderizado de mallas 3D en _render_3d_model()")
print("  3. Optimizar rendimiento con caching de proyecciones")
print("  4. Agregar soporte para texturas del modelo")
print("  5. Implementar iluminación básica (shading)")

print("\n✓ Configuración completa")
