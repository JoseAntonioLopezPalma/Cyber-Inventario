"""
Tests Unitarios con Pytest para Cyber-Inventory.

Cubre:
- Validaciones de creación
- Lógica de negocio
- Edge cases
- Parametrización de múltiples categorías
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import HardwareItem, HardwareCategory
from app.crud import HardwareRepository
from app.schemas import (
    HardwareItemCreate,
    HardwareItemUpdate,
    HardwareCategoryEnum,
)


# ==================== CONFIGURACIÓN DE FIXTURES ====================

@pytest.fixture(scope="function")
def db_session():
    """
    Crea una base de datos SQLite en memoria para cada test.
    Se limpia automáticamente después de cada test.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    
    session = SessionLocal()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def repository(db_session):
    """Proporciona una instancia del repositorio con sesión en memoria."""
    return HardwareRepository(db_session)


@pytest.fixture
def sample_item_data():
    """Datos de ejemplo para un ítem de hardware."""
    return HardwareItemCreate(
        nombre="Intel Core i9-13900K",
        categoria=HardwareCategoryEnum.MICROPROCESADORES,
        stock=10,
        precio=689.99,
    )


# ==================== TESTS DE VALIDACIÓN ====================

class TestValidacionesCreacion:
    """Tests para validar la creación de ítems."""

    def test_crear_item_valido(self, repository, sample_item_data):
        """Debe crear un ítem con datos válidos."""
        item = repository.crear(sample_item_data)
        
        assert item.id is not None
        assert item.nombre == "Intel Core i9-13900K"
        assert item.stock == 10
        assert item.precio == 689.99
        assert item.categoria == HardwareCategory.MICROPROCESADORES

    def test_precio_negativo_invalido(self):
        """No debe permitir crear ítem con precio negativo."""
        with pytest.raises(ValueError):
            HardwareItemCreate(
                nombre="GPU Defectuosa",
                categoria=HardwareCategoryEnum.TARJETAS_GRAFICAS,
                stock=5,
                precio=-100.0,
            )

    def test_precio_cero_invalido(self):
        """No debe permitir crear ítem con precio cero."""
        with pytest.raises(ValueError):
            HardwareItemCreate(
                nombre="GPU Gratis",
                categoria=HardwareCategoryEnum.TARJETAS_GRAFICAS,
                stock=5,
                precio=0.0,
            )

    def test_stock_negativo_invalido(self):
        """No debe permitir crear ítem con stock negativo."""
        with pytest.raises(ValueError):
            HardwareItemCreate(
                nombre="Discos Duros Negativa",
                categoria=HardwareCategoryEnum.DISCOS_DUROS,
                stock=-5,
                precio=100.0,
            )

    def test_stock_cero_valido(self, repository):
        """Debe permitir crear ítem con stock 0."""
        item_data = HardwareItemCreate(
            nombre="Discos Duros Nuevo",
            categoria=HardwareCategoryEnum.DISCOS_DUROS,
            stock=0,
            precio=50.0,
        )
        item = repository.crear(item_data)
        assert item.stock == 0

    def test_nombre_vacio_invalido(self):
        """No debe permitir nombre vacío o solo espacios."""
        with pytest.raises(ValueError):
            HardwareItemCreate(
                nombre="",
                categoria=HardwareCategoryEnum.MONITORES,
                stock=1,
                precio=300.0,
            )

        with pytest.raises(ValueError):
            HardwareItemCreate(
                nombre="   ",
                categoria=HardwareCategoryEnum.MONITORES,
                stock=1,
                precio=300.0,
            )

    def test_precio_muy_alto_invalido(self):
        """No debe permitir precios ilógicamente altos."""
        with pytest.raises(ValueError):
            HardwareItemCreate(
                nombre="GPU Legendaria",
                categoria=HardwareCategoryEnum.TARJETAS_GRAFICAS,
                stock=1,
                precio=2_000_000.0,
            )

    @pytest.mark.parametrize("precio", [0.01, 1.0, 100.0, 99999.99])
    def test_precios_validos_parametrizado(self, repository, precio):
        """Debe aceptar múltiples precios válidos."""
        item_data = HardwareItemCreate(
            nombre="Componente Genérico",
            categoria=HardwareCategoryEnum.GABINETES,
            stock=1,
            precio=precio,
        )
        item = repository.crear(item_data)
        assert item.precio == round(precio, 2)


# ==================== TESTS DE LÓGICA DE NEGOCIO ====================

class TestLogicaInventario:
    """Tests para la lógica de negocio de inventario."""

    def test_reducir_stock_exitosamente(self, repository, sample_item_data):
        """Debe reducir el stock correctamente."""
        item = repository.crear(sample_item_data)
        actualizado = repository.reducir_stock(item.id, 3)
        
        assert actualizado.stock == 7

    def test_reducir_stock_insuficiente(self, repository, sample_item_data):
        """No debe permitir reducir stock por debajo de 0."""
        item = repository.crear(sample_item_data)
        
        with pytest.raises(ValueError, match="Stock insuficiente"):
            repository.reducir_stock(item.id, 15)

    def test_reducir_stock_a_cero(self, repository, sample_item_data):
        """Debe permitir reducir stock exactamente a 0."""
        item = repository.crear(sample_item_data)
        actualizado = repository.reducir_stock(item.id, 10)
        
        assert actualizado.stock == 0

    def test_aumentar_stock_exitosamente(self, repository, sample_item_data):
        """Debe aumentar el stock correctamente."""
        item = repository.crear(sample_item_data)
        actualizado = repository.aumentar_stock(item.id, 5)
        
        assert actualizado.stock == 15

    def test_multiples_reducciones_stock(self, repository, sample_item_data):
        """Debe permitir múltiples operaciones de reducción."""
        item = repository.crear(sample_item_data)
        
        repository.reducir_stock(item.id, 2)
        item = repository.obtener_por_id(item.id)
        assert item.stock == 8
        
        repository.reducir_stock(item.id, 3)
        item = repository.obtener_por_id(item.id)
        assert item.stock == 5

    def test_multiples_aumentos_stock(self, repository, sample_item_data):
        """Debe permitir múltiples operaciones de aumento."""
        item = repository.crear(sample_item_data)
        
        repository.aumentar_stock(item.id, 10)
        item = repository.obtener_por_id(item.id)
        assert item.stock == 20
        
        repository.aumentar_stock(item.id, 5)
        item = repository.obtener_por_id(item.id)
        assert item.stock == 25

    def test_actualizar_precio(self, repository, sample_item_data):
        """Debe actualizar el precio correctamente."""
        item = repository.crear(sample_item_data)
        update = HardwareItemUpdate(precio=799.99)
        
        actualizado = repository.actualizar(item.id, update)
        assert actualizado.precio == 799.99

    def test_actualizar_nombre(self, repository, sample_item_data):
        """Debe actualizar el nombre correctamente."""
        item = repository.crear(sample_item_data)
        update = HardwareItemUpdate(nombre="Intel Core i9-14900K")
        
        actualizado = repository.actualizar(item.id, update)
        assert actualizado.nombre == "Intel Core i9-14900K"

    def test_actualizar_categoria(self, repository, sample_item_data):
        """Debe actualizar la categoría correctamente."""
        item = repository.crear(sample_item_data)
        update = HardwareItemUpdate(categoria=HardwareCategoryEnum.TARJETAS_GRAFICAS)
        
        actualizado = repository.actualizar(item.id, update)
        assert actualizado.categoria == HardwareCategory.TARJETAS_GRAFICAS


# ==================== TESTS DE EDGE CASES ====================

class TestEdgeCases:
    """Tests para casos límite y situaciones especiales."""

    def test_obtener_item_inexistente(self, repository):
        """Debe retornar None al obtener un ítem que no existe."""
        resultado = repository.obtener_por_id(999)
        assert resultado is None

    def test_actualizar_item_inexistente(self, repository):
        """Debe retornar None al actualizar un ítem inexistente."""
        update = HardwareItemUpdate(precio=100.0)
        resultado = repository.actualizar(999, update)
        assert resultado is None

    def test_eliminar_item_inexistente(self, repository):
        """Debe retornar False al eliminar un ítem inexistente."""
        resultado = repository.eliminar(999)
        assert resultado is False

    def test_reducir_stock_item_inexistente(self, repository):
        """Debe retornar None al reducir stock de ítem inexistente."""
        resultado = repository.reducir_stock(999, 1)
        assert resultado is None

    def test_aumentar_stock_item_inexistente(self, repository):
        """Debe retornar None al aumentar stock de ítem inexistente."""
        resultado = repository.aumentar_stock(999, 1)
        assert resultado is None

    def test_eliminar_item_existente(self, repository, sample_item_data):
        """Debe eliminar correctamente un ítem existente."""
        item = repository.crear(sample_item_data)
        resultado = repository.eliminar(item.id)
        
        assert resultado is True
        assert repository.obtener_por_id(item.id) is None

    def test_buscar_nombre_exacto(self, repository):
        """Debe encontrar ítem con búsqueda de nombre exacta."""
        item_data = HardwareItemCreate(
            nombre="RTX 4090",
            categoria=HardwareCategoryEnum.TARJETAS_GRAFICAS,
            stock=3,
            precio=1599.99,
        )
        created = repository.crear(item_data)
        
        resultados = repository.buscar_por_nombre("RTX 4090")
        assert len(resultados) == 1
        assert resultados[0].id == created.id

    def test_buscar_nombre_parcial(self, repository):
        """Debe encontrar ítems con búsqueda de nombre parcial."""
        items_data = [
            HardwareItemCreate(
                nombre="Intel Core i5",
                categoria=HardwareCategoryEnum.MICROPROCESADORES,
                stock=5,
                precio=300.0,
            ),
            HardwareItemCreate(
                nombre="Intel Core i7",
                categoria=HardwareCategoryEnum.MICROPROCESADORES,
                stock=5,
                precio=500.0,
            ),
            HardwareItemCreate(
                nombre="AMD Ryzen 5",
                categoria=HardwareCategoryEnum.MICROPROCESADORES,
                stock=5,
                precio=250.0,
            ),
        ]
        
        for item_data in items_data:
            repository.crear(item_data)
        
        resultados = repository.buscar_por_nombre("Intel")
        assert len(resultados) == 2

    def test_precio_redondeado_a_dos_decimales(self, repository):
        """Los precios deben redondearse a 2 decimales."""
        item_data = HardwareItemCreate(
            nombre="Monitor",
            categoria=HardwareCategoryEnum.MONITORES,
            stock=1,
            precio=199.999,
        )
        item = repository.crear(item_data)
        assert item.precio == 200.0


# ==================== TESTS PARAMETRIZADOS ====================

class TestParametrizacion:
    """Tests parametrizados para múltiples categorías de hardware."""

    @pytest.mark.parametrize("categoria", [
        HardwareCategoryEnum.MICROPROCESADORES,
        HardwareCategoryEnum.REFRIGERADORES_CPU,
        HardwareCategoryEnum.TARJETAS_GRAFICAS,
        HardwareCategoryEnum.MEMORIA_RAM,
        HardwareCategoryEnum.PLACAS_BASE,
        HardwareCategoryEnum.GABINETES,
        HardwareCategoryEnum.DISCOS_DUROS,
        HardwareCategoryEnum.UNIDADES_SSD,
        HardwareCategoryEnum.MONITORES,
        HardwareCategoryEnum.FUENTES_POWER,
    ])
    def test_crear_item_todas_categorias(self, repository, categoria):
        """Debe crear ítems en todas las categorías disponibles."""
        item_data = HardwareItemCreate(
            nombre=f"Componente {categoria}",
            categoria=categoria,
            stock=5,
            precio=100.0,
        )
        item = repository.crear(item_data)
        
        assert item.categoria.value == categoria.value
        assert item.id is not None

    @pytest.mark.parametrize("categoria,stock,precio", [
        (HardwareCategoryEnum.MICROPROCESADORES, 10, 689.99),
        (HardwareCategoryEnum.TARJETAS_GRAFICAS, 3, 1599.99),
        (HardwareCategoryEnum.MEMORIA_RAM, 20, 99.99),
        (HardwareCategoryEnum.DISCOS_DUROS, 15, 149.99),
        (HardwareCategoryEnum.UNIDADES_SSD, 25, 249.99),
        (HardwareCategoryEnum.MONITORES, 5, 349.99),
        (HardwareCategoryEnum.FUENTES_POWER, 12, 119.99),
    ])
    def test_crear_item_multiples_atributos(
        self, repository, categoria, stock, precio
    ):
        """Crea ítems con múltiples combinaciones de atributos."""
        item_data = HardwareItemCreate(
            nombre=f"Item {categoria}",
            categoria=categoria,
            stock=stock,
            precio=precio,
        )
        item = repository.crear(item_data)
        
        assert item.stock == stock
        assert item.precio == precio
        assert item.categoria.value == categoria.value

    @pytest.mark.parametrize("cantidad_a_reducir", [1, 2, 5, 10])
    def test_reducir_stock_multiples_cantidades(self, repository, cantidad_a_reducir):
        """Prueba reducción de stock con diferentes cantidades."""
        item_data = HardwareItemCreate(
            nombre="Stock Test Item",
            categoria=HardwareCategoryEnum.MEMORIA_RAM,
            stock=20,
            precio=75.0,
        )
        item = repository.crear(item_data)
        
        actualizado = repository.reducir_stock(item.id, cantidad_a_reducir)
        assert actualizado.stock == (20 - cantidad_a_reducir)


# ==================== TESTS DE REPOSITORIO ====================

class TestRepositorio:
    """Tests para métodos específicos del repositorio."""

    def test_obtener_total_items_vacio(self, repository):
        """Debe retornar 0 cuando no hay ítems."""
        total = repository.obtener_total_items()
        assert total == 0

    def test_obtener_total_items_con_datos(self, repository):
        """Debe contar correctamente los ítems."""
        items_data = [
            HardwareItemCreate(
                nombre=f"Item {i}",
                categoria=HardwareCategoryEnum.MICROPROCESADORES,
                stock=1,
                precio=100.0,
            )
            for i in range(5)
        ]
        
        for item_data in items_data:
            repository.crear(item_data)
        
        total = repository.obtener_total_items()
        assert total == 5

    def test_obtener_valor_total_inventario(self, repository):
        """Debe calcular el valor total del inventario."""
        items_data = [
            HardwareItemCreate(
                nombre="Item 1",
                categoria=HardwareCategoryEnum.MICROPROCESADORES,
                stock=2,
                precio=100.0,  # 2 * 100 = 200
            ),
            HardwareItemCreate(
                nombre="Item 2",
                categoria=HardwareCategoryEnum.TARJETAS_GRAFICAS,
                stock=3,
                precio=50.0,  # 3 * 50 = 150
            ),
        ]
        
        for item_data in items_data:
            repository.crear(item_data)
        
        valor_total = repository.obtener_valor_total_inventario()
        assert valor_total == 350.0

    def test_obtener_por_categoria(self, repository):
        """Debe obtener ítems por categoría."""
        cpus = HardwareItemCreate(
            nombre="CPU",
            categoria=HardwareCategoryEnum.MICROPROCESADORES,
            stock=5,
            precio=400.0,
        )
        gpu = HardwareItemCreate(
            nombre="GPU",
            categoria=HardwareCategoryEnum.TARJETAS_GRAFICAS,
            stock=3,
            precio=1000.0,
        )
        
        repository.crear(cpus)
        repository.crear(gpu)
        
        cpus_items = repository.obtener_por_categoria(
            HardwareCategoryEnum.MICROPROCESADORES
        )
        assert len(cpus_items) == 1
        assert cpus_items[0].nombre == "CPU"

    def test_obtener_stock_por_categoria(self, repository):
        """Debe contar el stock total por categoría."""
        items = [
            HardwareItemCreate(
                nombre="RAM 1",
                categoria=HardwareCategoryEnum.MEMORIA_RAM,
                stock=10,
                precio=50.0,
            ),
            HardwareItemCreate(
                nombre="RAM 2",
                categoria=HardwareCategoryEnum.MEMORIA_RAM,
                stock=15,
                precio=60.0,
            ),
        ]
        
        for item_data in items:
            repository.crear(item_data)
        
        stock_total = repository.obtener_stock_por_categoria(
            HardwareCategoryEnum.MEMORIA_RAM
        )
        assert stock_total == 25
