"""
Script para importar CSVs a la base de datos.
Ejecución: python import_csvs.py
"""

import sys
import io
from pathlib import Path

# Configurar UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal, init_db
from app.csv_importer import import_all_csvs, print_summary


def main():
    """Función principal de importación."""
    print("Iniciando importacion de archivos CSV...")
    print()
    
    # Inicializar base de datos
    try:
        init_db()
        print("OK: Base de datos inicializada\n")
    except Exception as e:
        print(f"ERROR al inicializar BD: {e}")
        return
    
    # Crear sesión y ejecutar importación
    db = SessionLocal()
    try:
        results = import_all_csvs(db)
        print_summary(results)
    except Exception as e:
        print(f"ERROR durante importacion: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
