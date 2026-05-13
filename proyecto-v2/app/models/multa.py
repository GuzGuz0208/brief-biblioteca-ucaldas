from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class EstadoMulta(str, Enum):
    PENDIENTE = "PENDIENTE"
    PAGADA = "PAGADA"


class MultaBase(BaseModel):
    id_prestamo: str = Field(..., min_length=1)
    codigo_estudiante: str = Field(..., min_length=1)
    dias_retraso: int = Field(..., ge=0)
    monto_total: int = Field(..., ge=0)
    estado: EstadoMulta = EstadoMulta.PENDIENTE


class MultaCreate(MultaBase):
    pass


class Multa(MultaBase):
    id_multa: str
    model_config = ConfigDict(from_attributes=True)
