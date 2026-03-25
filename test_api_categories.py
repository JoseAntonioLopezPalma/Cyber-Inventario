#!/usr/bin/env python
"""Script para verificar qué devuelve la API."""

import httpx
import json

print("🔍 Obteniendo items desde la API...\n")

# Test: Obtener primeros 10 items
response = httpx.get('http://localhost:8000/api/items?limit=10')
data = response.json()

print(f"Total items en respuesta: {len(data['items'])}\n")
print("Primeros 5 items con sus categorías:\n")

for i, item in enumerate(data['items'][:5], 1):
    print(f"{i}. {item['nombre'][:40]:40} | cat: {item['categoria']}")

print("\n" + "="*70)
print("\n🔍 Filtrando por categoría 'Microprocesadores'...\n")

response = httpx.get('http://localhost:8000/api/items?categoria=Microprocesadores&limit=3')
filtered_data = response.json()

print(f"Items encontrados: {len(filtered_data['items'])}\n")
for item in filtered_data['items'][:3]:
    print(f"   - {item['nombre'][:40]:40} | {item['categoria']}")

print("\n✅ Verificación completa")
