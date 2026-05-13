from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional


class EstadoPrestamo(str, Enum):
    VIGENTE = "VIGENTE"
    VENCIDO = "VENCIDO"
    DEVUELTO = "DEVUELTO"


class PrestamoBase(BaseModel):
    codigo_inventario: str = Field(..., min_length=1)
    codigo_estudiante: str = Field(..., min_length=1)


class PrestamoCreate(PrestamoBase):
    pass


class Prestamo(PrestamoBase):
    id_prestamo: str
    fecha_prestamo: datetime
    fecha_vencimiento: datetime
    fecha_devolucion: Optional[datetime] = None
    estado: EstadoPrestamo
    renovaciones: int = 0
    model_config = ConfigDict(from_attributes=True)
