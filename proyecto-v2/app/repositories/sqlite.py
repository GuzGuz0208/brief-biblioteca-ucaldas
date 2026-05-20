import sqlite3
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

# Importamos los modelos que ya tienes
from app.models.libro import Libro, LibroCreate
from app.models.ejemplar import Ejemplar, EjemplarCreate, EstadoEjemplar
from app.models.estudiante import Estudiante, EstudianteCreate
from app.models.prestamo import Prestamo, PrestamoCreate, EstadoPrestamo
from app.models.multa import Multa, MultaCreate, EstadoMulta
from app.models.reserva import Reserva, ReservaCreate, EstadoReserva

class SqliteRepository:
    """Repositorio en SQLite para todas las entidades."""

    def __init__(self, db_path: str = "biblioteca.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        """Crea y retorna una conexión a la base de datos."""
        # Permitir acceso desde diferentes hilos (uvicorn workers / FastAPI)
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        # Esto permite acceder a las columnas por nombre como un diccionario
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Inicializa las tablas si no existen."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Tabla Libros
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS libros (
                    id_libro TEXT PRIMARY KEY,
                    titulo TEXT NOT NULL,
                    autor TEXT NOT NULL,
                    sala TEXT NOT NULL,
                    alta_demanda BOOLEAN NOT NULL
                )
            ''')

            # Tabla Ejemplares
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ejemplares (
                    codigo_inventario TEXT PRIMARY KEY,
                    id_libro TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    FOREIGN KEY(id_libro) REFERENCES libros(id_libro)
                )
            ''')

            # Tabla Estudiantes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estudiantes (
                    codigo_estudiante TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    nivel TEXT NOT NULL
                )
            ''')

            # Tabla Prestamos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prestamos (
                    id_prestamo TEXT PRIMARY KEY,
                    codigo_inventario TEXT NOT NULL,
                    codigo_estudiante TEXT NOT NULL,
                    fecha_prestamo TEXT NOT NULL,
                    fecha_vencimiento TEXT NOT NULL,
                    fecha_devolucion TEXT,
                    estado TEXT NOT NULL,
                    renovaciones INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(codigo_inventario) REFERENCES ejemplares(codigo_inventario),
                    FOREIGN KEY(codigo_estudiante) REFERENCES estudiantes(codigo_estudiante)
                )
            ''')

            # Tabla Multas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS multas (
                    id_multa TEXT PRIMARY KEY,
                    id_prestamo TEXT NOT NULL,
                    codigo_estudiante TEXT NOT NULL,
                    dias_retraso INTEGER NOT NULL,
                    monto_total INTEGER NOT NULL,
                    estado TEXT NOT NULL,
                    FOREIGN KEY(id_prestamo) REFERENCES prestamos(id_prestamo),
                    FOREIGN KEY(codigo_estudiante) REFERENCES estudiantes(codigo_estudiante)
                )
            ''')

            # Tabla Reservas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reservas (
                    id_reserva TEXT PRIMARY KEY,
                    codigo_estudiante TEXT NOT NULL,
                    id_libro TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    FOREIGN KEY(codigo_estudiante) REFERENCES estudiantes(codigo_estudiante),
                    FOREIGN KEY(id_libro) REFERENCES libros(id_libro)
                )
            ''')
            conn.commit()

    # ============ HELPER PARA PARSEAR FECHAS ============
    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        if not date_str:
            return None
        return datetime.fromisoformat(date_str)

    # ============ LIBROS ============

    def create_libro(self, libro: LibroCreate) -> Libro:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO libros (id_libro, titulo, autor, sala, alta_demanda) VALUES (?, ?, ?, ?, ?)",
                (libro.id_libro, libro.titulo, libro.autor, libro.sala, libro.alta_demanda)
            )
            conn.commit()
        return Libro(**libro.model_dump())

    def get_libro(self, id_libro: str) -> Optional[Libro]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM libros WHERE id_libro = ?", (id_libro,))
            row = cursor.fetchone()
            if row:
                return Libro(**dict(row))
        return None

    def get_all_libros(self) -> List[Libro]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM libros")
            rows = cursor.fetchall()
            return [Libro(**dict(row)) for row in rows]

    def get_libros_disponibles(self) -> List[Libro]:
        """Retorna libros que tienen al menos un ejemplar disponible."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Un INNER JOIN para encontrar libros con ejemplares en estado DISPONIBLE
            cursor.execute('''
                SELECT DISTINCT l.* FROM libros l
                INNER JOIN ejemplares e ON l.id_libro = e.id_libro
                WHERE e.estado = ?
            ''', (str(EstadoEjemplar.DISPONIBLE),))
            rows = cursor.fetchall()
            return [Libro(**dict(row)) for row in rows]

    # ============ EJEMPLARES ============

    def create_ejemplar(self, ejemplar: EjemplarCreate) -> Ejemplar:
        nuevo_ejemplar = Ejemplar(**ejemplar.model_dump())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ejemplares (codigo_inventario, id_libro, estado) VALUES (?, ?, ?)",
                (nuevo_ejemplar.codigo_inventario, nuevo_ejemplar.id_libro, str(nuevo_ejemplar.estado))
            )
            conn.commit()
        return nuevo_ejemplar

    def get_ejemplar(self, codigo_inventario: str) -> Optional[Ejemplar]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ejemplares WHERE codigo_inventario = ?", (codigo_inventario,))
            row = cursor.fetchone()
            if row:
                return Ejemplar(**dict(row))
        return None

    def get_all_ejemplares(self) -> List[Ejemplar]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ejemplares")
            rows = cursor.fetchall()
            return [Ejemplar(**dict(row)) for row in rows]

    def get_ejemplares_por_libro(self, id_libro: str) -> List[Ejemplar]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ejemplares WHERE id_libro = ?", (id_libro,))
            rows = cursor.fetchall()
            return [Ejemplar(**dict(row)) for row in rows]

    def update_ejemplar_estado(self, codigo_inventario: str, nuevo_estado: EstadoEjemplar) -> Optional[Ejemplar]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE ejemplares SET estado = ? WHERE codigo_inventario = ?", (nuevo_estado.value, codigo_inventario))
            conn.commit()
        return self.get_ejemplar(codigo_inventario)

    # ============ ESTUDIANTES ============

    def create_estudiante(self, estudiante: EstudianteCreate) -> Estudiante:
        nuevo_estudiante = Estudiante(**estudiante.model_dump())
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO estudiantes (codigo_estudiante, nombre, nivel) VALUES (?, ?, ?)",
                (nuevo_estudiante.codigo_estudiante, nuevo_estudiante.nombre, nuevo_estudiante.nivel.value)
            )
            conn.commit()
        return nuevo_estudiante

    def get_estudiante(self, codigo_estudiante: str) -> Optional[Estudiante]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM estudiantes WHERE codigo_estudiante = ?", (codigo_estudiante,))
            row = cursor.fetchone()
            if row:
                return Estudiante(**dict(row))
        return None

    def get_all_estudiantes(self) -> List[Estudiante]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM estudiantes")
            rows = cursor.fetchall()
            return [Estudiante(**dict(row)) for row in rows]

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
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO prestamos (id_prestamo, codigo_inventario, codigo_estudiante, fecha_prestamo, fecha_vencimiento, estado, renovaciones) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (id_prestamo, prestamo.codigo_inventario, prestamo.codigo_estudiante, fecha_prestamo.isoformat(), fecha_vencimiento.isoformat(), str(EstadoPrestamo.VIGENTE), 0)
            )
            conn.commit()
        return nuevo_prestamo

    def get_prestamo(self, id_prestamo: str) -> Optional[Prestamo]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prestamos WHERE id_prestamo = ?", (id_prestamo,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d['fecha_prestamo'] = self._parse_datetime(d['fecha_prestamo'])
                d['fecha_vencimiento'] = self._parse_datetime(d['fecha_vencimiento'])
                d['fecha_devolucion'] = self._parse_datetime(d['fecha_devolucion'])
                return Prestamo(**d)
        return None

    def get_all_prestamos(self) -> List[Prestamo]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prestamos")
            rows = cursor.fetchall()
            prestamos = []
            for row in rows:
                d = dict(row)
                d['fecha_prestamo'] = self._parse_datetime(d['fecha_prestamo'])
                d['fecha_vencimiento'] = self._parse_datetime(d['fecha_vencimiento'])
                d['fecha_devolucion'] = self._parse_datetime(d['fecha_devolucion'])
                prestamos.append(Prestamo(**d))
            return prestamos

    def get_prestamos_activos_estudiante(self, codigo_estudiante: str) -> List[Prestamo]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prestamos WHERE codigo_estudiante = ? AND estado = ?", (codigo_estudiante, str(EstadoPrestamo.VIGENTE)))
            rows = cursor.fetchall()
            prestamos = []
            for row in rows:
                d = dict(row)
                d['fecha_prestamo'] = self._parse_datetime(d['fecha_prestamo'])
                d['fecha_vencimiento'] = self._parse_datetime(d['fecha_vencimiento'])
                d['fecha_devolucion'] = self._parse_datetime(d['fecha_devolucion'])
                prestamos.append(Prestamo(**d))
            return prestamos

    def get_prestamos_vencidos_estudiante(self, codigo_estudiante: str) -> List[Prestamo]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prestamos WHERE codigo_estudiante = ? AND estado = ?", (codigo_estudiante, str(EstadoPrestamo.VENCIDO)))
            rows = cursor.fetchall()
            prestamos = []
            for row in rows:
                d = dict(row)
                d['fecha_prestamo'] = self._parse_datetime(d['fecha_prestamo'])
                d['fecha_vencimiento'] = self._parse_datetime(d['fecha_vencimiento'])
                d['fecha_devolucion'] = self._parse_datetime(d['fecha_devolucion'])
                prestamos.append(Prestamo(**d))
            return prestamos

    def get_prestamos_vigentes(self) -> List[Prestamo]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prestamos WHERE estado = ?", (str(EstadoPrestamo.VIGENTE),))
            rows = cursor.fetchall()
            prestamos = []
            for row in rows:
                d = dict(row)
                d['fecha_prestamo'] = self._parse_datetime(d['fecha_prestamo'])
                d['fecha_vencimiento'] = self._parse_datetime(d['fecha_vencimiento'])
                d['fecha_devolucion'] = self._parse_datetime(d['fecha_devolucion'])
                prestamos.append(Prestamo(**d))
            return prestamos

    def get_prestamos_vencidos(self) -> List[Prestamo]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prestamos WHERE estado = ?", (str(EstadoPrestamo.VENCIDO),))
            rows = cursor.fetchall()
            prestamos = []
            for row in rows:
                d = dict(row)
                d['fecha_prestamo'] = self._parse_datetime(d['fecha_prestamo'])
                d['fecha_vencimiento'] = self._parse_datetime(d['fecha_vencimiento'])
                d['fecha_devolucion'] = self._parse_datetime(d['fecha_devolucion'])
                prestamos.append(Prestamo(**d))
            return prestamos

    def get_historial_prestamos_estudiante(self, codigo_estudiante: str) -> List[Prestamo]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prestamos WHERE codigo_estudiante = ?", (codigo_estudiante,))
            rows = cursor.fetchall()
            prestamos = []
            for row in rows:
                d = dict(row)
                d['fecha_prestamo'] = self._parse_datetime(d['fecha_prestamo'])
                d['fecha_vencimiento'] = self._parse_datetime(d['fecha_vencimiento'])
                d['fecha_devolucion'] = self._parse_datetime(d['fecha_devolucion'])
                prestamos.append(Prestamo(**d))
            return prestamos

    def update_prestamo_estado(self, id_prestamo: str, nuevo_estado: EstadoPrestamo,
                               fecha_devolucion: Optional[datetime] = None) -> Optional[Prestamo]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if fecha_devolucion:
                cursor.execute("UPDATE prestamos SET estado = ?, fecha_devolucion = ? WHERE id_prestamo = ?", (nuevo_estado.value, fecha_devolucion.isoformat(), id_prestamo))
            else:
                cursor.execute("UPDATE prestamos SET estado = ? WHERE id_prestamo = ?", (nuevo_estado.value, id_prestamo))
            conn.commit()
        return self.get_prestamo(id_prestamo)

    def update_prestamo_renovacion(self, id_prestamo: str, nueva_fecha_vencimiento: datetime) -> Optional[Prestamo]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE prestamos SET fecha_vencimiento = ?, renovaciones = renovaciones + 1 WHERE id_prestamo = ?", (nueva_fecha_vencimiento.isoformat(), id_prestamo))
            conn.commit()
        return self.get_prestamo(id_prestamo)

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
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO multas (id_multa, id_prestamo, codigo_estudiante, dias_retraso, monto_total, estado) VALUES (?, ?, ?, ?, ?, ?)",
                (id_multa, multa.id_prestamo, multa.codigo_estudiante, multa.dias_retraso, multa.monto_total, str(EstadoMulta.PENDIENTE))
            )
            conn.commit()
        return nueva_multa

    def get_multa(self, id_multa: str) -> Optional[Multa]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM multas WHERE id_multa = ?", (id_multa,))
            row = cursor.fetchone()
            if row:
                return Multa(**dict(row))
        return None

    def get_all_multas(self) -> List[Multa]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM multas")
            rows = cursor.fetchall()
            return [Multa(**dict(row)) for row in rows]

    def get_multas_pendientes_estudiante(self, codigo_estudiante: str) -> List[Multa]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM multas WHERE codigo_estudiante = ? AND estado = ?", (codigo_estudiante, str(EstadoMulta.PENDIENTE)))
            rows = cursor.fetchall()
            return [Multa(**dict(row)) for row in rows]

    def get_multas_por_prestamo(self, id_prestamo: str) -> Optional[Multa]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM multas WHERE id_prestamo = ?", (id_prestamo,))
            row = cursor.fetchone()
            if row:
                return Multa(**dict(row))
        return None

    def update_multa_pago(self, id_multa: str) -> Optional[Multa]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE multas SET estado = ? WHERE id_multa = ?", (str(EstadoMulta.PAGADA), id_multa))
            conn.commit()
        return self.get_multa(id_multa)

    # ============ RESERVAS ============

    def create_reserva(self, reserva: ReservaCreate) -> Reserva:
        id_reserva = str(uuid4())
        nueva_reserva = Reserva(
            id_reserva=id_reserva,
            codigo_estudiante=reserva.codigo_estudiante,
            id_libro=reserva.id_libro,
            estado=EstadoReserva.ACTIVA
        )
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reservas (id_reserva, codigo_estudiante, id_libro, estado) VALUES (?, ?, ?, ?)",
                (id_reserva, reserva.codigo_estudiante, reserva.id_libro, str(EstadoReserva.ACTIVA))
            )
            conn.commit()
        return nueva_reserva

    def get_reserva(self, id_reserva: str) -> Optional[Reserva]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reservas WHERE id_reserva = ?", (id_reserva,))
            row = cursor.fetchone()
            if row:
                return Reserva(**dict(row))
        return None

    def get_all_reservas(self) -> List[Reserva]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reservas")
            rows = cursor.fetchall()
            return [Reserva(**dict(row)) for row in rows]

    def get_reservas_activas_libro(self, id_libro: str) -> List[Reserva]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reservas WHERE id_libro = ? AND estado = ?", (id_libro, str(EstadoReserva.ACTIVA)))
            rows = cursor.fetchall()
            return [Reserva(**dict(row)) for row in rows]

    def get_reservas_estudiante(self, codigo_estudiante: str) -> List[Reserva]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reservas WHERE codigo_estudiante = ?", (codigo_estudiante,))
            rows = cursor.fetchall()
            return [Reserva(**dict(row)) for row in rows]

    def update_reserva_estado(self, id_reserva: str, nuevo_estado: EstadoReserva) -> Optional[Reserva]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE reservas SET estado = ? WHERE id_reserva = ?", (nuevo_estado.value, id_reserva))
            conn.commit()
        return self.get_reserva(id_reserva)