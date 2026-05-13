from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class NivelEstudiante(str, Enum):
    PREGRADO = "PREGRADO"
    POSGRADO = "POSGRADO"


class EstudianteBase(BaseModel):
    codigo_estudiante: str = Field(..., min_length=1)
    nombre: str = Field(..., min_length=1)
    nivel: NivelEstudiante


class EstudianteCreate(EstudianteBase):
    pass


class Estudiante(EstudianteBase):
    model_config = ConfigDict(from_attributes=True)
