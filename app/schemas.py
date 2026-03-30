"""
Esquemas Pydantic para validación de datos.
Garantiza que las entradas cumplan con las reglas de negocio.
Compatible con Pydantic v1.
"""

from pydantic import BaseModel, Field, validator
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
    stock: int = Field(..., ge=0)
    precio: float = Field(..., gt=0)

    @validator("nombre")
    def validar_nombre_no_vacio(cls, v):
        """Valida que el nombre no sea solo espacios en blanco."""
        if not v or v.strip() == "":
            raise ValueError("El nombre no puede estar vacío o contener solo espacios")
        return v.strip()

    @validator("precio")
    def validar_precio_razonable(cls, v):
        """Valida que el precio sea razonablemente alto y redondea a 2 decimales."""
        if v > 100_000:
            raise ValueError("El precio es ilógicamente alto (máximo $100,000)")
        # Redondear a 2 decimales
        return round(v, 2)

    class Config:
        use_enum_values = True


class HardwareItemCreate(HardwareItemBase):
    """Esquema para creación de ítems (POST)."""
    pass


class HardwareItemUpdate(BaseModel):
    """Esquema para actualización de ítems (PUT/PATCH)."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    categoria: Optional[HardwareCategoryEnum] = None
    stock: Optional[int] = Field(None, ge=0)
    precio: Optional[float] = Field(None, gt=0)


class HardwareItemResponse(HardwareItemBase):
    """Esquema para respuestas (GET)."""
    id: int
    fecha_entrada: datetime

    class Config:
        orm_mode = True
        use_enum_values = True


class HardwareItemListResponse(BaseModel):
    """Respuesta para listados."""
    total: int = Field(..., ge=0)
    items: List[HardwareItemResponse]
    precio_total_inventario: float = Field(..., ge=0)

    class Config:
        orm_mode = True


class ErrorResponse(BaseModel):
    """Esquema estándar para errores."""
    detail: str
    status_code: int
