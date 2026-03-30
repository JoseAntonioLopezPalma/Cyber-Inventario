"""
Tests de Integración para los endpoints FastAPI.
Prueba los endpoints a través de HTTP simulado (TestClient).
"""

import pytest
from starlette.testclient import TestClient
from starlette.applications import Starlette
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


@pytest.fixture(scope="function")
def test_db():
    """
    Crea una base de datos SQLite en memoria para pruebas de integración.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def client(test_db):
    """Cliente TestClient para probar endpoints."""
    return TestClient(app)


class TestEndpointsCreacion:
    """Tests para endpoints de creación."""

    def test_crear_item_exitoso(self, client):
        """POST /api/items debe crear un ítem exitosamente."""
        response = client.post(
            "/api/items",
            json={
                "nombre": "Intel Core i9-13900K",
                "categoria": "Microprocesadores",
                "stock": 10,
                "precio": 689.99,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Intel Core i9-13900K"
        assert data["stock"] == 10
        assert data["precio"] == 689.99
        assert "id" in data
        assert "fecha_entrada" in data

    def test_crear_item_precio_negativo(self, client):
        """POST /api/items debe rechazar precio negativo."""
        response = client.post(
            "/api/items",
            json={
                "nombre": "GPU Defectuosa",
                "categoria": "Tarjetas Gráficas",
                "stock": 5,
                "precio": -100.0,
            },
        )

        assert response.status_code == 422  # Validation error

    def test_crear_item_stock_negativo(self, client):
        """POST /api/items debe rechazar stock negativo."""
        response = client.post(
            "/api/items",
            json={
                "nombre": "Memoria Negativa",
                "categoria": "Memoria RAM",
                "stock": -5,
                "precio": 100.0,
            },
        )

        assert response.status_code == 422  # Validation error

    def test_crear_item_nombre_vacio(self, client):
        """POST /api/items debe rechazar nombre vacío."""
        response = client.post(
            "/api/items",
            json={
                "nombre": "",
                "categoria": "Monitores",
                "stock": 1,
                "precio": 300.0,
            },
        )

        assert response.status_code == 422  # Validation error


class TestEndpointsLectura:
    """Tests para endpoints de lectura."""

    def test_obtener_item_por_id_existente(self, client):
        """GET /api/items/{id} debe retornar el ítem."""
        # Crear un ítem primero
        create_response = client.post(
            "/api/items",
            json={
                "nombre": "Test Item",
                "categoria": "Monitores",
                "stock": 1,
                "precio": 50.0,
            },
        )
        item_id = create_response.json()["id"]

        # Obtener el ítem
        response = client.get(f"/api/items/{item_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["nombre"] == "Test Item"

    def test_obtener_item_por_id_inexistente(self, client):
        """GET /api/items/999 debe retornar 404."""
        response = client.get("/api/items/999")

        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"].lower()

    def test_listar_items_vacio(self, client):
        """GET /api/items debe retornar lista vacía."""
        response = client.get("/api/items")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["precio_total_inventario"] == 0.0

    def test_listar_items_con_resultados(self, client):
        """GET /api/items debe retornar ítems creados."""
        # Crear 2 ítems
        for i in range(2):
            client.post(
                "/api/items",
                json={
                    "nombre": f"Item {i}",
                    "categoria": "Memoria RAM",
                    "stock": 5,
                    "precio": 100.0,
                },
            )

        response = client.get("/api/items")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["precio_total_inventario"] == 1000.0  # 5 * 100 * 2

    def test_listar_items_con_paginacion(self, client):
        """GET /api/items?skip=X&limit=Y debe aplicar paginación."""
        # Crear 5 ítems
        for i in range(5):
            client.post(
                "/api/items",
                json={
                    "nombre": f"Item {i}",
                    "categoria": "Monitores",
                    "stock": 1,
                    "precio": 300.0,
                },
            )

        # Obtener con paginación
        response = client.get("/api/items?skip=2&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2

    def test_listar_items_por_categoria(self, client):
        """GET /api/items?categoria=X debe filtrar por categoría."""
        # Crear ítems de diferentes categorías
        client.post(
            "/api/items",
            json={
                "nombre": "CPU",
                "categoria": "Microprocesadores",
                "stock": 5,
                "precio": 400.0,
            },
        )
        client.post(
            "/api/items",
            json={
                "nombre": "GPU",
                "categoria": "Tarjetas Gráficas",
                "stock": 3,
                "precio": 1000.0,
            },
        )

        response = client.get("/api/items?categoria=Microprocesadores")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["nombre"] == "CPU"


class TestEndpointsActualizacion:
    """Tests para endpoints de actualización."""

    def test_actualizar_item_exitoso(self, client):
        """PUT /api/items/{id} debe actualizar el ítem."""
        # Crear ítem
        create_response = client.post(
            "/api/items",
            json={
                "nombre": "Original",
                "categoria": "Monitores",
                "stock": 10,
                "precio": 50.0,
            },
        )
        item_id = create_response.json()["id"]

        # Actualizar
        response = client.put(
            f"/api/items/{item_id}",
            json={
                "nombre": "Actualizado",
                "precio": 75.0,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Actualizado"
        assert data["precio"] == 75.0
        assert data["stock"] == 10  # No cambió

    def test_actualizar_item_inexistente(self, client):
        """PUT /api/items/999 debe retornar 404."""
        response = client.put(
            "/api/items/999",
            json={"precio": 100.0},
        )

        assert response.status_code == 404


class TestEndpointsEliminacion:
    """Tests para endpoints de eliminación."""

    def test_eliminar_item_exitoso(self, client):
        """DELETE /api/items/{id} debe eliminar el ítem."""
        # Crear ítem
        create_response = client.post(
            "/api/items",
            json={
                "nombre": "Para Eliminar",
                "categoria": "Monitores",
                "stock": 1,
                "precio": 30.0,
            },
        )
        item_id = create_response.json()["id"]

        # Eliminar
        response = client.delete(f"/api/items/{item_id}")

        assert response.status_code == 204

        # Verificar que se eliminó
        get_response = client.get(f"/api/items/{item_id}")
        assert get_response.status_code == 404

    def test_eliminar_item_inexistente(self, client):
        """DELETE /api/items/999 debe retornar 404."""
        response = client.delete("/api/items/999")

        assert response.status_code == 404


class TestOperacionesInventario:
    """Tests para operaciones de reducción/aumento de stock."""

    def test_reducir_stock_exitoso(self, client):
        """POST /api/items/{id}/reducir-stock debe reducir el stock."""
        # Crear ítem
        create_response = client.post(
            "/api/items",
            json={
                "nombre": "Stock Item",
                "categoria": "Memoria RAM",
                "stock": 20,
                "precio": 100.0,
            },
        )
        item_id = create_response.json()["id"]

        # Reducir stock
        response = client.post(
            f"/api/items/{item_id}/reducir-stock?cantidad=5"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["stock"] == 15

    def test_reducir_stock_insuficiente(self, client):
        """POST /api/items/{id}/reducir-stock debe fallar si no hay stock."""
        # Crear ítem con stock bajo
        create_response = client.post(
            "/api/items",
            json={
                "nombre": "Low Stock",
                "categoria": "Monitores",
                "stock": 5,
                "precio": 20.0,
            },
        )
        item_id = create_response.json()["id"]

        # Intentar reducir más del disponible
        response = client.post(
            f"/api/items/{item_id}/reducir-stock?cantidad=10"
        )

        assert response.status_code == 400
        assert "Stock insuficiente" in response.json()["detail"]

    def test_aumentar_stock_exitoso(self, client):
        """POST /api/items/{id}/aumentar-stock debe aumentar el stock."""
        # Crear ítem
        create_response = client.post(
            "/api/items",
            json={
                "nombre": "Increase Item",
                "categoria": "Monitores",
                "stock": 10,
                "precio": 50.0,
            },
        )
        item_id = create_response.json()["id"]

        # Aumentar stock
        response = client.post(
            f"/api/items/{item_id}/aumentar-stock?cantidad=15"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["stock"] == 25


class TestBusqueda:
    """Tests para endpoints de búsqueda."""

    def test_buscar_por_nombre(self, client):
        """GET /api/buscar?q=X debe buscar por nombre."""
        # Crear ítems
        client.post(
            "/api/items",
            json={
                "nombre": "Intel Core i5",
                "categoria": "Microprocesadores",
                "stock": 5,
                "precio": 300.0,
            },
        )
        client.post(
            "/api/items",
            json={
                "nombre": "AMD Ryzen 5",
                "categoria": "Microprocesadores",
                "stock": 3,
                "precio": 250.0,
            },
        )

        response = client.get("/api/buscar?q=Intel")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["nombre"] == "Intel Core i5"

    def test_obtener_por_categoria_endpoint(self, client):
        """GET /api/categorias/{categoria} debe retornar todos los ítems."""
        # Crear ítems
        client.post(
            "/api/items",
            json={
                "nombre": "GPU 1",
                "categoria": "Tarjetas Gráficas",
                "stock": 2,
                "precio": 1500.0,
            },
        )
        client.post(
            "/api/items",
            json={
                "nombre": "GPU 2",
                "categoria": "Tarjetas Gráficas",
                "stock": 1,
                "precio": 2000.0,
            },
        )

        response = client.get("/api/categorias/Tarjetas Gráficas")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2


class TestEstadisticas:
    """Tests para endpoint de estadísticas."""

    def test_obtener_estadisticas(self, client):
        """GET /api/estadisticas debe retornar estadísticas."""
        # Crear ítems
        client.post(
            "/api/items",
            json={
                "nombre": "Item 1",
                "categoria": "Microprocesadores",
                "stock": 5,
                "precio": 100.0,
            },
        )
        client.post(
            "/api/items",
            json={
                "nombre": "Item 2",
                "categoria": "Memoria RAM",
                "stock": 10,
                "precio": 50.0,
            },
        )

        response = client.get("/api/estadisticas")

        assert response.status_code == 200
        data = response.json()
        assert data["total_items"] == 2
        assert data["valor_total_inventario"] == 1000.0  # 5*100 + 10*50
        assert data["moneda"] == "USD"


class TestHealthCheck:
    """Tests para endpoint de health check."""

    def test_health_check(self, client):
        """GET /health debe retornar estado ok."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Cyber-Inventory"
