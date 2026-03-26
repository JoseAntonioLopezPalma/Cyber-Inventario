"""
FastAPI Application - Punto de entrada principal.
Endpoints RESTful para gestión de inventario de hardware.
Documentación automática disponible en /docs (Swagger) y /redoc
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import os

from app.database import get_db, init_db
from app.crud import HardwareRepository
from app.schemas import (
    HardwareItemCreate,
    HardwareItemUpdate,
    HardwareItemResponse,
    HardwareItemListResponse,
    HardwareCategoryEnum,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación."""
    init_db()
    yield

# Inicialización de FastAPI
app = FastAPI(
    title="Cyber-Inventory API",
    description="Sistema de gestión de almacén de hardware informático",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ==================== ENDPOINTS CRUD ====================

@app.post(
    "/api/items",
    response_model=HardwareItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo ítem de hardware",
    tags=["Hardware Items"],
)
async def crear_item(
    item: HardwareItemCreate,
    db: Session = Depends(get_db),
):
    """
    Crea un nuevo ítem de hardware en el inventario.
    
    Validaciones:
    - El precio debe ser positivo
    - El stock debe ser >= 0
    - El nombre no puede estar vacío
    """
    repository = HardwareRepository(db)
    db_item = repository.crear(item)
    return db_item


@app.get(
    "/api/items/{item_id}",
    response_model=HardwareItemResponse,
    summary="Obtener ítem por ID",
    tags=["Hardware Items"],
)
async def obtener_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    """
    Obtiene los detalles de un ítem específico.
    
    Returns:
        404: Si el ítem no existe
    """
    repository = HardwareRepository(db)
    db_item = repository.obtener_por_id(item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ítem con ID {item_id} no encontrado",
        )
    return db_item


@app.get(
    "/api/items",
    response_model=HardwareItemListResponse,
    summary="Listar ítems con paginación y filtros",
    tags=["Hardware Items"],
)
async def listar_items(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros"),
    categoria: Optional[str] = Query(
        None, description="Filtrar por categoría"
    ),
    sort_by: Optional[str] = Query(
        "id", description="Campo por el cual ordenar (id, nombre_articulo, stock, precio, categoria)"
    ),
    order: Optional[str] = Query(
        "desc", description="Orden: 'asc' (ascendente) o 'desc' (descendente)"
    ),
    db: Session = Depends(get_db),
):
    """
    Lista todos los ítems con soporte para paginación, filtros y ordenamiento.
    
    Query Parameters:
    - skip: Offset para paginación (default: 0)
    - limit: Máximo de resultados (default: 100, máximo: 1000)
    - categoria: Filtro opcional por categoría
    - sort_by: Campo para ordenamiento (id, nombre_articulo, stock, precio, categoria)
    - order: 'asc' o 'desc' (default: desc)
    """
    repository = HardwareRepository(db)
    items = repository.obtener_todos(
        skip=skip, 
        limit=limit, 
        categoria=categoria,
        sort_by=sort_by,
        order=order
    )
    # Obtener total de items (considerando filtro de categoría)
    total = repository.obtener_total_items(categoria=categoria)
    precio_total = repository.obtener_valor_total_inventario(categoria=categoria)
    
    return HardwareItemListResponse(
        total=total,
        items=items,
        precio_total_inventario=precio_total,
    )


@app.put(
    "/api/items/{item_id}",
    response_model=HardwareItemResponse,
    summary="Actualizar ítem",
    tags=["Hardware Items"],
)
async def actualizar_item(
    item_id: int,
    item_update: HardwareItemUpdate,
    db: Session = Depends(get_db),
):
    """
    Actualiza un ítem existente (soporta actualización parcial).
    
    Returns:
        404: Si el ítem no existe
    """
    repository = HardwareRepository(db)
    db_item = repository.actualizar(item_id, item_update)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ítem con ID {item_id} no encontrado",
        )
    return db_item


@app.delete(
    "/api/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar ítem",
    tags=["Hardware Items"],
)
async def eliminar_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    """
    Elimina un ítem del inventario.
    
    Returns:
        204: Eliminación exitosa
        404: Si el ítem no existe
    """
    repository = HardwareRepository(db)
    success = repository.eliminar(item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ítem con ID {item_id} no encontrado",
        )
    return None


# ==================== ENDPOINTS DE NEGOCIO ====================

@app.post(
    "/api/items/{item_id}/reducir-stock",
    response_model=HardwareItemResponse,
    summary="Reducir stock (venta/retiro)",
    tags=["Operaciones de Inventario"],
)
async def reducir_stock(
    item_id: int,
    cantidad: int = Query(..., ge=1, description="Cantidad a reducir"),
    db: Session = Depends(get_db),
):
    """
    Reduce el stock de un ítem (simula una venta o retiro).
    
    Validaciones:
    - La cantidad debe ser positiva
    - Debe haber stock suficiente
    
    Returns:
        400: Si no hay stock suficiente
        404: Si el ítem no existe
    """
    repository = HardwareRepository(db)
    try:
        db_item = repository.reducir_stock(item_id, cantidad)
        if not db_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ítem con ID {item_id} no encontrado",
            )
        return db_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@app.post(
    "/api/items/{item_id}/aumentar-stock",
    response_model=HardwareItemResponse,
    summary="Aumentar stock (entrada de inventario)",
    tags=["Operaciones de Inventario"],
)
async def aumentar_stock(
    item_id: int,
    cantidad: int = Query(..., ge=1, description="Cantidad a agregar"),
    db: Session = Depends(get_db),
):
    """
    Aumenta el stock de un ítem (entrada de mercadería).
    
    Validaciones:
    - La cantidad debe ser positiva
    
    Returns:
        404: Si el ítem no existe
    """
    repository = HardwareRepository(db)
    db_item = repository.aumentar_stock(item_id, cantidad)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ítem con ID {item_id} no encontrado",
        )
    return db_item


@app.get(
    "/api/categorias/{categoria}",
    response_model=HardwareItemListResponse,
    summary="Obtener ítems por categoría",
    tags=["Búsqueda"],
)
async def obtener_por_categoria(
    categoria: str,
    db: Session = Depends(get_db),
):
    """
    Obtiene todos los ítems de una categoría específica.
    """
    repository = HardwareRepository(db)
    items = repository.obtener_por_categoria(categoria)
    total = len(items)
    precio_total = sum(item.stock * item.precio for item in items)
    
    return HardwareItemListResponse(
        total=total,
        items=items,
        precio_total_inventario=precio_total,
    )


@app.get(
    "/api/buscar",
    response_model=HardwareItemListResponse,
    summary="Buscar ítems por nombre",
    tags=["Búsqueda"],
)
async def buscar_por_nombre(
    q: str = Query(..., min_length=1, description="Texto a buscar"),
    db: Session = Depends(get_db),
):
    """
    Busca ítems cuyo nombre contenga el texto proporcionado.
    """
    repository = HardwareRepository(db)
    items = repository.buscar_por_nombre(q)
    total = len(items)
    precio_total = sum(item.stock * item.precio for item in items)
    
    return HardwareItemListResponse(
        total=total,
        items=items,
        precio_total_inventario=precio_total,
    )


@app.get(
    "/api/estadisticas",
    summary="Obtener estadísticas del inventario",
    tags=["Reportes"],
)
async def obtener_estadisticas(
    db: Session = Depends(get_db),
):
    """
    Retorna estadísticas generales del inventario.
    """
    repository = HardwareRepository(db)
    total_items = repository.obtener_total_items()
    valor_total = repository.obtener_valor_total_inventario()
    
    return {
        "total_items": total_items,
        "valor_total_inventario": round(valor_total, 2),
        "moneda": "USD",
    }


@app.get(
    "/api/items/mas-caro/stock",
    response_model=HardwareItemResponse,
    summary="Obtener item más caro en stock",
    tags=["Reportes"],
)
async def obtener_item_mas_caro_en_stock(
    db: Session = Depends(get_db),
):
    """
    Retorna el ítem más caro que tiene stock disponible.
    
    Returns:
        404: Si no hay ítems con stock
    """
    repository = HardwareRepository(db)
    item = repository.obtener_mas_caro_en_stock()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay ítems en stock",
        )
    return item


@app.post(
    "/api/importar-csv",
    summary="Importar datos de CSV",
    tags=["Datos"],
)
async def importar_csv_data(
    db: Session = Depends(get_db),
):
    """
    Ejecuta la importación de archivos CSV desde la carpeta ./data
    
    Returns:
        Mensaje con cantidad de items importados
    """
    try:
        import subprocess
        import sys
        
        # Ejecutar el script de importación
        result = subprocess.run(
            [sys.executable, "import_csv_data.py"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        if result.returncode != 0:
            raise Exception(result.stderr or "Error ejecutando el script")
        
        return {
            "success": True,
            "mensaje": f"Importación completada\n{result.stdout}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al importar CSV: {str(e)}"
        )


# ==================== ENDPOINTS DE FRONTEND ====================

@app.get("/", tags=["Frontend"])
async def root():
    """Sirve la página principal del frontend."""
    return FileResponse("static/index.html")


# Montar archivos estáticos
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# ==================== HEALTH CHECK ====================

@app.get("/health", tags=["Sistema"], summary="Verificar estado de la API")
async def health_check():
    """Endpoint para verificar que la API está activa."""
    return {"status": "healthy", "service": "Cyber-Inventory"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
