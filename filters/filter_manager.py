"""
Gestor de filtros múltiples para aplicación AR.

Permite cargar, organizar y aplicar múltiples filtros (bigote, lentes, etc.)
sobre un mismo frame, con control de orden (Z-order) y activación individual.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Any
import os

try:
    import cv2  # type: ignore
except ImportError:
    cv2 = None


@dataclass
class FilterItem:
    """Representa un filtro individual con su configuración.
    
    Attributes:
        name: Identificador único del filtro (ej: "bigote", "lentes")
        filter_obj: Instancia de OverlayFilter con el PNG cargado
        enabled: Si el filtro está activo (se aplica al frame)
        z_order: Orden de dibujado (menor = se dibuja primero/abajo)
    """
    name: str
    filter_obj: Any  # OverlayFilter instance
    enabled: bool = True
    z_order: int = 0


class FilterManager:
    """Gestor central de múltiples filtros AR.
    
    Maneja una colección de filtros con sus estados individuales,
    permitiendo aplicarlos en orden sobre un frame de video.
    """
    
    def __init__(self):
        """Inicializa el gestor con una lista vacía de filtros."""
        self.filters: List[FilterItem] = []
    
    def add(self, name: str, filter_obj: Any, enabled: bool = True, z_order: int = 0) -> None:
        """Crea un FilterItem y lo agrega a la lista.
        
        Args:
            name: Identificador único del filtro
            filter_obj: Instancia de OverlayFilter con el PNG cargado
            enabled: Estado inicial del filtro (True = activo)
            z_order: Orden de renderizado (0=fondo, mayor=frente)
        
        Example:
            manager.add("bigote", OverlayFilter("bigote.png"), enabled=True, z_order=1)
            manager.add("lentes", OverlayFilter("lentes.png"), enabled=True, z_order=2)
        """
        # Verificar que no exista un filtro con el mismo nombre
        if self.get_filter_by_name(name):
            print(f"⚠️  Filtro '{name}' ya existe, reemplazando...")
            self.remove(name)
        
        item = FilterItem(
            name=name,
            filter_obj=filter_obj,
            enabled=enabled,
            z_order=z_order
        )
        self.filters.append(item)
        
        # Reordenar por z_order después de agregar
        self._sort_by_z_order()
        
        print(f"✓ Filtro '{name}' agregado (z_order={z_order}, {'ON' if enabled else 'OFF'})")
    
    def set_enabled(self, name: str, enabled: bool) -> bool:
        """Busca un filtro por nombre y lo enciende o apaga.
        
        Args:
            name: Nombre del filtro a modificar
            enabled: True para activar, False para desactivar
        
        Returns:
            True si se encontró y modificó el filtro, False si no existe
        
        Example:
            manager.set_enabled("bigote", False)  # Apaga el bigote
            manager.set_enabled("lentes", True)   # Enciende los lentes
        """
        filter_item = self.get_filter_by_name(name)
        if filter_item:
            filter_item.enabled = enabled
            status = "activado" if enabled else "desactivado"
            print(f"🔄 Filtro '{name}' {status}")
            return True
        else:
            print(f"❌ Filtro '{name}' no encontrado")
            return False
    
    def toggle(self, name: str) -> Optional[bool]:
        """Alterna el estado de un filtro (ON ↔ OFF).
        
        Args:
            name: Nombre del filtro
        
        Returns:
            Nuevo estado (True/False) o None si no existe
        """
        filter_item = self.get_filter_by_name(name)
        if filter_item:
            filter_item.enabled = not filter_item.enabled
            return filter_item.enabled
        return None
    
    def apply(self, frame: Any, detections: List[Any]) -> Any:
        """Aplica todos los filtros activos en orden sobre el mismo frame.
        
        Los filtros se aplican según su z_order (menor primero).
        Solo se aplican filtros con enabled=True.
        
        Args:
            frame: Frame de video BGR (numpy array)
            detections: Lista de detecciones (x, y, w, h) para posicionar filtros
        
        Returns:
            Frame modificado con todos los filtros aplicados
        
        Example:
            # Aplicar bigote (z=1) y luego lentes (z=2)
            frame = manager.apply(frame, [(x, y, w, h)])
        """
        for filter_item in self.filters:
            if filter_item.enabled and filter_item.filter_obj:
                # Aplicar el filtro modificando el frame in-place
                frame = filter_item.filter_obj.apply(frame, detections)
        
        return frame
    
    def move(self, name: str, new_z_order: int) -> bool:
        """Cambia el z_order de un filtro (controla qué se dibuja encima).
        
        Z-order menor = se dibuja primero (más atrás)
        Z-order mayor = se dibuja después (más adelante)
        
        Args:
            name: Nombre del filtro a mover
            new_z_order: Nuevo orden de renderizado
        
        Returns:
            True si se movió exitosamente, False si no existe
        
        Example:
            # Mover lentes por debajo del bigote
            manager.move("lentes", 0)  # Lentes atrás
            manager.move("bigote", 1)  # Bigote adelante
        """
        filter_item = self.get_filter_by_name(name)
        if filter_item:
            old_z = filter_item.z_order
            filter_item.z_order = new_z_order
            self._sort_by_z_order()
            print(f"↕️  Filtro '{name}' movido de z={old_z} a z={new_z_order}")
            return True
        else:
            print(f"❌ Filtro '{name}' no encontrado")
            return False
    
    def remove(self, name: str) -> bool:
        """Elimina un filtro de la lista.
        
        Args:
            name: Nombre del filtro a eliminar
        
        Returns:
            True si se eliminó, False si no existía
        """
        for i, item in enumerate(self.filters):
            if item.name == name:
                self.filters.pop(i)
                print(f"🗑️  Filtro '{name}' eliminado")
                return True
        return False
    
    def get_filter_by_name(self, name: str) -> Optional[FilterItem]:
        """Busca y retorna un FilterItem por su nombre.
        
        Args:
            name: Nombre del filtro a buscar
        
        Returns:
            FilterItem si existe, None si no se encuentra
        """
        for item in self.filters:
            if item.name == name:
                return item
        return None
    
    def list_filters(self) -> None:
        """Muestra todos los filtros cargados con su estado actual."""
        if not self.filters:
            print("📋 No hay filtros cargados")
            return
        
        print(f"\n📋 Filtros cargados ({len(self.filters)}):")
        for item in self.filters:
            status = "✓ ON " if item.enabled else "✗ OFF"
            print(f"  [{status}] {item.name} (z={item.z_order})")
    
    def _sort_by_z_order(self) -> None:
        """Ordena los filtros por z_order (menor a mayor)."""
        self.filters.sort(key=lambda x: x.z_order)
    
    def get_active_count(self) -> int:
        """Retorna cuántos filtros están actualmente activos."""
        return sum(1 for f in self.filters if f.enabled)


__all__ = ["FilterManager", "FilterItem"]
