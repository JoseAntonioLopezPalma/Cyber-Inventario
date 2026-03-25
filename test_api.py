#!/usr/bin/env python
"""Script rápido para verificar que la API está funcionando."""

import httpx
import sys

try:
    # Test health check
    print("🔍 Probando health check...")
    resp = httpx.get('http://localhost:8000/health')
    print(f"✓ Health check: {resp.status_code}")
    
    # Test items
    print("\n🔍 Obteniendo items...")
    resp = httpx.get('http://localhost:8000/api/items')
    data = resp.json()
    items_count = len(data.get('items', []))
    print(f"✓ Items encontrados: {items_count}")
    
    if items_count > 0:
        first_item = data['items'][0]
        print(f"✓ Primer item: {first_item.get('nombre')} - ${first_item.get('precio')}")
    
    # Test estadísticas
    print("\n🔍 Obteniendo estadísticas...")
    resp = httpx.get('http://localhost:8000/api/estadisticas')
    stats = resp.json()
    print(f"✓ Total items: {stats.get('total_items')}")
    print(f"✓ Valor total: ${stats.get('valor_total_inventario')}")
    
    print("\n✅ ¡LA API ESTÁ FUNCIONANDO CORRECTAMENTE!")
    print(f"\n🌐 Accede a: http://localhost:8000/")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"💡 Asegúrate que el servidor está corriendo: python -m uvicorn app.main:app --reload")
    sys.exit(1)
