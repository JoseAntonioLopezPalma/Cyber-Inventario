"""
Módulo para importar datos de CSVs a la base de datos.
Mapea automáticamente archivos CSV a categorías de hardware.
"""

import pandas as pd
import os
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import HardwareCategory
from app.crud import HardwareRepository
from app.schemas import HardwareItemCreate


# Mapeo de archivos CSV a categorías
CSV_MAPPING = {
    "CPUData.csv": HardwareCategory.MICROPROCESADORES,
    "CPUCoolerData.csv": HardwareCategory.REFRIGERADORES_CPU,
    "GPUData.csv": HardwareCategory.TARJETAS_GRAFICAS,
    "RAMData.csv": HardwareCategory.MEMORIA_RAM,
    "MotherboardData.csv": HardwareCategory.PLACAS_BASE,
    "CaseData.csv": HardwareCategory.GABINETES,
    "HDDData.csv": HardwareCategory.DISCOS_DUROS,
    "SSDData.csv": HardwareCategory.UNIDADES_SSD,
    "MonitorData.csv": HardwareCategory.MONITORES,
    "PSUData.csv": HardwareCategory.FUENTES_POWER,
}


def parse_price(price_str):
    """
    Extrae el valor numérico del precio.
    Ej: "$158.86 USD" -> 158.86
    """
    if pd.isna(price_str):
        return None
    
    price_str = str(price_str).strip()
    
    # Remover símbolos de moneda y texto
    price_str = price_str.replace("$", "").replace("USD", "").replace("£", "").strip()
    
    try:
        price = float(price_str)
        return price if price > 0 else None
    except ValueError:
        return None


def import_csv_file(db: Session, csv_path: str, categoria: HardwareCategory) -> dict:
    """
    Importa un archivo CSV a la base de datos.
    
    Args:
        db: Sesión de base de dados
        csv_path: Ruta al archivo CSV
        categoria: Categoría del hardware
        
    Returns:
        Dict con estadísticas de importación
    """
    repo = HardwareRepository(db)
    stats = {
        "archivo": os.path.basename(csv_path),
        "categoria": categoria.value,
        "insertados": 0,
        "errores": 0,
        "errores_detalles": []
    }
    
    if not os.path.exists(csv_path):
        stats["errores"] += 1
        stats["errores_detalles"].append(f"Archivo no encontrado: {csv_path}")
        return stats
    
    try:
        df = pd.read_csv(csv_path)
        
        for idx, row in df.iterrows():
            try:
                # Obtener nombre del producto
                nombre = row.get("Name", "").strip()
                
                if not nombre or nombre.lower() == "nan":
                    continue
                
                # Obtener y procesar precio
                precio = parse_price(row.get("Price", None))
                
                # Si no hay precio válido, usar un precio por defecto
                if precio is None:
                    precio = 0.01  # Precio mínimo permitido
                
                # Crear ítem
                item_create = HardwareItemCreate(
                    nombre=nombre,
                    categoria=categoria,
                    stock=1,
                    precio=precio
                )
                
                repo.crear(item_create)
                stats["insertados"] += 1
                
            except Exception as e:
                stats["errores"] += 1
                stats["errores_detalles"].append(f"Fila {idx}: {str(e)}")
                
    except Exception as e:
        stats["errores"] += 1
        stats["errores_detalles"].append(f"Error leyendo CSV: {str(e)}")
    
    return stats


def import_all_csvs(db: Session) -> list:
    """
    Importa todos los CSVs disponibles en la carpeta CSV/.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Lista con estadísticas de cada importación
    """
    results = []
    csv_folder = Path("CSV")
    
    if not csv_folder.exists():
        print(f"ERROR: Carpeta {csv_folder} no encontrada")
        return results
    
    for csv_file, categoria in CSV_MAPPING.items():
        csv_path = csv_folder / csv_file
        print(f"Importando {csv_file}...")
        
        stats = import_csv_file(db, str(csv_path), categoria)
        results.append(stats)
        
        # Mostrar resultado
        if stats["insertados"] > 0:
            print(f"  OK: {stats['insertados']} items insertados")
        if stats["errores"] > 0:
            print(f"  ADVERTENCIA: {stats['errores']} errores encontrados")
    
    return results


def print_summary(results: list):
    """Imprime un resumen de la importación."""
    print("\n" + "="*60)
    print("RESUMEN DE IMPORTACION")
    print("="*60)
    
    total_insertados = sum(r["insertados"] for r in results)
    total_errores = sum(r["errores"] for r in results)
    
    for r in results:
        status = "OK" if r["insertados"] > 0 else "SKIP"
        print(f"{status} {r['archivo']:20} | {r['insertados']:4} items | {r['errores']} errores")
    
    print("="*60)
    print(f"TOTAL: {total_insertados} items importados")
    if total_errores > 0:
        print(f"ADVERTENCIA: Total errores: {total_errores}")
    print("="*60)
