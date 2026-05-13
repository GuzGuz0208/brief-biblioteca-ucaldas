from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class EstadoReserva(str, Enum):
    ACTIVA = "ACTIVA"
    CANCELADA = "CANCELADA"
    COMPLETADA = "COMPLETADA"


class ReservaBase(BaseModel):
    codigo_estudiante: str = Field(..., min_length=1)
    id_libro: str = Field(..., min_length=1)
    estado: EstadoReserva = EstadoReserva.ACTIVA


class ReservaCreate(ReservaBase):
    pass


class Reserva(ReservaBase):
    id_reserva: str
    model_config = ConfigDict(from_attributes=True)
