"""
Script de Importación de Datos desde CSV a la Base de Datos.
Utiliza pandas para leer archivos CSV y SQLAlchemy para insertar en la BD.

Uso:
    python import_csv_data.py
"""

import os
import pandas as pd
from pathlib import Path
from decimal import Decimal
from sqlalchemy.orm import Session

from app.database import SessionLocal, init_db
from app.models import HardwareItem, HardwareCategory
from app.crud import HardwareRepository


# Mapping de archivos CSV a categorías (en español)
CSV_CATEGORY_MAPPING = {
    "CPUData.csv": "Microprocesadores",
    "CPUCoolerData.csv": "Refrigeradores CPU",
    "GPUData.csv": "Tarjetas Gráficas",
    "RAMData.csv": "Memoria RAM",
    "MotherboardData.csv": "Placas Base",
    "CaseData.csv": "Gabinetes",
    "HDDData.csv": "Discos Duros",
    "SSDData.csv": "Unidades SSD",
    "MonitorData.csv": "Monitores",
    "PSUData.csv": "Fuentes Power",
}


def extract_price(price_str):
    """
    Extrae el precio numérico de una cadena como "$123.45 USD".
    
    Args:
        price_str: String con formato "$XXX.XX USD" o None
        
    Returns:
        float o 0.0 si no se puede extraer
    """
    if pd.isna(price_str) or price_str == "":
        return 0.0
    
    try:
        # Remover $ y "USD" y espacios
        price_clean = str(price_str).replace("$", "").replace("USD", "").strip()
        return float(price_clean)
    except (ValueError, AttributeError):
        return 0.0


def clean_name(name):
    """Limpia y normaliza el nombre del producto."""
    if pd.isna(name):
        return "Producto Sin Nombre"
    return str(name).strip()


def import_csv_file(csv_path: str, category: str, db_session: Session):
    """
    Importa un archivo CSV específico a la base de datos.
    
    Args:
        csv_path: Ruta al archivo CSV
        category: Categoría en español para estos items
        db_session: Sesión de base de datos activa
        
    Returns:
        tuple: (cantidad_importada, cantidad_errores)
    """
    print(f"\n📂 Leyendo {Path(csv_path).name}...")
    
    try:
        # Leer CSV
        df = pd.read_csv(csv_path)
        print(f"   ✓ {len(df)} registros encontrados")
        
        if len(df) == 0:
            print(f"   ⚠ Archivo vacío, saltando...")
            return 0, 0
        
        # Validar que existan columnas mínimas
        if "Name" not in df.columns or "Price" not in df.columns:
            print(f"   ✗ Columnas 'Name' o 'Price' no encontradas")
            return 0, len(df)
        
        repository = HardwareRepository(db_session)
        imported_count = 0
        error_count = 0
        
        # Procesar cada fila
        for idx, row in df.iterrows():
            try:
                nombre = clean_name(row.get("Name"))
                precio = extract_price(row.get("Price"))
                
                # Validar precio mínimo
                if precio <= 0:
                    error_count += 1
                    continue
                
                # Crear item
                existing = db_session.query(HardwareItem).filter(
                    HardwareItem.nombre == nombre
                ).first()
                
                if existing:
                    # Actualizar precio si es diferente
                    if existing.precio != precio:
                        existing.precio = precio
                        db_session.commit()
                else:
                    # Crear nuevo item con stock inicial = 1
                    new_item = HardwareItem(
                        nombre=nombre,
                        categoria=HardwareCategory(category),
                        stock=1,
                        precio=precio,
                    )
                    db_session.add(new_item)
                    db_session.commit()
                
                imported_count += 1
                
                # Mostrar progreso cada 50 items
                if (imported_count + error_count) % 50 == 0:
                    print(f"   ⏳ Procesados {imported_count + error_count}/{len(df)} registros...")
                
            except Exception as e:
                error_count += 1
                print(f"   ! Error en fila {idx}: {str(e)[:50]}")
        
        print(f"   ✓ Importados: {imported_count}")
        if error_count > 0:
            print(f"   ⚠ Errores: {error_count}")
        
        return imported_count, error_count
        
    except FileNotFoundError:
        print(f"   ✗ Archivo no encontrado: {csv_path}")
        return 0, 1
    except Exception as e:
        print(f"   ✗ Error al leer CSV: {str(e)}")
        return 0, 1


def get_csv_files() -> dict:
    """
    Descubre archivos CSV en la carpeta CSV/ automáticamente.
    
    Returns:
        dict: {ruta_csv: categoria_español}
    """
    csv_folder = Path("CSV")
    
    if not csv_folder.exists():
        print("❌ Carpeta 'CSV' no encontrada")
        return {}
    
    csv_files = {}
    for csv_file in csv_folder.glob("*.csv"):
        filename = csv_file.name
        if filename in CSV_CATEGORY_MAPPING:
            category = CSV_CATEGORY_MAPPING[filename]
            csv_files[str(csv_file)] = category
        else:
            print(f"⚠  Archivo CSV desconocido: {filename}")
    
    return csv_files


def main():
    """Función principal de importación."""
    print("\n" + "="*60)
    print(" 🚀 CYBER-INVENTORY - Importador de Datos CSV")
    print("="*60)
    
    # Inicializar base de datos
    print("\n📊 Inicializando base de datos...")
    init_db()
    print("   ✓ Base de datos lista")
    
    # Obtener archivos CSV
    csv_files = get_csv_files()
    if not csv_files:
        print("\n❌ No se encontraron archivos CSV válidos")
        return
    
    print(f"\n📦 Se encontraron {len(csv_files)} archivos CSV")
    
    # Importar cada archivo
    db_session = SessionLocal()
    total_imported = 0
    total_errors = 0
    
    try:
        for csv_path, category in csv_files.items():
            imported, errors = import_csv_file(csv_path, category, db_session)
            total_imported += imported
            total_errors += errors
    finally:
        db_session.close()
    
    # Resumen final
    print("\n" + "="*60)
    print(f" 📊 RESUMEN DE IMPORTACIÓN")
    print("="*60)
    print(f"   ✓ Total importados: {total_imported}")
    if total_errors > 0:
        print(f"   ⚠ Total errores: {total_errors}")
    
    # Estadísticas finales
    db_session = SessionLocal()
    try:
        repository = HardwareRepository(db_session)
        total_items = repository.obtener_total_items()
        total_value = repository.obtener_valor_total_inventario()
        
        print("\n📈 ESTADÍSTICAS DE INVENTARIO")
        print("="*60)
        print(f"   Total de ítems: {total_items}")
        print(f"   Valor total: ${total_value:,.2f} USD")
        
        # Por categoría
        print("\n📂 POR CATEGORÍA")
        print("-"*60)
        for category in HardwareCategory:
            items = repository.obtener_por_categoria(category.value)
            if items:
                count = len(items)
                value = sum(item.stock * item.precio for item in items)
                print(f"   {category.value:25} | {count:3} items | ${value:>12,.2f}")
        
    finally:
        db_session.close()
    
    print("\n" + "="*60)
    print("✅ ¡Importación completada!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
