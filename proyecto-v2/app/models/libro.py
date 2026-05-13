from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class LibroBase(BaseModel):
    titulo: str = Field(..., min_length=1)
    autor: str = Field(..., min_length=1)
    sala: str = Field(..., min_length=1)
    alta_demanda: bool


class LibroCreate(LibroBase):
    id_libro: str = Field(..., min_length=1)


class Libro(LibroBase):
    id_libro: str
    model_config = ConfigDict(from_attributes=True)
