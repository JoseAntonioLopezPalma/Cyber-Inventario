"""
Script para eliminar duplicados de la base de datos.
Mantiene el primer registro de cada nombre y elimina los duplicados.
"""

from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker
from app.database import DATABASE_URL, Base
from app.models import HardwareItem, HardwareCategory

# Crear conexión a la base de datos
engine = create_engine(
    "sqlite:///./warehouse.db",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Obtener el conteo inicial
    initial_count = db.query(HardwareItem).count()
    print(f"Registros iniciales: {initial_count}")
    
    # Encontrar duplicados por nombre
    duplicates = db.query(
        HardwareItem.nombre,
        func.count(HardwareItem.id).label('count')
    ).group_by(HardwareItem.nombre).having(
        func.count(HardwareItem.id) > 1
    ).all()
    
    print(f"\nNombres duplicados encontrados: {len(duplicates)}")
    
    removed_count = 0
    
    for nombre, count in duplicates:
        # Obtener todos los IDs con este nombre
        items = db.query(HardwareItem.id).filter(
            HardwareItem.nombre == nombre
        ).order_by(HardwareItem.id).all()
        
        # Mantener el primero, eliminar el resto
        ids_to_delete = [item.id for item in items[1:]]
        
        if ids_to_delete:
            db.query(HardwareItem).filter(
                HardwareItem.id.in_(ids_to_delete)
            ).delete(synchronize_session=False)
            removed_count += len(ids_to_delete)
            print(f"  • {nombre}: {count} registros → mantiene 1, elimina {len(ids_to_delete)}")
    
    # Confirmar cambios
    db.commit()
    
    # Verificar resultado final
    final_count = db.query(HardwareItem).count()
    print(f"\n✓ Registros eliminados: {removed_count}")
    print(f"✓ Registros finales: {final_count}")
    print(f"✓ Base de datos limpia")

except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
