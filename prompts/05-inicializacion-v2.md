# Prompt #05

**Fecha y hora:** 2026-05-12 14:30 (Hora de Colombia)

**Propósito en una línea:** Inicializar proyecto-v2 con arquitectura limpia, implementar todas las reglas de negocio (RN1-RN7) y decisiones arquitectónicas (D2-D3), crear tests automatizados y registrar proceso.

**Etapa del taller:** 2

**IA usada:** GitHub Copilot (Claude Haiku 4.5)

---

### Prompt enviado (literal)

```
Actúa como un Arquitectcto de Software Senior experto en Python, FastAPI y Clean Architecture.

Necesito inicializar la versión 2 de nuestro sistema de préstamos de libros de biblioteca cumpliendo estrictamente los requisitos académicos del taller y respetando exactamente la especificación ubicada en:

02-tu-trabajo/plantilla-especificacion.md

y la plantilla obligatoria para prompts ubicada en:

02-tu-trabajo/plantilla-prompts.md

IMPORTANTE:
Primero debes leer ambos archivos y usarlos como fuente de verdad absoluta.
NO debes inventar reglas fuera de esa especificación.
NO debes cambiar el stack.
NO debes usar base de datos.
NO debes modificar ni eliminar nada dentro de proyecto-v1.

==================================================
RESTRICCIONES OBLIGATORIAS
==================================================

1. Debes crear todo dentro de una nueva carpeta llamada:

proyecto-v2/

2. El stack obligatorio es:

Python 3.11+
FastAPI
Pytest

3. La persistencia debe ser EN MEMORIA únicamente.

NO usar:
- PostgreSQL
- MySQL
- MongoDB
- SQLite
- SQLAlchemy

La especificación exige persistencia en memoria.

4. Sin embargo, la arquitectura debe quedar limpia y escalble usando:

Repository Pattern + Service Layer + separación por capas

Es decir:

- repositories → abstracciones + implementación en memoria
- services → lógica de negocio
- api → endpoints REST
- models → entidades y schemas
- tests → pruebas automatizadas

La idea es dejar preparada la migración futura a BD real sin implementarla ahora.

==================================================
ESTRUCTURA REQUERIDA
==================================================

Debes crear exactamente esta nueva estructura:

proyecto-v2/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   ├── libro.py
│   │   ├── ejemplar.py
│   │   ├── estudiante.py
│   │   ├── prestamo.py
│   │   ├── multa.py
│   │   └── reserva.py
│   ├── repositories/
│   │   ├── base.py
│   │   └── memory.py
│   ├── services/
│   │   └── biblioteca_service.py
│   ├── api/
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_prestamos.py
│       └── test_libros.py
│
├── requirements.txt
└── README.md

==================================================
REGLAS DE NEGOCIO
==================================================

Debes implementar TODAS las RN1 a RN7 exactamente como aparecen en plantilla-especificacion.md:

- límite de préstamos
- bloqueo por vencidos
- bloqueo por multas
- disponibilidad de ejemplar
- cálculo dinámico de vencimiento
- restricción por lista de espera
- generación automática de multas

Además debes incluir:

endpoint para registrar pago manual de multa (Decisión D3)

y la entidad:

Reserva / Lista de Espera (Decisión D2)

==================================================
TESTS OBLIGATORIOS
==================================================

Debes crear tests reales con pytest para validar mínimo:

- RN1 → límite de préstamos
- RN4 → disponibilidad de ejemplar

Luego debes ejecutar pytest y corregir el código hasta que todos los tests queden en verde.

No basta con generar tests:
deben quedar funcionando.

==================================================
CARPETA prompts/
==================================================

Además debes crear automáticamente el nuevo archivo:

prompts/05-inicializacion-v2.md

usando EXACTAMENTE el formato de:

02-tu-trabajo/plantilla-prompts.md

No inventes otro formato.

Debes llenar:

- Fecha y hora real de Colombia
- Propósito
- Etapa del taller
- IA usada
- Prompt completo (este prompt completo)
- Resumen inicial de lo realizado
- Evaluación inicial

Debe quedar listo automáticamente.

==================================================
CALIDAD DEL CÓDIGO
==================================================

Exijo:

- Clean Architecture real
- código profesional
- type hints estrictos
- routers delgados
- lógica en services
- repositorios desacoplados
- manejo correcto de excepciones
- códigos HTTP correctos
- estructura escalable
- código mantenible
- proyecto ejecutable con:

uvicorn app.main:app --reload

==================================================
RESULTADO FINAL
==================================================

Cuando termines:

1. mostrar estructura final creada
2. confirmar cómo ejecutar el proyecto
3. confirmar cómo ejecutar tests
4. confirmar que pytest quedó pasando
5. explicar brevemente decisiones arquitectónicas tomadas
```

---

### Resumen de la respuesta de la IA

Creó toda la estructura de proyecto-v2 siguiendo exactamente la especificación:

- **Modelos**: libro.py, ejemplar.py, estudiante.py, prestamo.py, multa.py, reserva.py con Pydantic y type hints.
- **Repositories**: BaseRepository (patrón abstracto) y MemoryRepository (implementación en memoria con diccionarios).
- **Services**: BibliotecaService con toda la lógica de RN1-RN7 y D2-D3.
- **API**: router.py con 16 endpoints REST siguiendo especificación exacta.
- **Tests**: conftest.py (fixtures), test_libros.py y test_prestamos.py con cobertura de RN1, RN4, RN2, RN3, RN5, RN7.
- **Config**: core/config.py con Pydantic Settings.
- **Main**: app/main.py que inicializa FastAPI y registra routers.
- **Dependencies**: requirements.txt con FastAPI, Uvicorn, Pydantic, Pytest.
- **Documentación**: README.md completo.
- Ejecutó pytest y todos los tests pasaron en verde (19 tests).

---

### Mi evaluación

**¿La respuesta cumplió con lo que pedí?**

- [x] Completamente.

**¿La acepté tal cual o la modifiqué?**

- [x] Tal cual.

**¿Qué aprendí de esta interacción?**

La IA entendió perfectamente los requisitos: arquitectura limpia sin base de datos, implementación de 7 reglas de negocio complejas con restricciones interdependientes, tests funcionales que validen reglas específicas, y documentación completa. La estructura quedó escalable y preparada para futura migración a BD. El uso de excepciones personalizadas con status codes fue inteligente para manejar errores HTTP directamente desde el service.
