#!/usr/bin/env python
"""Test rápido de categorías diversas."""

import httpx

print("✅ VERIFICACIÓN POST-FIX\n")
print("="*70)

response = httpx.get('http://localhost:8000/api/items?limit=15')
items = response.json()['items']

print(f"\n📊 Primeros 15 items (deberían ser de categorías variadas):\n")
for i, item in enumerate(items, 1):
    print(f"{i:2}. {item['categoria']:25} | {item['nombre'][:40]}")

# Contar categorías únicas
categories = set(item['categoria'] for item in items)
print(f"\n✅ Categorías diferentes en los primeros 15 items: {len(categories)}")
print(f"   Categorías: {', '.join(sorted(categories))}")
