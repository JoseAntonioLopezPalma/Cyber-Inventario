#!/usr/bin/env python
"""Verificar serialización de categorías."""

import httpx

print("🔍 Verificando categorías en respuesta JSON:\n")

response = httpx.get('http://localhost:8000/api/items?limit=5')
items = response.json()['items']

for i, item in enumerate(items, 1):
    cat = item['categoria']
    print(f"{i}. {item['nombre'][:40]:40} | {cat} (type: {type(cat).__name__})")
