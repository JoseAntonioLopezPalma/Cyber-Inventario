"""
Configuración de Pytest (conftest.py)
Define fixtures compartidas y configuración global de tests.
"""

import pytest


def pytest_configure(config):
    """Ejecutado antes de descubrir y ejecutar tests."""
    config.addinivalue_line(
        "markers", "parametrize: marca para tests parametrizados"
    )


@pytest.fixture(autouse=True)
def reset_imports():
    """
    Limpia imports entre tests para evitar state compartido.
    Se ejecuta automáticamente antes de cada test.
    """
    yield
    import sys
    # Aquí se pueden agregar limpiezas adicionales si es necesario
