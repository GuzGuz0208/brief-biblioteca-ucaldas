"""Tests para la funcionalidad de libros y ejemplares."""
import pytest
from app.services.biblioteca_service import BibliotecaException


def test_crear_libro(service):
    """Test: crear un libro nuevo."""
    resultado = service.registrar_libro(
        id_libro="LIB001",
        titulo="Clean Code",
        autor="Robert C. Martin",
        sala="A1",
        alta_demanda=False
    )

    assert resultado["id_libro"] == "LIB001"
    assert resultado["titulo"] == "Clean Code"
    assert resultado["autor"] == "Robert C. Martin"
    assert resultado["sala"] == "A1"
    assert resultado["alta_demanda"] == False


def test_crear_libro_duplicado(service):
    """Test: no se puede crear un libro con ID duplicado."""
    service.registrar_libro("LIB001", "Libro 1", "Autor 1", "A1", False)

    with pytest.raises(BibliotecaException, match="El libro ya existe"):
        service.registrar_libro("LIB001", "Libro 2", "Autor 2", "A2", False)


def test_crear_ejemplar(service):
    """Test: crear un ejemplar de un libro."""
    service.registrar_libro("LIB001", "Libro 1", "Autor 1", "A1", False)

    resultado = service.registrar_ejemplar("EJ001", "LIB001")

    assert resultado["codigo_inventario"] == "EJ001"
    assert resultado["id_libro"] == "LIB001"
    assert resultado["estado"] == "DISPONIBLE"


def test_crear_ejemplar_libro_inexistente(service):
    """Test: no se puede crear ejemplar de libro que no existe."""
    with pytest.raises(BibliotecaException, match="El libro no existe"):
        service.registrar_ejemplar("EJ001", "LIB_INEXISTENTE")


def test_obtener_libros(setup_inicial):
    """Test: obtener todos los libros."""
    libros = setup_inicial.obtener_libros()

    assert len(libros) == 2
    assert libros[0]["id_libro"] == "LIB001"
    assert libros[1]["id_libro"] == "LIB002"


def test_obtener_libros_disponibles(setup_inicial):
    """Test: obtener libros con ejemplares disponibles."""
    libros = setup_inicial.obtener_libros(disponible=True)

    # Ambos libros deben tener ejemplares disponibles
    assert len(libros) == 2


def test_obtener_libro_detalle(setup_inicial):
    """Test: obtener detalles de un libro específico."""
    libro = setup_inicial.obtener_libro("LIB001")

    assert libro["id_libro"] == "LIB001"
    assert libro["titulo"] == "Clean Architecture"
    assert len(libro["ejemplares"]) == 2


def test_obtener_libro_inexistente(setup_inicial):
    """Test: obtener libro que no existe."""
    with pytest.raises(BibliotecaException, match="Libro no encontrado"):
        setup_inicial.obtener_libro("LIB_INEXISTENTE")
