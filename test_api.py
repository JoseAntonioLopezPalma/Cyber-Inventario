#!/usr/bin/env python3
import sys
import time
import urllib.request
import json

time.sleep(2)  # Esperar a que el servidor inicie

try:
    response = urllib.request.urlopen('http://localhost:8000/api/items?skip=0&limit=2', timeout=5)
    data_raw = response.read().decode()
    data = json.loads(data_raw)
    
    print("SUCCESS")
    print(f"Total items: {data['total']}")
    if data['items']:
        print(f"Primer item ID: {data['items'][0]['id']}")
    sys.exit(0)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
