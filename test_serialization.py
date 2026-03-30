from app.database import SessionLocal
from app.models import HardwareItem
from app.schemas import HardwareItemResponse
from datetime import datetime

db = SessionLocal()
items = db.query(HardwareItem).limit(2).all()

print(f"Items encontrados: {len(items)}")

for item in items:
    print(f"Item bruto: ID={item.id}, nombre={item.nombre}, categoria={item.categoria}")
    print(f"Categoria type: {type(item.categoria)}")
    print(f"Fecha entrada: {item.fecha_entrada}")
    
    try:
        response = HardwareItemResponse.model_validate(item)
        print(f"Response model: {response}")
        import json
        print(f"JSON: {response.model_dump_json()}")
    except Exception as e:
        print(f"Error serializando: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
    break
