#!/usr/bin/env python
"""Script de depuración para verificar los schemas"""

from app.database import SessionLocal
from app.models import HardwareItem
from app.schemas import HardwareItemResponse
import json

db = SessionLocal()

# Obtener el item más caro en stock
item = db.query(HardwareItem).filter(
    HardwareItem.stock > 0
).order_by(HardwareItem.precio.desc()).first()

if item:
    print(f"Item encontrado: {item.nombre}")
    print(f"Categoría tipo: {type(item.categoria)}")
    print(f"Categoría value: {item.categoria}")
    print(f"Categoría .value: {item.categoria.value if hasattr(item.categoria, 'value') else 'N/A'}")
    
    # Intentar serializar
    try:
        # Method 1: Direct return (what FastAPI does)
        print("\n=== Intento 1: Crear schema desde objeto ORM ===")
        response = HardwareItemResponse.model_validate(item)
        print(f"OK: {response}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
    
    # Method 2: Manual conversion
    try:
        print("\n=== Intento 2: Conversión manual ===")
        data = {
            'id': item.id,
            'nombre': item.nombre,
            'categoria': item.categoria.value,  # Convert enum to string
            'stock': item.stock,
            'precio': item.precio,
            'fecha_entrada': item.fecha_entrada
        }
        response = HardwareItemResponse(**data)
        print(f"OK: {response.model_dump_json()}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")

    # Method 3: Using from_attributes
    try:
        print("\n=== Intento 3: Usando from_attributes ===")
        response_dict = {
            'id': item.id,
            'nombre': item.nombre,
            'categoria': item.categoria,
            'stock': item.stock,
            'precio': item.precio,
            'fecha_entrada': item.fecha_entrada
        }
        response = HardwareItemResponse(**response_dict)
        print(f"OK: {response}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
else:
    print("No hay items en stock")

db.close()
