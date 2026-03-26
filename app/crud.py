"""
CRUD Operations con patrón Repository.
Abstrae la lógica de persistencia de la lógica de negocio.
Sigue principios SOLID: responsabilidad única, inyección de dependencias.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models import HardwareItem, HardwareCategory
from app.schemas import HardwareItemCreate, HardwareItemUpdate


class HardwareRepository:
    """
    Repositorio para operaciones CRUD en HardwareItem.
    Abstrae la complejidad de SQLAlchemy y proporciona una interfaz limpia.
    """

    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesión de base de datos.
        
        Args:
            db: Sesión SQLAlchemy activa
        """
        self.db = db

    def crear(self, item: HardwareItemCreate) -> HardwareItem:
        """
        Crea un nuevo ítem de hardware.
        
        Args:
            item: Datos del ítem a crear (validados por Pydantic)
            
        Returns:
            El ítem creado con ID asignado
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        db_item = HardwareItem(
            nombre=item.nombre,
            categoria=item.categoria,
            stock=item.stock,
            precio=item.precio,
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def obtener_por_id(self, item_id: int) -> Optional[HardwareItem]:
        """
        Obtiene un ítem por su ID.
        
        Args:
            item_id: ID del ítem a recuperar
            
        Returns:
            El ítem si existe, None si no
        """
        return self.db.query(HardwareItem).filter(HardwareItem.id == item_id).first()

    def obtener_todos(
        self, 
        skip: int = 0, 
        limit: int = 100,
        categoria: Optional[str] = None,
        sort_by: str = "id",
        order: str = "desc"
    ) -> List[HardwareItem]:
        """
        Obtiene todos los ítems con filtros opcionales y ordenamiento.
        
        Args:
            skip: Número de registros a saltar (paginación)
            limit: Número máximo de registros a retornar
            categoria: Filtro opcional por categoría
            sort_by: Campo para ordenar (id, nombre_articulo, stock, precio, categoria)
            order: Dirección del orden ('asc' o 'desc')
            
        Returns:
            Lista de ítems ordenados y paginados
        """
        query = self.db.query(HardwareItem)
        
        if categoria:
            # Si hay filtro de categoría, mostrar items de esa categoría
            query = query.filter(HardwareItem.categoria == categoria)
        
        # Aplicar ordenamiento ANTES de la paginación (CRÍTICO)
        # Validar el campo de ordenamiento para prevenir SQL injection
        valid_columns = {
            "id": HardwareItem.id,
            "nombre_articulo": HardwareItem.nombre,
            "stock": HardwareItem.stock,
            "precio": HardwareItem.precio,
            "categoria": HardwareItem.categoria,
        }
        
        if sort_by not in valid_columns:
            sort_by = "id"
        
        column = valid_columns[sort_by]
        
        # Aplicar orden ascendente o descendente
        if order.lower() == "asc":
            query = query.order_by(column.asc())
        else:
            query = query.order_by(column.desc())
        
        # IMPORTANTE: Aplicar paginación DESPUÉS del ordenamiento
        return query.offset(skip).limit(limit).all()

    def obtener_por_categoria(self, categoria: str) -> List[HardwareItem]:
        """
        Obtiene todos los ítems de una categoría específica.
        
        Args:
            categoria: Nombre de la categoría
            
        Returns:
            Lista de ítems en esa categoría
        """
        return self.db.query(HardwareItem).filter(
            HardwareItem.categoria == categoria
        ).all()

    def actualizar(
        self, 
        item_id: int, 
        item_update: HardwareItemUpdate
    ) -> Optional[HardwareItem]:
        """
        Actualiza un ítem existente.
        
        Args:
            item_id: ID del ítem a actualizar
            item_update: Datos a actualizar (solo los campos proporcionados)
            
        Returns:
            El ítem actualizado o None si no existe
        """
        db_item = self.obtener_por_id(item_id)
        if not db_item:
            return None

        # Actualiza solo los campos proporcionados
        update_data = item_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)

        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def eliminar(self, item_id: int) -> bool:
        """
        Elimina un ítem por su ID.
        
        Args:
            item_id: ID del ítem a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        db_item = self.obtener_por_id(item_id)
        if not db_item:
            return False

        self.db.delete(db_item)
        self.db.commit()
        return True

    def obtener_total_items(self, categoria: Optional[str] = None) -> int:
        """
        Obtiene la cantidad total de ítems en el inventario.
        
        Args:
            categoria: Filtro opcional por categoría
        
        Returns:
            Número total de ítems
        """
        query = self.db.query(func.count(HardwareItem.id))
        if categoria:
            query = query.filter(HardwareItem.categoria == categoria)
        return query.scalar()

    def obtener_valor_total_inventario(self, categoria: Optional[str] = None) -> float:
        """
        Calcula el valor total del inventario (stock * precio).
        
        Args:
            categoria: Filtro opcional por categoría
        
        Returns:
            Valor total en dinero
        """
        query = self.db.query(
            func.sum(HardwareItem.stock * HardwareItem.precio)
        )
        if categoria:
            query = query.filter(HardwareItem.categoria == categoria)
        result = query.scalar()
        return float(result) if result else 0.0

    def obtener_stock_por_categoria(self, categoria: str) -> int:
        """
        Obtiene el stock total de una categoría.
        
        Args:
            categoria: Nombre de la categoría
            
        Returns:
            Cantidad total de ítems en esa categoría
        """
        result = self.db.query(
            func.sum(HardwareItem.stock)
        ).filter(HardwareItem.categoria == categoria).scalar()
        return int(result) if result else 0

    def reducir_stock(self, item_id: int, cantidad: int) -> Optional[HardwareItem]:
        """
        Reduce el stock de un ítem (venta/retiro).
        
        Args:
            item_id: ID del ítem
            cantidad: Cantidad a reducir
            
        Returns:
            El ítem actualizado o None si no existe
            
        Raises:
            ValueError: Si no hay stock suficiente
        """
        db_item = self.obtener_por_id(item_id)
        if not db_item:
            return None

        if db_item.stock < cantidad:
            raise ValueError(
                f"Stock insuficiente. Disponible: {db_item.stock}, "
                f"Solicitado: {cantidad}"
            )

        db_item.stock -= cantidad
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def aumentar_stock(self, item_id: int, cantidad: int) -> Optional[HardwareItem]:
        """
        Aumenta el stock de un ítem (entrada de inventario).
        
        Args:
            item_id: ID del ítem
            cantidad: Cantidad a agregar
            
        Returns:
            El ítem actualizado o None si no existe
        """
        db_item = self.obtener_por_id(item_id)
        if not db_item:
            return None

        db_item.stock += cantidad
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def buscar_por_nombre(self, nombre: str) -> List[HardwareItem]:
        """
        Busca ítems cuyo nombre contenga la cadena dada.
        
        Args:
            nombre: Texto a buscar (case-insensitive)
            
        Returns:
            Lista de ítems que coinciden
        """
        return self.db.query(HardwareItem).filter(
            HardwareItem.nombre.ilike(f"%{nombre}%")
        ).all()

    def obtener_mas_caro_en_stock(self) -> Optional[HardwareItem]:
        """
        Obtiene el ítem más caro que tiene stock disponible.
        
        Returns:
            El ítem más caro con stock > 0, o None si no hay items
        """
        return self.db.query(HardwareItem).filter(
            HardwareItem.stock > 0
        ).order_by(HardwareItem.precio.desc()).first()

    def limpiar_tabla(self) -> None:
        """
        Elimina todos los registros de la tabla.
        ⚠️ Usar solo en testing.
        """
        self.db.query(HardwareItem).delete()
        self.db.commit()
