import pytest
from datetime import datetime
from app.repositories.memory import MemoryRepository
from app.services.biblioteca_service import BibliotecaService, BibliotecaException
from app.models.estudiante import NivelEstudiante


@pytest.fixture
def repo():
    """Fixture que proporciona un repositorio en memoria vacío."""
    return MemoryRepository()


@pytest.fixture
def service(repo):
    """Fixture que proporciona un servicio con repositorio en memoria."""
    return BibliotecaService(repo)


@pytest.fixture
def setup_inicial(service):
    """Fixture que configura datos iniciales para los tests."""
    # Registrar un libro normal
    service.registrar_libro(
        id_libro="LIB001",
        titulo="Clean Architecture",
        autor="Robert C. Martin",
        sala="A1",
        alta_demanda=False
    )

    # Registrar un libro de alta demanda
    service.registrar_libro(
        id_libro="LIB002",
        titulo="Design Patterns",
        autor="Gang of Four",
        sala="A2",
        alta_demanda=True
    )

    # Registrar ejemplares
    service.registrar_ejemplar("EJ001", "LIB001")
    service.registrar_ejemplar("EJ002", "LIB001")
    service.registrar_ejemplar("EJ003", "LIB002")

    # Registrar estudiantes
    service.registrar_estudiante("EST001", "Juan Pérez", "PREGRADO")
    service.registrar_estudiante("EST002", "María García", "POSGRADO")

    return service
