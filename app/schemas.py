"""
Esquemas Pydantic para validación de datos.
Garantiza que las entradas cumplan con las reglas de negocio.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class HardwareCategoryEnum(str, Enum):
    """Enumeración de categorías para esquemas (basadas en datos CSV)."""
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


class HardwareItemBase(BaseModel):
    """Esquema base con validaciones comunes."""
    nombre: str = Field(..., min_length=1, max_length=255)
    categoria: HardwareCategoryEnum
    stock: int = Field(..., ge=0)  # >= 0
    precio: float = Field(..., gt=0)  # > 0

    @field_validator("nombre")
    def nombre_no_vacio(cls, v):
        """Valida que el nombre no sea solo espacios."""
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío o contener solo espacios")
        return v.strip()

    @field_validator("precio")
    def precio_valido(cls, v):
        """Valida que el precio sea positivo y razonable."""
        if v < 0:
            raise ValueError("El precio no puede ser negativo")
        if v > 1_000_000:
            raise ValueError("El precio parece ser demasiado alto (> $1M)")
        return round(v, 2)

    @field_validator("stock")
    def stock_valido(cls, v):
        """Valida que el stock no sea negativo."""
        if v < 0:
            raise ValueError("El stock no puede ser negativo")
        return v


class HardwareItemCreate(HardwareItemBase):
    """Esquema para creación de ítems (POST)."""
    pass


class HardwareItemUpdate(BaseModel):
    """Esquema para actualización de ítems (PUT/PATCH)."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    categoria: Optional[HardwareCategoryEnum] = None
    stock: Optional[int] = Field(None, ge=0)
    precio: Optional[float] = Field(None, gt=0)

    @field_validator("nombre")
    def nombre_no_vacio(cls, v):
        """Valida que el nombre no sea solo espacios."""
        if v is not None and not v.strip():
            raise ValueError("El nombre no puede estar vacío o contener solo espacios")
        return v.strip() if v else v

    @field_validator("precio")
    def precio_valido(cls, v):
        """Valida que el precio sea positivo."""
        if v is not None:
            if v < 0:
                raise ValueError("El precio no puede ser negativo")
            if v > 1_000_000:
                raise ValueError("El precio parece ser demasiado alto (> $1M)")
            return round(v, 2)
        return v

    @field_validator("stock")
    def stock_valido(cls, v):
        """Valida que el stock no sea negativo."""
        if v is not None and v < 0:
            raise ValueError("El stock no puede ser negativo")
        return v


class HardwareItemResponse(HardwareItemBase):
    """Esquema para respuestas (GET)."""
    id: int
    fecha_entrada: datetime

    model_config = ConfigDict(
        from_attributes=True,  # Permite mapeo desde modelos ORM
        serialize_as_any=True,  # Serializar enums como sus valores
    )


class HardwareItemListResponse(BaseModel):
    """Respuesta para listados."""
    total: int = Field(..., ge=0)
    items: List[HardwareItemResponse]
    precio_total_inventario: float = Field(..., ge=0)


class ErrorResponse(BaseModel):
    """Esquema estándar para errores."""
    detail: str
    status_code: int
