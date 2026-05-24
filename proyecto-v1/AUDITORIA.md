1. FECHA DE AUDITORÍA: 19 de mayo de 2026

2. CONTEXTO DEL PROYECTO:

Se evaluó el servicio contenido en `proyecto-v1` para verificar su conformidad con el Plan de Pruebas de la Etapa 4 de la Biblioteca UCaldas. La auditoría se centró en la consistencia de rutas REST, uso correcto de esquemas Pydantic, y la existencia de reglas de negocio críticas relacionadas con la gestión de estudiantes, libros/ejemplares y préstamos (límites por tipo de usuario, vencimientos, multas y listas de espera). Las pruebas fueron de caja negra (ejecución de curls) y revisión del código fuente disponible.

3. ENDPOINTS INEXISTENTES (HALLAZGOS CRÍTICOS):

- **POST /api/estudiantes**: No existe. Resultado: los intentos de crear usuarios mediante `curl` fallaron con 404/405 porque no hay ruta ni controlador que registre estudiantes. Actualmente no hay persistencia ni validación de `tipo` (pregrado/posgrado).
- **POST /api/libros**: No existe. Resultado: no se pueden añadir nuevos libros vía API; el sistema usa un catálogo estático de 3 libros en memoria.
- **POST /api/libros/{id}/ejemplares**: No existe la entidad `ejemplar` ni la gestión de ejemplares independientes. No es posible crear instancias físicas de un libro para prestarlas individualmente.
- **Falta de lógica de negocio (RNs)**:
  - RN1 / RN2 — Límite de préstamos por tipo: no implementado; no hay restricciones de 3 préstamos para `pregrado` ni 5 para `posgrado`.
  - RN3 — Validación de préstamos vencidos: ausente; el sistema no bloquea acciones por préstamos vencidos ni calcula vencimientos.
  - RN4 / RN8 — Multas económicas: inexistente; no se calcula, registra ni expone la multa por retraso.
  - RN5 — Duplicación de préstamos sobre el mismo ejemplar: no hay control; el sistema podría permitir prestar un mismo ejemplar simultáneamente.
  - RN7 — Listas de espera/cola: ausente; no existe mecanismo para encolar solicitudes cuando un ejemplar no está disponible.

Impacto: Estos hallazgos impiden la validación automatizada del comportamiento esperado en la Etapa 4 y producen fallos en los curls especificados por el plan de pruebas.

4. REFACTORIZACIÓN DEL CÓDIGO (`main.py`) — VERSIÓN PROPUESTA COMPLETA

Descripción: la versión propuesta implementa rutas bajo `/api`, modelos Pydantic con tipado estricto, endpoints para estudiantes, libros, ejemplares y préstamos, y reglas de negocio en memoria para límites y control de ejemplares.

Sustituir o actualizar `proyecto-v1/main.py` con el siguiente contenido:

```python
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timedelta

app = FastAPI(title="API Biblioteca UCaldas - Refactor Etapa 4", version="1.0.0")

class Estudiante(BaseModel):
    id: str = Field(..., example="EST-001")
    nombre: str
    programa: str
    semestre: Optional[int]
    tipo: str = Field(..., regex=r"^(pregrado|posgrado)$")

class Libro(BaseModel):
    id: int
    titulo: str
    autor: str
    descripcion: Optional[str] = None

class Ejemplar(BaseModel):
    id: int
    libro_id: int
    disponible: bool = True
    waitlist: List[str] = []  # lista de ids de estudiantes en espera

class CrearPrestamoRequest(BaseModel):
    estudianteId: str
    ejemplarId: int
    dias: Optional[int] = 14

class Prestamo(BaseModel):
    id: int
    ejemplarId: int
    estudianteId: str
    fecha_prestamo: str
    fecha_vencimiento: str
    fecha_devolucion: Optional[str] = None
    multa_acumulada: float = 0.0

# --- Almacenamiento en memoria (prototipo) ---
estudiantes: Dict[str, Estudiante] = {}
libros: Dict[int, Libro] = {}
ejemplares: Dict[int, Ejemplar] = {}
prestamos: Dict[int, Prestamo] = {}

_ejemplar_counter = 1
_prestamo_counter = 1

# Reglas (configurables)
LIMITE_PRESTAMOS = {"pregrado": 3, "posgrado": 5}
MULTA_DIARIA = 0.50

def fecha_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def contar_prestamos_vigentes(estudiante_id: str) -> int:
    return sum(1 for p in prestamos.values() if p.estudianteId == estudiante_id and p.fecha_devolucion is None)

# --- Endpoints — Estudiantes ---
@app.post("/api/estudiantes", response_model=Estudiante)
def crear_estudiante(est: Estudiante):
    if est.id in estudiantes:
        raise HTTPException(status_code=400, detail="Estudiante ya existe")
    estudiantes[est.id] = est
    return est

@app.get("/api/estudiantes", response_model=List[Estudiante])
def listar_estudiantes():
    return list(estudiantes.values())

# --- Endpoints — Libros y Ejemplares ---
@app.post("/api/libros", response_model=Libro)
def crear_libro(lib: Libro):
    if lib.id in libros:
        raise HTTPException(status_code=400, detail="Libro ya existe")
    libros[lib.id] = lib
    return lib

@app.post("/api/libros/{libro_id}/ejemplares", response_model=List[Ejemplar])
def crear_ejemplares(libro_id: int = Path(...), cantidad: int = Query(1, ge=1)):
    global _ejemplar_counter
    if libro_id not in libros:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    created: List[Ejemplar] = []
    for _ in range(cantidad):
        ejempl = Ejemplar(id=_ejemplar_counter, libro_id=libro_id, disponible=True, waitlist=[])
        ejemplares[_ejemplar_counter] = ejempl
        created.append(ejempl)
        _ejemplar_counter += 1
    return created

@app.get("/api/libros", response_model=List[Libro])
def listar_libros():
    return list(libros.values())

@app.get("/api/ejemplares", response_model=List[Ejemplar])
def listar_ejemplares():
    return list(ejemplares.values())

# --- Endpoints — Préstamos ---
@app.post("/api/prestamos", response_model=Prestamo)
def crear_prestamo(req: CrearPrestamoRequest):
    global _prestamo_counter
    # Validaciones
    if req.estudianteId not in estudiantes:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    if req.ejemplarId not in ejemplares:
        raise HTTPException(status_code=404, detail="Ejemplar no encontrado")

    ejempl = ejemplares[req.ejemplarId]
    # RN5: evitar duplicación — ejemplar debe estar disponible
    if not ejempl.disponible:
        # Añadir a lista de espera y devolver error controlado
        if req.estudianteId not in ejempl.waitlist:
            ejempl.waitlist.append(req.estudianteId)
        raise HTTPException(status_code=400, detail="Ejemplar no disponible; añadido a lista de espera")

    # RN1/RN2: límites por tipo
    estudiante = estudiantes[req.estudianteId]
    limite = LIMITE_PRESTAMOS.get(estudiante.tipo, 3)
    vigentes = contar_prestamos_vigentes(estudiante.id)
    if vigentes >= limite:
        raise HTTPException(status_code=400, detail=f"Límite de préstamos ({limite}) alcanzado para este usuario")

    # Crear préstamo
    ahora = datetime.now()
    venc = ahora + timedelta(days=req.dias or 14)
    prest = Prestamo(
        id=_prestamo_counter,
        ejemplarId=req.ejemplarId,
        estudianteId=req.estudianteId,
        fecha_prestamo=fecha_str(ahora),
        fecha_vencimiento=fecha_str(venc),
    )
    prestamos[_prestamo_counter] = prest
    _prestamo_counter += 1

    # Marcar ejemplar no disponible
    ejempl.disponible = False
    return prest

@app.get("/api/prestamos", response_model=List[Prestamo])
def listar_prestamos():
    return list(prestamos.values())

@app.put("/api/prestamos/{prestamo_id}/devolver", response_model=Prestamo)
def devolver_prestamo(prestamo_id: int = Path(...)):
    if prestamo_id not in prestamos:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    prest = prestamos[prestamo_id]
    if prest.fecha_devolucion is not None:
        raise HTTPException(status_code=400, detail="Préstamo ya devuelto")

    fecha_dev = datetime.now()
    prest.fecha_devolucion = fecha_str(fecha_dev)

    # Calcular multa si aplica
    venc = datetime.strptime(prest.fecha_vencimiento, "%Y-%m-%d %H:%M:%S")
    if fecha_dev > venc:
        dias = (fecha_dev - venc).days
        prest.multa_acumulada = round(dias * MULTA_DIARIA, 2)

    # Liberar ejemplar y gestionar waitlist
    ejempl = ejemplares.get(prest.ejemplarId)
    if ejempl:
        ejempl.disponible = True
        if ejempl.waitlist:
            siguiente = ejempl.waitlist.pop(0)
            # En un sistema real se notificará al usuario; aquí solo se libera la posición.

    return prest

@app.post("/api/ejemplares/{ejemplar_id}/renovar", response_model=Prestamo)
def renovar_prestamo(ejemplar_id: int = Path(...), estudianteId: str = Query(...)):
    # Buscar préstamo vigente para ejemplar y estudiante
    prest = next((p for p in prestamos.values() if p.ejemplarId == ejemplar_id and p.estudianteId == estudianteId and p.fecha_devolucion is None), None)
    if not prest:
        raise HTTPException(status_code=404, detail="Préstamo vigente no encontrado para ese ejemplar/estudiante")
    ejempl = ejemplares.get(ejemplar_id)
    if ejempl and ejempl.waitlist:
        raise HTTPException(status_code=400, detail="No se puede renovar: existe lista de espera para este ejemplar")
    # Extender 7 días
    fecha_v = datetime.strptime(prest.fecha_vencimiento, "%Y-%m-%d %H:%M:%S")
    nueva_v = fecha_v + timedelta(days=7)
    prest.fecha_vencimiento = fecha_str(nueva_v)
    return prest

```

Observaciones:
- La implementación usa almacenamiento en memoria; es una base para pruebas y prototipado.
- Para producción: migrar a persistencia (BD), añadir autenticación/autorización, pruebas unitarias e integración, y manejo asíncrono de notificaciones en la `waitlist`.

5. CURLS DE VERIFICACIÓN FINAL

Ejecutar los siguientes comandos en Git Bash o terminal para validar la API propuesta (host: `http://localhost:8000`):

- Crear estudiante:
```
curl -i -X POST http://localhost:8000/api/estudiantes \
  -H "Content-Type: application/json" \
  -d '{"id":"EST-001","nombre":"Ana Lopez","programa":"Ingenieria de Sistemas","semestre":5,"tipo":"pregrado"}'
```

- Crear libro:
```
curl -i -X POST http://localhost:8000/api/libros \
  -H "Content-Type: application/json" \
  -d '{"id":100,"titulo":"Clean Architecture","autor":"R. C. Martin"}'
```

- Crear ejemplar para el libro (libro_id = 100):
```
curl -i -X POST "http://localhost:8000/api/libros/100/ejemplares?cantidad=1"
```

- Listar ejemplares:
```
curl -i -X GET http://localhost:8000/api/ejemplares
```

- Crear préstamo (body JSON; usar `ejemplarId` obtenido del listado anterior):
```
curl -i -X POST http://localhost:8000/api/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId":"EST-001","ejemplarId":1,"dias":14}'
```

- Intentar crear préstamo duplicado sobre el mismo ejemplar (debe fallar y añadir a waitlist):
```
curl -i -X POST http://localhost:8000/api/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId":"EST-001","ejemplarId":1}'
```

- Listar préstamos:
```
curl -i -X GET http://localhost:8000/api/prestamos
```

- Devolver préstamo (suponiendo `prestamo_id` = 1):
```
curl -i -X PUT http://localhost:8000/api/prestamos/1/devolver
```

- Renovar préstamo (ejemplar_id y estudianteId):
```
curl -i -X POST "http://localhost:8000/api/ejemplares/1/renovar?estudianteId=EST-001"
```

---

Registro de Prompt:
- Fecha: 19 de mayo de 2026
- Objetivo: Auditoría y refactorización del `proyecto-v1` para Etapa 4
- Modelo de IA utilizado: GPT-5 mini
