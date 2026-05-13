"""Tests para la funcionalidad de préstamos y reglas de negocio."""
import pytest
from datetime import datetime, timedelta
from app.services.biblioteca_service import BibliotecaException


# ============ RN1: Límite de préstamos ============

def test_rn1_pregrado_limite_3(setup_inicial):
    """
    RN1 - PREGRADO: máximo 3 préstamos activos.
    Este test verifica que no se permite un cuarto préstamo.
    """
    service = setup_inicial

    # Crear ejemplares adicionales para poder hacer múltiples préstamos
    service.registrar_ejemplar("EJ004", "LIB001")
    service.registrar_ejemplar("EJ005", "LIB001")

    # Primer préstamo: OK
    prestamo1 = service.solicitar_prestamo("EST001", "EJ001")
    assert prestamo1["estado"] == "VIGENTE"

    # Segundo préstamo: OK
    prestamo2 = service.solicitar_prestamo("EST001", "EJ002")
    assert prestamo2["estado"] == "VIGENTE"

    # Tercer préstamo: OK
    prestamo3 = service.solicitar_prestamo("EST001", "EJ004")
    assert prestamo3["estado"] == "VIGENTE"

    # Cuarto préstamo: DEBE FALLAR
    with pytest.raises(BibliotecaException) as exc_info:
        service.solicitar_prestamo("EST001", "EJ005")

    assert "limite_prestamos_alcanzado" in str(exc_info.value)
    assert exc_info.value.status_code == 409


def test_rn1_posgrado_limite_5(setup_inicial):
    """
    RN1 - POSGRADO: máximo 5 préstamos activos.
    """
    service = setup_inicial

    # Crear 5 ejemplares más
    for i in range(4, 9):
        service.registrar_ejemplar(f"EJ{i:03d}", "LIB001")

    # Registrar 5 préstamos para estudiante de posgrado
    for i in range(1, 6):
        prestamo = service.solicitar_prestamo("EST002", f"EJ{i:03d}")
        assert prestamo["estado"] == "VIGENTE"

    # El sexto préstamo debe fallar
    with pytest.raises(BibliotecaException) as exc_info:
        service.solicitar_prestamo("EST002", "EJ006")

    assert "limite_prestamos_alcanzado" in str(exc_info.value)
    assert exc_info.value.status_code == 409


# ============ RN4: Disponibilidad del ejemplar ============

def test_rn4_ejemplar_disponible(setup_inicial):
    """
    RN4: El ejemplar debe estar en estado DISPONIBLE para prestarse.
    """
    service = setup_inicial

    # Primer préstamo debe ser exitoso
    prestamo1 = service.solicitar_prestamo("EST001", "EJ001")
    assert prestamo1["estado"] == "VIGENTE"

    # Intentar prestar el mismo ejemplar debe fallar
    with pytest.raises(BibliotecaException) as exc_info:
        service.solicitar_prestamo("EST002", "EJ001")

    assert "ejemplar_no_disponible" in str(exc_info.value)
    assert exc_info.value.status_code == 409


def test_rn4_ejemplar_inexistente(setup_inicial):
    """
    RN4: No se puede prestar un ejemplar que no existe.
    """
    service = setup_inicial

    with pytest.raises(BibliotecaException, match="Ejemplar no encontrado"):
        service.solicitar_prestamo("EST001", "EJ_INEXISTENTE")


# ============ RN2: Bloqueo por vencidos ============

def test_rn2_bloqueado_por_vencido(setup_inicial):
    """
    RN2: No se permite nuevo préstamo si hay libros vencidos.
    """
    service = setup_inicial
    repo = service.repo

    # Crear un préstamo vencido
    prestamo_vencido = service.solicitar_prestamo("EST001", "EJ001")

    # Cambiar manualmente la fecha de vencimiento al pasado
    prestamo_obj = repo.get_prestamo(prestamo_vencido["id_prestamo"])
    prestamo_obj.fecha_vencimiento = datetime.now() - timedelta(days=1)

    # Marcar como vencido
    from app.models.prestamo import EstadoPrestamo
    repo.update_prestamo_estado(prestamo_vencido["id_prestamo"], EstadoPrestamo.VENCIDO)

    # Intentar prestar otro libro debe fallar
    with pytest.raises(BibliotecaException) as exc_info:
        service.solicitar_prestamo("EST001", "EJ002")

    assert "estudiante_con_vencimientos" in str(exc_info.value)
    assert exc_info.value.status_code == 403


# ============ RN3: Bloqueo por multas ============

def test_rn3_bloqueado_por_multas(setup_inicial):
    """
    RN3: No se permite nuevo préstamo si hay multas pendientes.
    """
    service = setup_inicial
    repo = service.repo

    # Crear un préstamo
    prestamo1 = service.solicitar_prestamo("EST001", "EJ001")

    # Modificar fecha de vencimiento para simular retraso
    prestamo_obj = repo.get_prestamo(prestamo1["id_prestamo"])
    prestamo_obj.fecha_vencimiento = datetime.now() - timedelta(days=3)

    # Registrar devolución con retraso (genera multa)
    resultado = service.registrar_devolucion(prestamo1["id_prestamo"])

    # Debería haber una multa generada
    multas = repo.get_multas_pendientes_estudiante("EST001")
    assert len(multas) > 0, "No se generó multa por retraso"

    # Intentar prestar otro libro debe fallar
    with pytest.raises(BibliotecaException) as exc_info:
        service.solicitar_prestamo("EST001", "EJ002")

    assert "multas_pendientes" in str(exc_info.value)
    assert exc_info.value.status_code == 403


# ============ RN5: Cálculo dinámico del plazo ============

def test_rn5_plazo_normal_15_dias(setup_inicial):
    """
    RN5: Libro normal (alta_demanda=False) tiene plazo de 15 días.
    """
    service = setup_inicial

    prestamo = service.solicitar_prestamo("EST001", "EJ001")

    fecha_prestamo = datetime.fromisoformat(prestamo["fecha_prestamo"])
    fecha_vencimiento = datetime.fromisoformat(prestamo["fecha_vencimiento"])

    dias_diferencia = (fecha_vencimiento.date() - fecha_prestamo.date()).days
    assert dias_diferencia == 15


def test_rn5_plazo_alta_demanda_3_dias(setup_inicial):
    """
    RN5: Libro alta_demanda=True tiene plazo de 3 días.
    """
    service = setup_inicial

    prestamo = service.solicitar_prestamo("EST001", "EJ003")  # LIB002 es alta demanda

    fecha_prestamo = datetime.fromisoformat(prestamo["fecha_prestamo"])
    fecha_vencimiento = datetime.fromisoformat(prestamo["fecha_vencimiento"])

    dias_diferencia = (fecha_vencimiento.date() - fecha_prestamo.date()).days
    assert dias_diferencia == 3


# ============ RN7: Cálculo de multas ============

def test_rn7_devolucion_sin_retraso(setup_inicial):
    """
    RN7: Devolución a tiempo no genera multa.
    """
    service = setup_inicial

    prestamo = service.solicitar_prestamo("EST001", "EJ001")
    resultado = service.registrar_devolucion(prestamo["id_prestamo"])

    assert resultado["estado"] == "DEVUELTO"
    assert resultado["multa"] is None


def test_rn7_devolucion_con_retraso_genera_multa(setup_inicial):
    """
    RN7: Devolución con retraso genera multa automática.
    Multa = días_retraso * 2000 pesos.
    """
    service = setup_inicial
    repo = service.repo

    prestamo = service.solicitar_prestamo("EST001", "EJ001")

    # Modificar fecha de vencimiento para simular retraso
    prestamo_obj = repo.get_prestamo(prestamo["id_prestamo"])
    prestamo_obj.fecha_vencimiento = datetime.now() - timedelta(days=5)

    resultado = service.registrar_devolucion(prestamo["id_prestamo"])

    assert resultado["estado"] == "DEVUELTO"
    assert resultado["multa"] is not None
    assert resultado["multa"]["dias_retraso"] == 5
    assert resultado["multa"]["monto"] == 10000  # 5 días * 2000


# ============ Historial y consultas ============

def test_historial_prestamos_estudiante(setup_inicial):
    """Test: obtener historial de préstamos de un estudiante."""
    service = setup_inicial

    # Hacer algunos préstamos
    p1 = service.solicitar_prestamo("EST001", "EJ001")
    p2 = service.solicitar_prestamo("EST001", "EJ002")

    # Obtener historial
    historial = service.obtener_historial_estudiante("EST001")

    assert len(historial) == 2
    assert historial[0]["id_prestamo"] == p1["id_prestamo"]
    assert historial[1]["id_prestamo"] == p2["id_prestamo"]


def test_obtener_prestamos_vigentes(setup_inicial):
    """Test: obtener todos los préstamos vigentes en el sistema."""
    service = setup_inicial

    p1 = service.solicitar_prestamo("EST001", "EJ001")
    p2 = service.solicitar_prestamo("EST002", "EJ002")

    vigentes = service.obtener_prestamos_vigentes()

    assert len(vigentes) == 2
