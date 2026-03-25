#!/usr/bin/env python
"""Script para ver qué devuelve exactamente el schema."""

from app.database import SessionLocal
from app.models import HardwareItem
from app.schemas import HardwareItemResponse

db = SessionLocal()

print("🔍 Verificando serialización de items:\n")

# Obtener un item de cada categoría
items = db.query(HardwareItem).limit(3).all()

for item in items:
    print(f"Item ID {item.id}:")
    print(f"  Nombre: {item.nombre}")
    print(f"  Categoría (tipo): {type(item.categoria)}")
    print(f"  Categoría (valor): {item.categoria}")
    print(f"  Categoría (value): {item.categoria.value if hasattr(item.categoria, 'value') else 'N/A'}")
    print()
    
    # Intentar serializar con Pydantic
    try:
        response = HardwareItemResponse.model_validate(item)
        print(f"  Pydantic categoria: {response.categoria}")
        print(f"  Pydantic dict: {response.model_dump()}")
    except Exception as e:
        print(f"  Error en Pydantic: {e}")
    print()

db.close()
