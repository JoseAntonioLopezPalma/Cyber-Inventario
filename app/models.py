"""
Modelos SQLAlchemy para la gestión de inventario de hardware.
Tabla principal: HardwareItem con validaciones y restricciones.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from datetime import datetime, UTC
import enum
from app.database import Base


class HardwareCategory(str, enum.Enum):
    """Categorías permitidas de hardware (basadas en datos CSV)."""
    MICROPROCESADORES = "Microprocesadores"
    REFRIGERADORES_CPU = "Refrigeradores CPU"
    TARJETAS_GRAFICAS = "Tarjetas Gráficas"
    MEMORIA_RAM = "Memoria RAM"
    PLACAS_BASE = "Placas Base"
    GABINETES = "Gabinetes"
    DISCOS_DUROS = "Discos Duros"
    UNIDADES_SSD = "Unidades SSD"
    MONITORES = "Monitores"
    FUENTES_POWER = "Fuentes Power"


class HardwareItem(Base):
    """
    Modelo principal para ítems de hardware.
    
    Atributos:
        id: Identificador único (PK)
        nombre: Nombre del producto
        categoria: Categoría del hardware (enum)
        stock: Cantidad disponible (>= 0)
        precio: Precio unitario (>= 0)
        fecha_entrada: Fecha de ingreso al inventario
    """
    __tablename__ = "hardware_items"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    categoria = Column(Enum(HardwareCategory), nullable=False, index=True)
    stock = Column(Integer, nullable=False, default=0)
    precio = Column(Float, nullable=False)
    fecha_entrada = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))

    def __repr__(self):
        return (
            f"<HardwareItem(id={self.id}, nombre='{self.nombre}', "
            f"categoria='{self.categoria}', stock={self.stock}, "
            f"precio=${self.precio})>"
        )
