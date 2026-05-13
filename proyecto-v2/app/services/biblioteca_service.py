from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from app.repositories.memory import MemoryRepository
from app.models.libro import LibroCreate
from app.models.ejemplar import EjemplarCreate, EstadoEjemplar
from app.models.estudiante import EstudianteCreate, NivelEstudiante
from app.models.prestamo import PrestamoCreate, Prestamo, EstadoPrestamo
from app.models.multa import MultaCreate
from app.models.reserva import ReservaCreate


class BibliotecaException(Exception):
    """Excepción base para errores de negocio."""

    def __init__(self, message: str, status_code: int = 400, data: dict = None):
        self.message = message
        self.status_code = status_code
        self.data = data or {}
        super().__init__(self.message)


class BibliotecaService:
    """Service que implementa toda la lógica de negocio de la biblioteca."""

    def __init__(self, repository: MemoryRepository):
        self.repo = repository

    # ============ LIBROS ============

    def registrar_libro(self, id_libro: str, titulo: str, autor: str, sala: str, alta_demanda: bool) -> Dict:
        """Registra un nuevo libro en el catálogo."""
        if self.repo.get_libro(id_libro):
            raise BibliotecaException("El libro ya existe")

        libro_create = LibroCreate(
            id_libro=id_libro,
            titulo=titulo,
            autor=autor,
            sala=sala,
            alta_demanda=alta_demanda
        )
        libro = self.repo.create_libro(libro_create)
        return {
            "id_libro": libro.id_libro,
            "titulo": libro.titulo,
            "autor": libro.autor,
            "sala": libro.sala,
            "alta_demanda": libro.alta_demanda
        }

    def registrar_ejemplar(self, codigo_inventario: str, id_libro: str) -> Dict:
        """Registra un ejemplar de un libro."""
        # Verificar que el libro exista
        libro = self.repo.get_libro(id_libro)
        if not libro:
            raise BibliotecaException("El libro no existe")

        if self.repo.get_ejemplar(codigo_inventario):
            raise BibliotecaException("El ejemplar ya existe")

        ejemplar_create = EjemplarCreate(
            codigo_inventario=codigo_inventario,
            id_libro=id_libro,
            estado=EstadoEjemplar.DISPONIBLE
        )
        ejemplar = self.repo.create_ejemplar(ejemplar_create)
        return {
            "codigo_inventario": ejemplar.codigo_inventario,
            "id_libro": ejemplar.id_libro,
            "estado": ejemplar.estado
        }

    def obtener_libros(self, disponible: Optional[bool] = None) -> List[Dict]:
        """Obtiene todos los libros del catálogo con filtro opcional de disponibilidad."""
        libros = self.repo.get_all_libros()

        if disponible is True:
            libros = self.repo.get_libros_disponibles()
        elif disponible is False:
            # Libros sin ejemplares disponibles
            libros = [l for l in libros if not any(
                e.id_libro == l.id_libro and e.estado == EstadoEjemplar.DISPONIBLE
                for e in self.repo.get_all_ejemplares()
            )]

        resultado = []
        for libro in libros:
            ejemplares = self.repo.get_ejemplares_por_libro(libro.id_libro)
            resultado.append({
                "id_libro": libro.id_libro,
                "titulo": libro.titulo,
                "autor": libro.autor,
                "sala": libro.sala,
                "alta_demanda": libro.alta_demanda,
                "ejemplares": [
                    {
                        "codigo_inventario": e.codigo_inventario,
                        "estado": e.estado
                    }
                    for e in ejemplares
                ]
            })

        return resultado

    def obtener_libro(self, id_libro: str) -> Dict:
        """Obtiene el detalle de un libro específico."""
        libro = self.repo.get_libro(id_libro)
        if not libro:
            raise BibliotecaException("Libro no encontrado")

        ejemplares = self.repo.get_ejemplares_por_libro(id_libro)
        return {
            "id_libro": libro.id_libro,
            "titulo": libro.titulo,
            "autor": libro.autor,
            "sala": libro.sala,
            "alta_demanda": libro.alta_demanda,
            "ejemplares": [
                {
                    "codigo_inventario": e.codigo_inventario,
                    "estado": e.estado
                }
                for e in ejemplares
            ]
        }

    # ============ ESTUDIANTES ============

    def registrar_estudiante(self, codigo_estudiante: str, nombre: str, nivel: str) -> Dict:
        """Registra un nuevo estudiante."""
        if self.repo.get_estudiante(codigo_estudiante):
            raise BibliotecaException("El estudiante ya existe")

        estudiante_create = EstudianteCreate(
            codigo_estudiante=codigo_estudiante,
            nombre=nombre,
            nivel=NivelEstudiante(nivel)
        )
        estudiante = self.repo.create_estudiante(estudiante_create)
        return {
            "codigo_estudiante": estudiante.codigo_estudiante,
            "nombre": estudiante.nombre,
            "nivel": estudiante.nivel
        }

    # ============ PRÉSTAMOS ============

    def solicitar_prestamo(self, codigo_estudiante: str, codigo_inventario: str) -> Dict:
        """
        Solicita un préstamo. Implementa RN1, RN2, RN3, RN4, RN5.

        RN1: Límite de préstamos por tipo de estudiante.
        RN2: Bloqueo por préstamos vencidos.
        RN3: Bloqueo por multas pendientes.
        RN4: Disponibilidad del ejemplar.
        RN5: Cálculo dinámico del plazo de vencimiento.
        """
        # Obtener estudiante
        estudiante = self.repo.get_estudiante(codigo_estudiante)
        if not estudiante:
            raise BibliotecaException("Estudiante no encontrado", 404)

        # Obtener ejemplar
        ejemplar = self.repo.get_ejemplar(codigo_inventario)
        if not ejemplar:
            raise BibliotecaException("Ejemplar no encontrado", 404)

        # Obtener libro
        libro = self.repo.get_libro(ejemplar.id_libro)
        if not libro:
            raise BibliotecaException("Libro no encontrado")

        # RN1: Verificar límite de préstamos
        prestamos_activos = self.repo.get_prestamos_activos_estudiante(codigo_estudiante)
        limite = 3 if estudiante.nivel == NivelEstudiante.PREGRADO else 5

        if len(prestamos_activos) >= limite:
            raise BibliotecaException(
                f"limite_prestamos_alcanzado",
                409,
                {"limite": limite, "actuales": len(prestamos_activos)}
            )

        # RN2: Verificar si hay préstamos vencidos
        prestamos_vencidos = self.repo.get_prestamos_vencidos_estudiante(codigo_estudiante)
        if prestamos_vencidos:
            raise BibliotecaException(
                "estudiante_con_vencimientos",
                403,
                {"mensaje": "Debe devolver los libros vencidos antes de solicitar nuevos."}
            )

        # RN3: Verificar multas pendientes
        multas_pendientes = self.repo.get_multas_pendientes_estudiante(codigo_estudiante)
        if multas_pendientes:
            raise BibliotecaException(
                "multas_pendientes",
                403,
                {"mensaje": "El estudiante tiene multas sin pagar."}
            )

        # RN4: Verificar disponibilidad del ejemplar
        if ejemplar.estado != EstadoEjemplar.DISPONIBLE:
            raise BibliotecaException(
                "ejemplar_no_disponible",
                409,
                {"estado_actual": ejemplar.estado}
            )

        # RN5: Calcular fecha de vencimiento
        fecha_prestamo = datetime.now()
        dias_prestamo = 3 if libro.alta_demanda else 15
        fecha_vencimiento = fecha_prestamo + timedelta(days=dias_prestamo)

        # Crear préstamo
        prestamo_create = PrestamoCreate(
            codigo_inventario=codigo_inventario,
            codigo_estudiante=codigo_estudiante
        )
        prestamo = self.repo.create_prestamo(prestamo_create, fecha_prestamo, fecha_vencimiento)

        # Actualizar estado del ejemplar
        self.repo.update_ejemplar_estado(codigo_inventario, EstadoEjemplar.PRESTADO)

        return {
            "id_prestamo": prestamo.id_prestamo,
            "codigo_inventario": prestamo.codigo_inventario,
            "codigo_estudiante": prestamo.codigo_estudiante,
            "fecha_prestamo": prestamo.fecha_prestamo.isoformat(),
            "fecha_vencimiento": prestamo.fecha_vencimiento.isoformat(),
            "estado": prestamo.estado
        }

    def registrar_devolucion(self, id_prestamo: str) -> Dict:
        """
        Registra la devolución de un libro. Implementa RN7.

        RN7: Cálculo y generación automática de multas.
        """
        prestamo = self.repo.get_prestamo(id_prestamo)
        if not prestamo:
            raise BibliotecaException("Préstamo no encontrado", 404)

        fecha_devolucion = datetime.now()

        # Actualizar estado del ejemplar a DISPONIBLE
        self.repo.update_ejemplar_estado(prestamo.codigo_inventario, EstadoEjemplar.DISPONIBLE)

        # RN7: Verificar si hay retraso
        multa_info = None
        if fecha_devolucion > prestamo.fecha_vencimiento:
            # Hay retraso
            dias_retraso = (fecha_devolucion.date() - prestamo.fecha_vencimiento.date()).days
            monto_multa = dias_retraso * 2000

            # Crear multa
            multa_create = MultaCreate(
                id_prestamo=id_prestamo,
                codigo_estudiante=prestamo.codigo_estudiante,
                dias_retraso=dias_retraso,
                monto_total=monto_multa
            )
            multa = self.repo.create_multa(multa_create)

            # Actualizar prestamo a DEVUELTO
            self.repo.update_prestamo_estado(id_prestamo, EstadoPrestamo.DEVUELTO, fecha_devolucion)

            multa_info = {
                "id_multa": multa.id_multa,
                "dias_retraso": multa.dias_retraso,
                "monto": multa.monto_total
            }
        else:
            # Sin retraso
            self.repo.update_prestamo_estado(id_prestamo, EstadoPrestamo.DEVUELTO, fecha_devolucion)

        return {
            "id_prestamo": id_prestamo,
            "estado": "DEVUELTO",
            "fecha_devolucion": fecha_devolucion.isoformat(),
            "multa": multa_info
        }

    def renovar_prestamo(self, id_prestamo: str) -> Dict:
        """
        Renueva un préstamo. Implementa RN6.

        RN6: Restricción de renovación por lista de espera.
        """
        prestamo = self.repo.get_prestamo(id_prestamo)
        if not prestamo:
            raise BibliotecaException("Préstamo no encontrado", 404)

        ejemplar = self.repo.get_ejemplar(prestamo.codigo_inventario)
        if not ejemplar:
            raise BibliotecaException("Ejemplar no encontrado")

        libro = self.repo.get_libro(ejemplar.id_libro)
        if not libro:
            raise BibliotecaException("Libro no encontrado")

        # RN6: Verificar si hay reservas activas
        reservas_activas = self.repo.get_reservas_activas_libro(ejemplar.id_libro)
        if reservas_activas:
            raise BibliotecaException(
                "renovacion_denegada",
                409,
                {"motivo": "libro_solicitado_por_tercero"}
            )

        # Calcular nueva fecha de vencimiento
        dias_prestamo = 3 if libro.alta_demanda else 15
        nueva_fecha_vencimiento = datetime.now() + timedelta(days=dias_prestamo)

        # Actualizar préstamo
        self.repo.update_prestamo_renovacion(id_prestamo, nueva_fecha_vencimiento)

        return {
            "id_prestamo": id_prestamo,
            "nueva_fecha_vencimiento": nueva_fecha_vencimiento.isoformat(),
            "renovaciones": prestamo.renovaciones + 1
        }

    def obtener_prestamos_vigentes(self) -> List[Dict]:
        """Obtiene todos los préstamos vigentes en el sistema."""
        prestamos = self.repo.get_prestamos_vigentes()
        return [
            {
                "id_prestamo": p.id_prestamo,
                "codigo_inventario": p.codigo_inventario,
                "codigo_estudiante": p.codigo_estudiante,
                "fecha_prestamo": p.fecha_prestamo.isoformat(),
                "fecha_vencimiento": p.fecha_vencimiento.isoformat(),
                "estado": p.estado
            }
            for p in prestamos
        ]

    def obtener_prestamos_vencidos(self) -> List[Dict]:
        """Obtiene todos los préstamos vencidos en el sistema."""
        # Actualizar estado de préstamos vencidos basado en fecha actual
        ahora = datetime.now()
        for prestamo in self.repo.get_all_prestamos():
            if prestamo.estado == EstadoPrestamo.VIGENTE and ahora > prestamo.fecha_vencimiento:
                self.repo.update_prestamo_estado(prestamo.id_prestamo, EstadoPrestamo.VENCIDO)

        prestamos = self.repo.get_prestamos_vencidos()
        return [
            {
                "id_prestamo": p.id_prestamo,
                "codigo_inventario": p.codigo_inventario,
                "codigo_estudiante": p.codigo_estudiante,
                "fecha_prestamo": p.fecha_prestamo.isoformat(),
                "fecha_vencimiento": p.fecha_vencimiento.isoformat(),
                "estado": p.estado
            }
            for p in prestamos
        ]

    def obtener_historial_estudiante(self, codigo_estudiante: str) -> List[Dict]:
        """Obtiene el historial completo de préstamos de un estudiante."""
        estudiante = self.repo.get_estudiante(codigo_estudiante)
        if not estudiante:
            raise BibliotecaException("Estudiante no encontrado", 404)

        prestamos = self.repo.get_historial_prestamos_estudiante(codigo_estudiante)
        return [
            {
                "id_prestamo": p.id_prestamo,
                "codigo_inventario": p.codigo_inventario,
                "fecha_prestamo": p.fecha_prestamo.isoformat(),
                "fecha_vencimiento": p.fecha_vencimiento.isoformat(),
                "fecha_devolucion": p.fecha_devolucion.isoformat() if p.fecha_devolucion else None,
                "estado": p.estado
            }
            for p in prestamos
        ]

    # ============ MULTAS ============

    def pagar_multa(self, id_multa: str) -> Dict:
        """Registra el pago de una multa (Decisión D3)."""
        multa = self.repo.get_multa(id_multa)
        if not multa:
            raise BibliotecaException("Multa no encontrada", 404)

        self.repo.update_multa_pago(id_multa)

        return {
            "id_multa": id_multa,
            "estado": "PAGADA",
            "monto_pagado": multa.monto_total
        }

    # ============ RESERVAS ============

    def crear_reserva(self, codigo_estudiante: str, id_libro: str) -> Dict:
        """Crea una reserva para un libro (Decisión D2)."""
        estudiante = self.repo.get_estudiante(codigo_estudiante)
        if not estudiante:
            raise BibliotecaException("Estudiante no encontrado", 404)

        libro = self.repo.get_libro(id_libro)
        if not libro:
            raise BibliotecaException("Libro no encontrado", 404)

        reserva_create = ReservaCreate(
            codigo_estudiante=codigo_estudiante,
            id_libro=id_libro
        )
        reserva = self.repo.create_reserva(reserva_create)

        return {
            "id_reserva": reserva.id_reserva,
            "codigo_estudiante": reserva.codigo_estudiante,
            "id_libro": reserva.id_libro,
            "estado": reserva.estado
        }
