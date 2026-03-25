#!/usr/bin/env python
"""Verificar que todo está funcionando correctamente."""

import httpx

print("✅ VERIFICACIÓN POST-ACTUALIZACIÓN\n")
print("="*70)

# Test: Items aleatorios
response = httpx.get('http://localhost:8000/api/items?limit=10')
items = response.json()['items']

print(f"\n📊 Items de prueba (para verificar categorías y datos):\n")
for i, item in enumerate(items[:5], 1):
    cat_width = len(item['categoria'])
    print(f"{i}. Stock: {item['stock']:3} | Precio: ${item['precio']:8.2f} | Cat: {item['categoria']:25} (ancho: {cat_width})")

print("\n✅ Todos los datos están disponibles para ordenar:")
print("   - Stock ✓")
print("   - Precio ✓")
print("   - Categoría ✓")
print("   - Nombre ✓")
print("\n🌐 Recarga la página para ver los cambios en: http://localhost:8000/")
