from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
from app.repositories.base import BaseRepository
from app.models.libro import Libro, LibroCreate
from app.models.ejemplar import Ejemplar, EjemplarCreate, EstadoEjemplar
from app.models.estudiante import Estudiante, EstudianteCreate
from app.models.prestamo import Prestamo, PrestamoCreate, EstadoPrestamo
from app.models.multa import Multa, MultaCreate, EstadoMulta
from app.models.reserva import Reserva, ReservaCreate, EstadoReserva


class MemoryRepository:
    """Repositorio en memoria para todas las entidades."""

    def __init__(self):
        self.libros: Dict[str, Libro] = {}
        self.ejemplares: Dict[str, Ejemplar] = {}
        self.estudiantes: Dict[str, Estudiante] = {}
        self.prestamos: Dict[str, Prestamo] = {}
        self.multas: Dict[str, Multa] = {}
        self.reservas: Dict[str, Reserva] = {}

    # ============ LIBROS ============

    def create_libro(self, libro: LibroCreate) -> Libro:
        nuevo_libro = Libro(**libro.model_dump())
        self.libros[libro.id_libro] = nuevo_libro
        return nuevo_libro

    def get_libro(self, id_libro: str) -> Optional[Libro]:
        return self.libros.get(id_libro)

    def get_all_libros(self) -> List[Libro]:
        return list(self.libros.values())

    def get_libros_disponibles(self) -> List[Libro]:
        """Retorna libros que tienen al menos un ejemplar disponible."""
        libros_con_disponibles = []
        for libro in self.libros.values():
            ejemplares_del_libro = [
                e for e in self.ejemplares.values()
                if e.id_libro == libro.id_libro and e.estado == EstadoEjemplar.DISPONIBLE
            ]
            if ejemplares_del_libro:
                libros_con_disponibles.append(libro)
        return libros_con_disponibles

    # ============ EJEMPLARES ============

    def create_ejemplar(self, ejemplar: EjemplarCreate) -> Ejemplar:
        nuevo_ejemplar = Ejemplar(**ejemplar.model_dump())
        self.ejemplares[ejemplar.codigo_inventario] = nuevo_ejemplar
        return nuevo_ejemplar

    def get_ejemplar(self, codigo_inventario: str) -> Optional[Ejemplar]:
        return self.ejemplares.get(codigo_inventario)

    def get_all_ejemplares(self) -> List[Ejemplar]:
        return list(self.ejemplares.values())

    def get_ejemplares_por_libro(self, id_libro: str) -> List[Ejemplar]:
        return [e for e in self.ejemplares.values() if e.id_libro == id_libro]

    def update_ejemplar_estado(self, codigo_inventario: str, nuevo_estado: EstadoEjemplar) -> Optional[Ejemplar]:
        ejemplar = self.ejemplares.get(codigo_inventario)
        if ejemplar:
            ejemplar.estado = nuevo_estado
        return ejemplar

    # ============ ESTUDIANTES ============

    def create_estudiante(self, estudiante: EstudianteCreate) -> Estudiante:
        nuevo_estudiante = Estudiante(**estudiante.model_dump())
        self.estudiantes[estudiante.codigo_estudiante] = nuevo_estudiante
        return nuevo_estudiante

    def get_estudiante(self, codigo_estudiante: str) -> Optional[Estudiante]:
        return self.estudiantes.get(codigo_estudiante)

    def get_all_estudiantes(self) -> List[Estudiante]:
        return list(self.estudiantes.values())

    # ============ PRÉSTAMOS ============

    def create_prestamo(self, prestamo: PrestamoCreate, fecha_prestamo: datetime,
                        fecha_vencimiento: datetime) -> Prestamo:
        id_prestamo = str(uuid4())
        nuevo_prestamo = Prestamo(
            id_prestamo=id_prestamo,
            codigo_inventario=prestamo.codigo_inventario,
            codigo_estudiante=prestamo.codigo_estudiante,
            fecha_prestamo=fecha_prestamo,
            fecha_vencimiento=fecha_vencimiento,
            estado=EstadoPrestamo.VIGENTE,
            renovaciones=0
        )
        self.prestamos[id_prestamo] = nuevo_prestamo
        return nuevo_prestamo

    def get_prestamo(self, id_prestamo: str) -> Optional[Prestamo]:
        return self.prestamos.get(id_prestamo)

    def get_all_prestamos(self) -> List[Prestamo]:
        return list(self.prestamos.values())

    def get_prestamos_activos_estudiante(self, codigo_estudiante: str) -> List[Prestamo]:
        """Préstamos VIGENTES del estudiante."""
        return [
            p for p in self.prestamos.values()
            if p.codigo_estudiante == codigo_estudiante and p.estado == EstadoPrestamo.VIGENTE
        ]

    def get_prestamos_vencidos_estudiante(self, codigo_estudiante: str) -> List[Prestamo]:
        """Préstamos VENCIDOS del estudiante."""
        return [
            p for p in self.prestamos.values()
            if p.codigo_estudiante == codigo_estudiante and p.estado == EstadoPrestamo.VENCIDO
        ]

    def get_prestamos_vigentes(self) -> List[Prestamo]:
        """Todos los préstamos vigentes en el sistema."""
        return [p for p in self.prestamos.values() if p.estado == EstadoPrestamo.VIGENTE]

    def get_prestamos_vencidos(self) -> List[Prestamo]:
        """Todos los préstamos vencidos en el sistema."""
        return [p for p in self.prestamos.values() if p.estado == EstadoPrestamo.VENCIDO]

    def get_historial_prestamos_estudiante(self, codigo_estudiante: str) -> List[Prestamo]:
        """Todos los préstamos del estudiante."""
        return [
            p for p in self.prestamos.values()
            if p.codigo_estudiante == codigo_estudiante
        ]

    def update_prestamo_estado(self, id_prestamo: str, nuevo_estado: EstadoPrestamo,
                               fecha_devolucion: Optional[datetime] = None) -> Optional[Prestamo]:
        prestamo = self.prestamos.get(id_prestamo)
        if prestamo:
            prestamo.estado = nuevo_estado
            if fecha_devolucion:
                prestamo.fecha_devolucion = fecha_devolucion
        return prestamo

    def update_prestamo_renovacion(self, id_prestamo: str, nueva_fecha_vencimiento: datetime) -> Optional[Prestamo]:
        prestamo = self.prestamos.get(id_prestamo)
        if prestamo:
            prestamo.fecha_vencimiento = nueva_fecha_vencimiento
            prestamo.renovaciones += 1
        return prestamo

    # ============ MULTAS ============

    def create_multa(self, multa: MultaCreate) -> Multa:
        id_multa = str(uuid4())
        nueva_multa = Multa(
            id_multa=id_multa,
            id_prestamo=multa.id_prestamo,
            codigo_estudiante=multa.codigo_estudiante,
            dias_retraso=multa.dias_retraso,
            monto_total=multa.monto_total,
            estado=EstadoMulta.PENDIENTE
        )
        self.multas[id_multa] = nueva_multa
        return nueva_multa

    def get_multa(self, id_multa: str) -> Optional[Multa]:
        return self.multas.get(id_multa)

    def get_all_multas(self) -> List[Multa]:
        return list(self.multas.values())

    def get_multas_pendientes_estudiante(self, codigo_estudiante: str) -> List[Multa]:
        """Multas pendientes del estudiante."""
        return [
            m for m in self.multas.values()
            if m.codigo_estudiante == codigo_estudiante and m.estado == EstadoMulta.PENDIENTE
        ]

    def get_multas_por_prestamo(self, id_prestamo: str) -> Optional[Multa]:
        """Obtener la multa asociada a un préstamo."""
        for multa in self.multas.values():
            if multa.id_prestamo == id_prestamo:
                return multa
        return None

    def update_multa_pago(self, id_multa: str) -> Optional[Multa]:
        """Marcar una multa como pagada."""
        multa = self.multas.get(id_multa)
        if multa:
            multa.estado = EstadoMulta.PAGADA
        return multa

    # ============ RESERVAS ============

    def create_reserva(self, reserva: ReservaCreate) -> Reserva:
        id_reserva = str(uuid4())
        nueva_reserva = Reserva(
            id_reserva=id_reserva,
            codigo_estudiante=reserva.codigo_estudiante,
            id_libro=reserva.id_libro,
            estado=EstadoReserva.ACTIVA
        )
        self.reservas[id_reserva] = nueva_reserva
        return nueva_reserva

    def get_reserva(self, id_reserva: str) -> Optional[Reserva]:
        return self.reservas.get(id_reserva)

    def get_all_reservas(self) -> List[Reserva]:
        return list(self.reservas.values())

    def get_reservas_activas_libro(self, id_libro: str) -> List[Reserva]:
        """Reservas activas para un libro específico."""
        return [
            r for r in self.reservas.values()
            if r.id_libro == id_libro and r.estado == EstadoReserva.ACTIVA
        ]

    def get_reservas_estudiante(self, codigo_estudiante: str) -> List[Reserva]:
        """Todas las reservas del estudiante."""
        return [
            r for r in self.reservas.values()
            if r.codigo_estudiante == codigo_estudiante
        ]

    def update_reserva_estado(self, id_reserva: str, nuevo_estado: EstadoReserva) -> Optional[Reserva]:
        reserva = self.reservas.get(id_reserva)
        if reserva:
            reserva.estado = nuevo_estado
        return reserva
