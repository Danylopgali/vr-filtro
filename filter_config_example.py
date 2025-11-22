#!/usr/bin/env python3
"""
Ejemplo de uso de @dataclass y List para gestionar múltiples filtros.
Demuestra cómo usar dataclasses para configurar filtros de forma clara.
"""
from dataclasses import dataclass, field
from typing import List, Optional
import os

@dataclass
class FilterConfig:
    """Configuración de un filtro individual.
    
    Attributes:
        name: Nombre descriptivo del filtro
        path: Ruta al archivo PNG
        scale: Factor de escala (0.1 - 2.0)
        offset_x: Desplazamiento horizontal en píxeles
        offset_y: Desplazamiento vertical en píxeles
        enabled: Si el filtro está activo
    """
    name: str
    path: str
    scale: float = 1.0
    offset_x: int = 0
    offset_y: int = 0
    enabled: bool = True
    
    def __post_init__(self):
        """Validación después de crear la instancia."""
        if not os.path.exists(self.path):
            print(f"⚠️ ADVERTENCIA: {self.path} no existe")
        if not (0.1 <= self.scale <= 2.0):
            raise ValueError(f"scale debe estar entre 0.1 y 2.0, recibido: {self.scale}")


@dataclass
class FilterCollection:
    """Colección de filtros con gestión automática.
    
    Attributes:
        filters: Lista de configuraciones de filtros
        active_index: Índice del filtro actualmente activo
    """
    filters: List[FilterConfig] = field(default_factory=list)
    active_index: int = 0
    
    def add_filter(self, config: FilterConfig) -> None:
        """Agrega un filtro a la colección."""
        self.filters.append(config)
        print(f"✓ Filtro '{config.name}' agregado ({config.path})")
    
    def next_filter(self) -> Optional[FilterConfig]:
        """Avanza al siguiente filtro (circular)."""
        if not self.filters:
            return None
        self.active_index = (self.active_index + 1) % len(self.filters)
        current = self.filters[self.active_index]
        print(f"🎭 Cambiando a: {current.name} ({self.active_index + 1}/{len(self.filters)})")
        return current
    
    def get_active(self) -> Optional[FilterConfig]:
        """Retorna el filtro actualmente activo."""
        if not self.filters:
            return None
        return self.filters[self.active_index]
    
    def list_filters(self) -> None:
        """Muestra todos los filtros disponibles."""
        print(f"\n📋 Filtros disponibles ({len(self.filters)}):")
        for i, f in enumerate(self.filters):
            active = "✓" if i == self.active_index else " "
            status = "ON" if f.enabled else "OFF"
            print(f"  [{active}] {i+1}. {f.name} (scale={f.scale}, {status})")


# Ejemplo de uso
if __name__ == "__main__":
    # Crear colección de filtros usando dataclass
    collection = FilterCollection()
    
    # Agregar varios bigotes con configuración usando @dataclass
    collection.add_filter(FilterConfig(
        name="Bigote Negro Clásico",
        path="assets/mustache_black_classic.png",
        scale=0.8
    ))
    
    collection.add_filter(FilterConfig(
        name="Bigote Café",
        path="assets/mustache_brown_classic.png",
        scale=0.75,
        offset_y=-5
    ))
    
    collection.add_filter(FilterConfig(
        name="Bigote Rojo Fino",
        path="assets/mustache_red_thin.png",
        scale=0.6
    ))
    
    # Listar filtros
    collection.list_filters()
    
    # Cambiar entre filtros
    print("\n🔄 Probando cambio de filtros:")
    for _ in range(3):
        current = collection.next_filter()
        if current:
            print(f"   → Activo: {current.name} en {current.path}")
