from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import Optional


class EstadoEjemplar(str, Enum):
    DISPONIBLE = "DISPONIBLE"
    PRESTADO = "PRESTADO"
    EXTRAVIADO = "EXTRAVIADO"


class EjemplarBase(BaseModel):
    codigo_inventario: str = Field(..., min_length=1)
    id_libro: str = Field(..., min_length=1)
    estado: EstadoEjemplar = EstadoEjemplar.DISPONIBLE


class EjemplarCreate(EjemplarBase):
    pass


class Ejemplar(EjemplarBase):
    model_config = ConfigDict(from_attributes=True)
