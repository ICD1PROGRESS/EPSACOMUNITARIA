from sqlmodel import SQLModel, Field, Relationship
from datetime import date, datetime
from typing import Optional, List

class Deuda(SQLModel, table=True):
    __tablename__ = "deudas"
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    epsa_id: int = Field(foreign_key="epsas.id")
    usuario_id: int = Field(foreign_key="usuarios.id")
    nro_deuda: str
    periodo: str
    consumo_m3: Optional[float] = None
    monto: float
    estado: str = Field(default="PENDIENTE")
    fecha_vencimiento: Optional[date] = None

    usuario: "Usuario" = Relationship(back_populates="deudas")
    epsa: "EPSA" = Relationship(back_populates="deudas")

class EPSA(SQLModel, table=True):
    __tablename__ = "epsas"
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True)
    ciudad: str
    created_at: datetime = Field(default_factory=datetime.now)

    # Usar rutas completas
    usuarios: List["Usuario"] = Relationship(back_populates="epsa")
    tarifas: List["Tarifa"] = Relationship(back_populates="epsa")
    lecturas: List["Lectura"] = Relationship(back_populates="epsa")
    pagos: List["Pago"] = Relationship(back_populates="epsa")
    configuracion: Optional["ConfiguracionEPSA"] = Relationship(back_populates="epsa")
    deudas: List["Deuda"] = Relationship(back_populates="epsa")

# ---------- Modelo ConfiguracionEPSA (antes de Usuario porque depende de EPSA) ----------
class ConfiguracionEPSA(SQLModel, table=True):
    __tablename__ = "configuracion_epsa"
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    epsa_id: int = Field(foreign_key="epsas.id", unique=True)
    logo_path: Optional[str] = None
    membrete_texto: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    sitio_web: Optional[str] = None

    epsa: EPSA = Relationship(back_populates="configuracion")

class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    epsa_id: int = Field(foreign_key="epsas.id")
    codigo: str = Field(index=True)
    nombre: str
    ci: str
    zona: str
    nro_medidor: str
    categoria: str = Field(default="RESIDENCIAL")
    saldo_actual: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.now)

    epsa: EPSA = Relationship(back_populates="usuarios")
    lecturas: List["Lectura"] = Relationship(back_populates="usuario")
    pagos: List["Pago"] = Relationship(back_populates="usuario")
    deudas: List["Deuda"] = Relationship(back_populates="usuario")

class Tarifa(SQLModel, table=True):
    __tablename__ = "tarifas"
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    epsa_id: int = Field(foreign_key="epsas.id")
    rango_inicio: float
    rango_fin: Optional[float] = None
    precio_unitario: float
    cargo_fijo: float = 0.0
    orden: int = 0

    epsa: EPSA = Relationship(back_populates="tarifas")

class Lectura(SQLModel, table=True):
    __tablename__ = "lecturas"
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    epsa_id: int = Field(foreign_key="epsas.id")
    usuario_id: int = Field(foreign_key="usuarios.id")
    periodo: str
    lectura_anterior: float
    lectura_actual: float
    consumo_m3: float
    fecha_toma: date
    importe_calculado: float = 0.0

    usuario: Usuario = Relationship(back_populates="lecturas")
    epsa: EPSA = Relationship(back_populates="lecturas")

# ---------- Modelo Pago ----------
class Pago(SQLModel, table=True):
    __tablename__ = "pagos"
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    epsa_id: int = Field(foreign_key="epsas.id")
    usuario_id: int = Field(foreign_key="usuarios.id")
    fecha_pago: date
    monto: float
    periodo: str
    recibo_nro: str
    created_at: datetime = Field(default_factory=datetime.now)

    usuario: Usuario = Relationship(back_populates="pagos")
    epsa: EPSA = Relationship(back_populates="pagos")

class Periodo(SQLModel, table=True):
    __tablename__ = "periodos"
    __table_args__ = {'extend_existing': True}
    id: int = Field(default=None, primary_key=True)
    epsa_id: int = Field(foreign_key="epsas.id")
    nombre: str  # Ej: "MARZO - ABRIL 2024"
    fecha_inicio: date
    fecha_fin: date
    activo: bool = Field(default=True)
    cerrado: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)