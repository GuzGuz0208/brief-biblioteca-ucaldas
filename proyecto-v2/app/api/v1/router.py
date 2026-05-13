from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.services.biblioteca_service import BibliotecaService, BibliotecaException
from app.repositories.memory import MemoryRepository

# Inicializar repositorio global
repo = MemoryRepository()
service = BibliotecaService(repo)

router = APIRouter(prefix="/api/v1", tags=["biblioteca"])


# ============ LIBROS ============

@router.post("/libros", status_code=201)
def crear_libro(
    id_libro: str,
    titulo: str,
    autor: str,
    sala: str,
    alta_demanda: bool
):
    """Registra un nuevo libro en el catálogo."""
    try:
        return service.registrar_libro(id_libro, titulo, autor, sala, alta_demanda)
    except BibliotecaException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ejemplares", status_code=201)
def crear_ejemplar(
    codigo_inventario: str,
    id_libro: str
):
    """Registra un nuevo ejemplar."""
    try:
        return service.registrar_ejemplar(codigo_inventario, id_libro)
    except BibliotecaException as e:
        raise HTTPException(status_code=400, detail=str(e))


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
        raise HTTPException(status_code=404, detail=str(e))


# ============ ESTUDIANTES ============

@router.post("/estudiantes", status_code=201)
def crear_estudiante(
    codigo_estudiante: str,
    nombre: str,
    nivel: str  # "PREGRADO" o "POSGRADO"
):
    """Registra un nuevo estudiante."""
    try:
        return service.registrar_estudiante(codigo_estudiante, nombre, nivel)
    except BibliotecaException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/estudiantes/{codigo_estudiante}/historial")
def obtener_historial_estudiante(codigo_estudiante: str):
    """Obtiene el historial completo de préstamos de un estudiante."""
    try:
        return service.obtener_historial_estudiante(codigo_estudiante)
    except BibliotecaException as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============ PRÉSTAMOS ============

@router.post("/prestamos", status_code=201)
def solicitar_prestamo(
    codigo_estudiante: str,
    codigo_inventario: str
):
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
        return service.solicitar_prestamo(codigo_estudiante, codigo_inventario)
    except BibliotecaException as e:
        if hasattr(e, 'status_code') and e.status_code:
            status = e.status_code
        else:
            status = 400

        # Construir respuesta de error
        detail = {"error": str(e)}
        if hasattr(e, 'data') and e.data:
            detail.update(e.data)

        raise HTTPException(status_code=status, detail=detail)


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
        raise HTTPException(status_code=404, detail=str(e))


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
        if hasattr(e, 'status_code') and e.status_code:
            status = e.status_code
        else:
            status = 400

        detail = {"error": str(e)}
        if hasattr(e, 'data') and e.data:
            detail.update(e.data)

        raise HTTPException(status_code=status, detail=detail)


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
        raise HTTPException(status_code=404, detail=str(e))


# ============ RESERVAS ============

@router.post("/reservas", status_code=201)
def crear_reserva(
    codigo_estudiante: str,
    id_libro: str
):
    """Crea una reserva para un libro (Decisión D2)."""
    try:
        return service.crear_reserva(codigo_estudiante, id_libro)
    except BibliotecaException as e:
        raise HTTPException(status_code=404, detail=str(e))
