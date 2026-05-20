from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.services.biblioteca_service import BibliotecaService, BibliotecaException
from app.repositories.sqlite import SqliteRepository

# Modelos para recibir bodies
from app.models.libro import LibroCreate
from app.models.ejemplar import EjemplarCreate
from app.models.estudiante import EstudianteCreate
from app.models.prestamo import PrestamoCreate
from app.models.reserva import ReservaCreate

# Inicializar repositorio global (creará un archivo biblioteca.db automáticamente)
repo = SqliteRepository()
service = BibliotecaService(repo)

router = APIRouter(prefix="/api/v1", tags=["biblioteca"])


# ============ LIBROS ============

@router.post("/libros", status_code=201)
def crear_libro(libro: LibroCreate):
    """Registra un nuevo libro en el catálogo (body JSON)."""
    try:
        return service.registrar_libro(libro.id_libro, libro.titulo, libro.autor, libro.sala, libro.alta_demanda)
    except BibliotecaException as e:
        # Mapear códigos de negocio: 403 -> 409, 404 -> 404, else usar status si viene
        status = getattr(e, 'status_code', None)
        if status == 404:
            code = 404
        elif status == 403:
            code = 409
        else:
            code = status or 400

        # Construir mensaje claro en formato JSON: HTTPException devuelve {"detail": ...}
        msg = e.message if hasattr(e, 'message') else str(e)
        if getattr(e, 'data', None):
            # Incluir datos adicionales en el mensaje
            msg = f"{msg} | detalles: {e.data}"

        raise HTTPException(status_code=code, detail=msg) from e


@router.post("/ejemplares", status_code=201)
def crear_ejemplar(ejemplar: EjemplarCreate):
    """Registra un nuevo ejemplar (body JSON)."""
    try:
        return service.registrar_ejemplar(ejemplar.codigo_inventario, ejemplar.id_libro)
    except BibliotecaException as e:
        status = getattr(e, 'status_code', None)
        if status == 404:
            code = 404
        elif status == 403:
            code = 409
        else:
            code = status or 400

        msg = e.message if hasattr(e, 'message') else str(e)
        if getattr(e, 'data', None):
            msg = f"{msg} | detalles: {e.data}"

        raise HTTPException(status_code=code, detail=msg) from e


@router.get("/libros")
def obtener_libros(disponible: Optional[bool] = Query(None)):
    """
    Obtiene todos los libros del catálogo.

    Query params:
    - disponible=true: solo libros con al menos un ejemplar disponible
    - disponible=false: solo libros sin ejemplares disponibles
    """
    return service.obtener_libros(disponible)


@router.get("/libros/{id_libro}")
def obtener_libro(id_libro: str):
    """Obtiene el detalle de un libro específico."""
    try:
        return service.obtener_libro(id_libro)
    except BibliotecaException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# ============ ESTUDIANTES ============

@router.post("/estudiantes", status_code=201)
def crear_estudiante(estudiante: EstudianteCreate):
    """Registra un nuevo estudiante (body JSON)."""
    try:
        # Enviar el valor del enum (ej. "PREGRADO")
        nivel_val = estudiante.nivel.value if hasattr(estudiante.nivel, 'value') else estudiante.nivel
        return service.registrar_estudiante(estudiante.codigo_estudiante, estudiante.nombre, nivel_val)
    except BibliotecaException as e:
        status = getattr(e, 'status_code', None)
        if status == 404:
            code = 404
        elif status == 403:
            code = 409
        else:
            code = status or 400

        msg = e.message if hasattr(e, 'message') else str(e)
        if getattr(e, 'data', None):
            msg = f"{msg} | detalles: {e.data}"

        raise HTTPException(status_code=code, detail=msg) from e


@router.get("/estudiantes/{codigo_estudiante}/historial")
def obtener_historial_estudiante(codigo_estudiante: str):
    """Obtiene el historial completo de préstamos de un estudiante."""
    try:
        return service.obtener_historial_estudiante(codigo_estudiante)
    except BibliotecaException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# ============ PRÉSTAMOS ============

@router.post("/prestamos", status_code=201)
def solicitar_prestamo(peticion: PrestamoCreate):
    """
    Solicita un préstamo.

    Implementa reglas:
    - RN1: Límite de préstamos por tipo de estudiante
    - RN2: Bloqueo por préstamos vencidos
    - RN3: Bloqueo por multas pendientes
    - RN4: Disponibilidad del ejemplar
    - RN5: Cálculo dinámico del plazo de vencimiento
    """
    try:
        return service.solicitar_prestamo(peticion.codigo_estudiante, peticion.codigo_inventario)
    except BibliotecaException as e:
        status = getattr(e, 'status_code', None)
        if status == 404:
            code = 404
        elif status == 403:
            # Normalizar bloqueos de negocio a 409 Conflict
            code = 409
        else:
            code = status or 400

        msg = e.message if hasattr(e, 'message') else str(e)
        if getattr(e, 'data', None):
            msg = f"{msg} | detalles: {e.data}"

        raise HTTPException(status_code=code, detail=msg) from e


@router.post("/prestamos/{id_prestamo}/devolucion", status_code=200)
def registrar_devolucion(id_prestamo: str):
    """
    Registra la devolución de un libro.

    Implementa regla:
    - RN7: Cálculo y generación automática de multas
    """
    try:
        return service.registrar_devolucion(id_prestamo)
    except BibliotecaException as e:
        status = getattr(e, 'status_code', None)
        code = status or 400
        msg = e.message if hasattr(e, 'message') else str(e)
        if getattr(e, 'data', None):
            msg = f"{msg} | detalles: {e.data}"
        raise HTTPException(status_code=code, detail=msg) from e


@router.post("/prestamos/{id_prestamo}/renovacion", status_code=200)
def renovar_prestamo(id_prestamo: str):
    """
    Renueva un préstamo.

    Implementa regla:
    - RN6: Restricción de renovación por lista de espera
    """
    try:
        return service.renovar_prestamo(id_prestamo)
    except BibliotecaException as e:
        status = getattr(e, 'status_code', None)
        if status == 404:
            code = 404
        elif status == 403:
            code = 409
        else:
            code = status or 400

        msg = e.message if hasattr(e, 'message') else str(e)
        if getattr(e, 'data', None):
            msg = f"{msg} | detalles: {e.data}"

        raise HTTPException(status_code=code, detail=msg) from e


@router.get("/prestamos/vigentes")
def obtener_prestamos_vigentes():
    """Obtiene todos los préstamos vigentes en el sistema."""
    return service.obtener_prestamos_vigentes()


@router.get("/prestamos/vencidos")
def obtener_prestamos_vencidos():
    """Obtiene todos los préstamos vencidos en el sistema."""
    return service.obtener_prestamos_vencidos()


# ============ MULTAS ============

@router.post("/multas/{id_multa}/pago", status_code=200)
def pagar_multa(id_multa: str):
    """Registra el pago de una multa (Decisión D3)."""
    try:
        return service.pagar_multa(id_multa)
    except BibliotecaException as e:
        status = getattr(e, 'status_code', None)
        code = status or 400
        msg = e.message if hasattr(e, 'message') else str(e)
        if getattr(e, 'data', None):
            msg = f"{msg} | detalles: {e.data}"
        raise HTTPException(status_code=code, detail=msg) from e


# ============ RESERVAS ============

@router.post("/reservas", status_code=201)
def crear_reserva(reserva: ReservaCreate):
    """Crea una reserva para un libro (body JSON, Decisión D2)."""
    try:
        return service.crear_reserva(reserva.codigo_estudiante, reserva.id_libro)
    except BibliotecaException as e:
        status = getattr(e, 'status_code', None)
        if status == 404:
            code = 404
        elif status == 403:
            code = 409
        else:
            code = status or 400

        msg = e.message if hasattr(e, 'message') else str(e)
        if getattr(e, 'data', None):
            msg = f"{msg} | detalles: {e.data}"

        raise HTTPException(status_code=code, detail=msg) from e
