# 📊 Guía de Importación de Datos CSV

## Descripción

El sistema incluye un script de importación que carga datos desde archivos CSV en la carpeta `CSV/` directamente a la base de datos SQLite.

**Categorías Mapeadas:**
- `CPUData.csv` → Microprocesadores
- `CPUCoolerData.csv` → Refrigeradores CPU
- `GPUData.csv` → Tarjetas Gráficas
- `RAMData.csv` → Memoria RAM
- `MotherboardData.csv` → Placas Base
- `CaseData.csv` → Gabinetes
- `HDDData.csv` → Discos Duros
- `SSDData.csv` → Unidades SSD
- `MonitorData.csv` → Monitores
- `PSUData.csv` → Fuentes Power

---

## 🚀 Uso

### Requisitos Previos

```bash
# 1. Asegúrate de que está instalado pandas
pip install pandas

# 2. Verifica que los archivos CSV están en la carpeta CSV/
ls CSV/
```

### Ejecutar la Importación

```bash
# Desde la raíz del proyecto
python import_csv_data.py
```

### Salida Esperada

```
============================================================
 🚀 CYBER-INVENTORY - Importador de Datos CSV
============================================================

📊 Inicializando base de datos...
   ✓ Base de datos lista

📦 Se encontraron 10 archivos CSV

📂 Leyendo CPUData.csv...
   ✓ 200 registros encontrados
   ✓ Importados: 200
   ...

============================================================
 📊 RESUMEN DE IMPORTACIÓN
============================================================
   ✓ Total importados: 3456
   
📈 ESTADÍSTICAS DE INVENTARIO
============================================================
   Total de ítems: 3456
   Valor total: $125,450.75 USD

📂 POR CATEGORÍA
------------------------------------------------------------
   Microprocesadores        | 200 items | $125,750.00
   Tarjetas Gráficas        | 150 items | $250,000.00
   ...
============================================================
✅ ¡Importación completada!
============================================================
```

---

## 📋 Estructura de Archivos CSV

El script espera que los CSV tengan al menos estas columnas:

### Columnas Requeridas
- **Name**: Nombre del producto (obligatorio)
- **Price**: Precio en formato "$XXX.XX USD" (obligatorio)

### Ejemplo
```csv
Name,Price,Producer,MPN
Intel Core i9-13900K,$689.99 USD,Intel,BX8071514208014
AMD Ryzen 5 5600X,$158.86 USD,AMD,100-100000065BOX
```

---

## ⚙️ Comportamiento del Script

### 1. **Lectura de CSV**
- Lee todos los archivos `.csv` de la carpeta `CSV/`
- Detecta automáticamente la categoría según el nombre del archivo
- Valida que existan columnas "Name" y "Price"

### 2. **Limpieza de Datos**
- Elimina espacios en blanco
- Extrae precio numérico de strings como "$XXX.XX USD"
- Descarta productos con precio ≤ 0
- Maneja valores faltantes (NaN)

### 3. **Inserción**
- Si el producto YA EXISTE: actualiza el precio
- Si NO EXISTE: crea nuevo con stock inicial = 1
- Todas las operaciones son transaccionales

### 4. **Reporte**
- Muestra progreso cada 50 items
- Resume total importado vs errores
- Calcula estadísticas por categoría

---

## 🔍 Casos de Uso Avanzados

### Importar Solo Categoría Específica

Modifica el script para descomentar solo una categoría:

```python
CSV_CATEGORY_MAPPING = {
    "CPUData.csv": "Microprocesadores",  # ✓ Importar solo esto
    # ... resto comentado
}
```

### Cambiar Stock Inicial

Edita la línea en `import_csv_file()`:

```python
new_item = HardwareItem(
    ...
    stock=5,  # ← Cambiar de 1 a 5
    ...
)
```

### Importar CSV Externo

```python
python import_csv_data.py
# O modifica el path en get_csv_files()
```

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'pandas'"
```bash
pip install pandas
```

### Error: "Carpeta 'CSV' no encontrada"
- Verifica que existe `c:\Users\Candryl\Desktop\Proyecto\CSV\`
- Crea la carpeta si no existe: `mkdir CSV`

### No se importan productos
Verifica:
1. Archivos CSV existen en carpeta `CSV/`
2. Columna "Name" existe
3. Columna "Price" existe
4. Precios tienen formato válido: "$XXX.XX USD"

### Duplicados después de importación
El script actualiza precios de productos existentes. Para reimportar limpio:
```bash
# Elimina la base de datos
rm warehouse.db

# Vuelve a importar
python import_csv_data.py
```

---

## 📊 Verificar Datos Importados

Después de importar, verifica los datos:

```python
# En Python interactivo
from app.database import SessionLocal
from app.crud import HardwareRepository

db = SessionLocal()
repo = HardwareRepository(db)

# Total de items
print(f"Total items: {repo.obtener_total_items()}")

# Valor total
print(f"Valor total: ${repo.obtener_valor_total_inventario()}")

# Items por categoría
for cat in ["Microprocesadores", "Tarjetas Gráficas", "Memoria RAM"]:
    items = repo.obtener_por_categoria(cat)
    total = sum(i.precio * i.stock for i in items)
    print(f"{cat}: {len(items)} items, ${total:.2f}")
```

O desde el navegador:
- Abre http://localhost:8000/docs
- Usa GET `/api/estadisticas` para ver totales
- Usa GET `/api/items` para listar productos

---

## 🔄 Pipeline Completo

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Importar datos CSV
python import_csv_data.py

# 3. Iniciar servidor
python -m uvicorn app.main:app --reload

# 4. Acceder al frontend
# http://localhost:8000/
# http://localhost:8000/docs

# 5. Ejecutar tests
pytest tests/ -v
```

---

## 📈 Performance

| Métrica | Tiempo Típico |
|---------|---|
| Lectura 1 CSV (200 items) | < 100ms |
| Importación total (10 CSVs, 3000+ items) | < 5 segundos |
| Validación y limpieza | Incluido |

---

## 🎯 Mapeo de Categorías

| Archivo CSV | Categoría ES | Stock Inicial |
|---|---|---|
| CPUData.csv | Microprocesadores | 1 |
| CPUCoolerData.csv | Refrigeradores CPU | 1 |
| GPUData.csv | Tarjetas Gráficas | 1 |
| RAMData.csv | Memoria RAM | 1 |
| MotherboardData.csv | Placas Base | 1 |
| CaseData.csv | Gabinetes | 1 |
| HDDData.csv | Discos Duros | 1 |
| SSDData.csv | Unidades SSD | 1 |
| MonitorData.csv | Monitores | 1 |
| PSUData.csv | Fuentes Power | 1 |

---

## ✅ Checklist Pre-Importación

- [ ] Carpeta `CSV/` existe y tiene archivos `.csv`
- [ ] Cada CSV tiene columnas "Name" y "Price"
- [ ] Precios tienen formato "$XXX.XX USD"
- [ ] Pandas está instalado: `pip list | grep pandas`
- [ ] Base de datos puede ser sobrescrita (si es necesario)
- [ ] Espacio en disco disponible (estimado: 1MB por 5000 items)

---

**¡Listo para importar datos!** 📦
