#!/usr/bin/env python
"""Script para verificar el orden en la BD."""

from app.database import SessionLocal
from app.models import HardwareItem

db = SessionLocal()

print("📊 PRIMEROS 20 ITEMS EN LA BD (orden actual):\n")
items = db.query(HardwareItem).limit(20).all()

for i, item in enumerate(items, 1):
    print(f"{i:2}. {item.nombre[:40]:40} | ID: {item.id:4} | {item.categoria}")

db.close()
