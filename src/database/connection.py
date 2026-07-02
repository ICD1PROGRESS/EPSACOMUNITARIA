from sqlmodel import create_engine, Session, SQLModel
from contextlib import contextmanager

# Importamos la URL ya construida (absoluta si es SQLite)
from src.utils.config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def init_db():
    """Crea las tablas si no existen."""
    from . import models  # Importación local para evitar circularidad
    SQLModel.metadata.create_all(engine, checkfirst=True)

@contextmanager
def get_session():
    """Administrador de contexto para obtener una sesión de BD."""
    with Session(engine) as session:
        yield session
