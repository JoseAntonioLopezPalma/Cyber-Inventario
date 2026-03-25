#!/usr/bin/env python
"""Verificar qué pasó con los items y el orden."""

from app.database import SessionLocal
from app.models import HardwareItem

db = SessionLocal()

print("🔍 Buscando item con ID 1:\n")
item1 = db.query(HardwareItem).filter(HardwareItem.id == 1).first()
if item1:
    print(f"Item ID 1: {item1.nombre} | {item1.categoria}")
else:
    print("No existe item con ID 1\n")

print("\n📊 Orden de items por ID:\n")
items = db.query(HardwareItem).order_by(HardwareItem.id).limit(15).all()
for item in items:
    print(f"ID {item.id:3} | {item.nombre[:40]:40} | {item.categoria}")

print("\n" + "="*80)
print("\n📊 Si ordenamos por categoría (como está en BD actual):\n")
items = db.query(HardwareItem).order_by(HardwareItem.categoria).limit(15).all()
for item in items:
    print(f"ID {item.id:3} | {item.nombre[:40]:40} | {item.categoria}")

db.close()
