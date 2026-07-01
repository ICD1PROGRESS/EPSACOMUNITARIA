import os
from sqlmodel import create_engine, Session, SQLModel
from contextlib import contextmanager
from pathlib import Path

# Obtener la URL de la base de datos desde el entorno
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/epsacol.db")

# Configurar argumentos de conexión SOLO para SQLite
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    # Asegurar que el directorio data/ existe
    Path("data").mkdir(exist_ok=True)
    connect_args = {"check_same_thread": False}

# Crear el engine con los argumentos condicionales
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def init_db():
    """Crea las tablas si no existen."""
    from . import models
    SQLModel.metadata.create_all(engine, checkfirst=True)

@contextmanager
def get_session():
    """Administrador de contexto para obtener una sesión de BD."""
    with Session(engine) as session:
        yield session
