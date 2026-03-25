#!/usr/bin/env python
"""Script para verificar las categorías en la BD."""

from app.database import SessionLocal
from app.models import HardwareItem, HardwareCategory

db = SessionLocal()

# Contar items por categoría
print("📊 ITEMS POR CATEGORÍA EN LA BD:\n")
for category in HardwareCategory:
    items = db.query(HardwareItem).filter(HardwareItem.categoria == category).count()
    print(f"   {category.value:25} | {items:4} items")

print("\n" + "="*60)

# Mostrar primeros 5 items de cada categoría
print("\n🔍 PRIMEROS ITEMS POR CATEGORÍA:\n")
for category in HardwareCategory:
    items = db.query(HardwareItem).filter(HardwareItem.categoria == category).limit(2).all()
    if items:
        print(f"\n{category.value}:")
        for item in items:
            print(f"   - {item.nombre[:40]:40} | ${item.precio}")

db.close()
