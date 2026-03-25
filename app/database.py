"""
Configuración de la base de datos SQLite con SQLAlchemy.
Sigue principios SOLID con inyección de dependencias.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
import os

# Configuración de la base de datos
DATABASE_URL = "sqlite:///./warehouse.db"

# Pool estático para SQLite (mejor para testing)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Factory para crear sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base para todos los modelos
Base = declarative_base()


def get_db():
    """Dependency injection para obtener sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa la base de datos creando todas las tablas."""
    Base.metadata.create_all(bind=engine)
