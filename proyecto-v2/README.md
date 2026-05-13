# Biblioteca API v2

API REST para gestionar préstamos de libros en una biblioteca universitaria.

## Especificación

Toda la especificación se encuentra en: `../02-tu-trabajo/plantilla-especificacion.md`

## Stack Tecnológico

- **Python 3.11+**
- **FastAPI** - Framework web moderno
- **Pytest** - Testing
- **Pydantic** - Validación de datos

## Arquitectura

Proyecto construido con **Clean Architecture**:

```
app/
├── api/           # Routers y endpoints REST
├── models/        # Schemas Pydantic
├── repositories/  # Abstracción de persistencia
├── services/      # Lógica de negocio
├── core/          # Configuración
└── tests/         # Tests automatizados
```

### Patrones utilizados

- **Repository Pattern**: Abstracción de datos (en memoria, escalable a BD)
- **Service Layer**: Lógica de negocio centralizada
- **Type Hints Estrictos**: Tipado completo en Python
- **Separación de responsabilidades**: Cada capa tiene un propósito específico

## Persistencia

**Completamente en memoria** (según especificación).

La arquitectura permite migración futura a base de datos sin cambios en lógica de negocio.

## Instalación

```bash
# Clonar o descargar el proyecto
cd proyecto-v2

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Ejecución

### Ejecutar servidor de desarrollo

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Ejecutar tests

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con salida detallada
pytest -v

# Ejecutar un archivo específico
pytest app/tests/test_prestamos.py -v

# Ejecutar un test específico
pytest app/tests/test_prestamos.py::test_rn1_pregrado_limite_3 -v
```

## Reglas de Negocio Implementadas

- **RN1**: Límite de préstamos (3 pregrado, 5 posgrado)
- **RN2**: Bloqueo por préstamos vencidos
- **RN3**: Bloqueo por multas pendientes
- **RN4**: Disponibilidad del ejemplar
- **RN5**: Cálculo dinámico del plazo (15 o 3 días)
- **RN6**: Restricción de renovación por lista de espera
- **RN7**: Generación automática de multas

## Decisiones Arquitectónicas

### D1: Persistencia en Memoria

Implementada via `MemoryRepository` que contiene diccionarios para cada entidad.

### D2: Lista de Espera / Reservas

Se implementó la entidad `Reserva` para controlar la RN6.

### D3: Pago Manual de Multas

Endpoint `POST /multas/{id_multa}/pago` registra pagos de multas.

## Endpoints Principales

### Libros
- `POST /api/v1/libros` - Registrar libro
- `GET /api/v1/libros` - Listar libros (con filtro disponible)
- `GET /api/v1/libros/{id_libro}` - Detalle de libro

### Préstamos
- `POST /api/v1/prestamos` - Solicitar préstamo
- `POST /api/v1/prestamos/{id_prestamo}/devolucion` - Registrar devolución
- `POST /api/v1/prestamos/{id_prestamo}/renovacion` - Renovar préstamo
- `GET /api/v1/prestamos/vigentes` - Listar vigentes
- `GET /api/v1/prestamos/vencidos` - Listar vencidos

### Multas
- `POST /api/v1/multas/{id_multa}/pago` - Registrar pago

### Reservas
- `POST /api/v1/reservas` - Crear reserva

## Testing

Los tests cubren:

- **RN1**: Límites de préstamos (pregrado y posgrado)
- **RN4**: Disponibilidad de ejemplares
- **RN2-RN3**: Bloqueos (vencidos, multas)
- **RN5**: Cálculo de plazos
- **RN7**: Generación de multas
- Historial y consultas

Ejecutar: `pytest app/tests/ -v`

## Estructuración del Código

```python
# Modelos (Pydantic)
from app.models.prestamo import Prestamo, EstadoPrestamo

# Repository (Acceso a datos)
from app.repositories.memory import MemoryRepository

# Service (Lógica de negocio)
from app.services.biblioteca_service import BibliotecaService

# API (Endpoints)
from app.api.v1.router import router
```

## Mantenibilidad

- ✅ Type hints completos
- ✅ Código documentado
- ✅ Separación clara de capas
- ✅ Excepciones personalizadas
- ✅ Tests automatizados
- ✅ Preparado para migración a BD

---

**Versión**: 2.0.0
**Estado**: Funcional, listo para producción académica
