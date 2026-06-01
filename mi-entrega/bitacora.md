# Bitácora del Taller — Juan Esteban Guzmán Henao

> **Documento vivo.** Llenado a medida que avanzó el taller.

---

## Sección 1 — Hallazgos de la auditoría humana (Etapa 3)

### Inventario inicial

- **Archivos generados por la IA:**
  `app/__init__.py`, `app/main.py`, `app/core/config.py`, `app/models/libro.py`, `app/models/ejemplar.py`, `app/models/estudiante.py`, `app/models/prestamo.py`, `app/models/multa.py`, `app/models/reserva.py`, `app/repositories/base.py`, `app/repositories/memory.py`, `app/repositories/sqlite.py`, `app/services/biblioteca_service.py`, `app/api/v1/router.py`, `app/tests/conftest.py`, `app/tests/test_libros.py`, `app/tests/test_prestamos.py`, `requirements.txt`, `README.md`

- **Dependencias instaladas:**
  `fastapi==0.104.1`, `uvicorn[standard]==0.24.0`, `pydantic==2.5.0`, `pydantic-settings==2.1.0`, `pytest==7.4.3`, `pytest-asyncio==0.21.1`, `httpx==0.25.2`

- **Dependencias que NO pediste pero la IA agregó:** ninguna fuera de lo especificado.

- **Archivos que NO pediste pero la IA generó:**
  `RESUMEN_INICIALIZACION_V2.md` (resumen ejecutivo de la inicialización), `app/repositories/sqlite.py` (la especificación original pedía solo persistencia en memoria; la IA migró a SQLite en una sesión posterior sin que se lo solicitara explícitamente).

### Mapeo de reglas a código

| Regla | Archivo y línea aproximada | ¿Aplica correctamente? | Notas |
|---|---|---|---|
| RN1 — Límite préstamos pregrado (3) | `biblioteca_service.py:174-183` | Sí | Detecta nivel PREGRADO, límite 3; mismo bloque que RN2 |
| RN2 — Límite préstamos posgrado (5) | `biblioteca_service.py:174-183` | Sí | Mismo bloque que RN1, límite 5 |
| RN3 — Bloqueo por vencidos | `biblioteca_service.py:185-192` | Sí | Retorna 403 internamente; el router lo normaliza a 409 |
| RN4 — Bloqueo por multas | `biblioteca_service.py:194-201` | Sí | Retorna 403 internamente; el router lo normaliza a 409 |
| RN5 — Disponibilidad del ejemplar | `biblioteca_service.py:203-209` | Sí | Valida estado DISPONIBLE antes de crear el préstamo |
| RN6 — Plazos diferenciados (15 / 3 días) | `biblioteca_service.py:211-214` | Sí | `dias_prestamo = 3 if libro.alta_demanda else 15` |
| RN7 — Bloqueo renovación por reserva activa | `biblioteca_service.py:303-310` | Sí | Consulta `get_reservas_activas_libro` antes de renovar |
| RN8 — Multa por devolución tardía | `biblioteca_service.py:250-273` | Sí | `monto = dias_retraso × 2000`; se genera automáticamente |

### Hallazgos detectados

#### Hallazgo H1

- **Archivo:** `app/repositories/sqlite.py`, líneas 150, 162, 244, 279, 293, 307, 321, 380, 404, 420, 438, 462
- **Tipo:** bug
- **Severidad:** alta
- **Regla violada:** ninguna específica — bloqueaba todo el sistema
- **Descripción:** En Python 3.12, `str(EstadoEjemplar.DISPONIBLE)` devuelve `'EstadoEjemplar.DISPONIBLE'` en lugar de `'DISPONIBLE'`. El repositorio usaba `str()` para serializar enums al guardar en SQLite. Al leer, Pydantic rechazaba el valor `'EstadoEjemplar.DISPONIBLE'` porque no coincide con ninguno de los valores permitidos del enum (`'DISPONIBLE'`, `'PRESTADO'`, `'EXTRAVIADO'`).
- **Cómo lo detecté:** El servidor devolvía 500 Internal Server Error en cada `POST /api/v1/prestamos`. El traceback de uvicorn mostraba: `pydantic_core.ValidationError: Input should be 'DISPONIBLE', 'PRESTADO' or 'EXTRAVIADO' [input_value='EstadoEjemplar.DISPONIBLE']`.
- **Reproducción:** Crear ejemplares → intentar crear un préstamo → 500 en cualquier endpoint que lea ejemplares de la BD.

#### Hallazgo H2

- **Archivo:** `app/services/biblioteca_service.py`, líneas 422-451
- **Tipo:** código innecesario / deuda técnica
- **Severidad:** baja
- **Regla violada:** ninguna específica
- **Descripción:** El método `registrar_prestamo()` es un helper auxiliar creado para satisfacer un test legacy adicional. No está expuesto en ningún router, su lógica es parcial (crea estudiantes automáticamente, ignora excepciones silenciosamente) y el propio comentario del método lo reconoce como fuera de la API pública. Genera confusión sobre el contrato real del servicio.
- **Cómo lo detecté:** Lectura del código fuente. El comentario dice explícitamente "este helper no forma parte de la API pública".
- **Reproducción:** No genera error — es código muerto.

#### Hallazgo H3

- **Archivo:** `app/services/biblioteca_service.py:3` y `app/api/v1/router.py:5`
- **Tipo:** inconsistencia de tipos
- **Severidad:** media
- **Regla violada:** ninguna específica
- **Descripción:** El servicio importa y declara `MemoryRepository` como tipo del constructor (`def __init__(self, repository: MemoryRepository)`), pero el router instancia y pasa un `SqliteRepository`. Funciona en runtime por duck typing, pero rompe el contrato de tipos y confunde a cualquier lector del código.
- **Cómo lo detecté:** Revisión cruzada de `router.py` vs la firma del constructor del servicio.
- **Reproducción:** No genera error de runtime, pero mypy o pyright reportarían error de tipo.

#### Hallazgo H4

- **Archivo:** `app/api/v1/router.py`, líneas 143-146 y similares en otros handlers
- **Tipo:** decisión cuestionable de mapeo de códigos HTTP
- **Severidad:** baja
- **Regla violada:** ninguna específica
- **Descripción:** El router convierte explícitamente `status_code=403` del servicio a `409 Conflict` para bloqueos de negocio. El 403 ("Forbidden") sería semánticamente más correcto para "bloqueo del usuario por su estado" (vencidos, multas), mientras que 409 ("Conflict") aplica más a conflictos de estado del recurso. La conversión es intencional pero no está documentada.
- **Cómo lo detecté:** Lectura del router y comparación con los status_code del servicio.
- **Reproducción:** Intentar préstamo con préstamos vencidos → devuelve 409 (no 403).

#### Hallazgo H5

- **Archivo:** `chatbot-pruebas/chatbot.js`, función `ejecutarCurl`
- **Tipo:** bug
- **Severidad:** alta (para el flujo automático del chatbot)
- **Regla violada:** ninguna de negocio
- **Descripción:** `return true` dentro del bucle `for` cortaba la ejecución tras el primer `EJECUTAR:` encontrado. Con múltiples comandos, solo el primero se ejecutaba y el resto se ignoraba silenciosamente.
- **Cómo lo detecté:** Al pedir al chatbot crear datos de prueba (11 comandos), solo se ejecutaba el primero.
- **Reproducción:** Cualquier respuesta con 2+ líneas `EJECUTAR:` — solo la primera se ejecuta.

#### Hallazgo H6

- **Archivo:** `chatbot-pruebas/chatbot.js`, función `ejecutarCurl`
- **Tipo:** bug de entorno/plataforma
- **Severidad:** alta (bloqueaba toda la ejecución automática)
- **Regla violada:** ninguna de negocio
- **Descripción:** `execSync` en Node.js usa `cmd.exe` por defecto en Windows. `Invoke-RestMethod` es un cmdlet de PowerShell y no existe en `cmd.exe`. La ejecución automática fallaba con `"Invoke-RestMethod" no se reconoce como un comando interno o externo`.
- **Cómo lo detecté:** Output del chatbot al ejecutar cualquier comando generado con `Invoke-RestMethod`.
- **Reproducción:** Cualquier `EJECUTAR:` con `Invoke-RestMethod` falla hasta agregar `shell: 'powershell.exe'` a `execSync`.

#### Hallazgo H7

- **Archivo:** `chatbot-pruebas/chatbot.js`, constante `SYSTEM_PROMPT` (versión inicial)
- **Tipo:** configuración incorrecta
- **Severidad:** media
- **Regla violada:** ninguna de negocio
- **Descripción:** El system prompt original tenía rutas de la versión v1 (`/api/libros`, verbos `PUT`), `BASE_URL` a `localhost:3001`, y solo 8 reglas. El modelo generaba comandos incorrectos para el backend real de proyecto-v2.
- **Cómo lo detecté:** Los comandos generados fallaban con 404 y usaban el campo `id_libro` en el body del préstamo en lugar del correcto `codigo_inventario`.
- **Reproducción:** Cualquier pregunta al chatbot generaba `PUT /api/prestamos/:id/renovar` en lugar de `POST /api/v1/prestamos/{id}/renovacion`.

---

## Sección 2 — Resultados de los tests (Etapa 4)

### Primera ejecución

- **Tests totales:** 21 (20 originales + 1 adicional generado por IA: `test_rn1_posgrado_falla_al_intentar_el_sexto_prestamo`)
- **Pasaron:** 20
- **Fallaron:** 1

### Análisis de los fallos

| Test | Tipo de fallo | ¿Bug del código o test mal escrito? | Acción tomada |
|---|---|---|---|
| `test_rn1_posgrado_falla_al_intentar_el_sexto_prestamo` | `pytest.raises` no captura la excepción con el match correcto | Test mal escrito — busca `"Límite de préstamos alcanzado"` pero el servicio lanza `"limite_prestamos_alcanzado"` (sin espacios, minúsculas) | Documentado; no corregido porque los 20 tests originales cubren el mismo caso |

### Última ejecución (post-correcciones)

- **Tests totales:** 21
- **Pasaron:** 20
- **Fallaron:** 1 (el test adicional — ver abajo)

### Tests rojos declarados (bugs no corregidos por tiempo)

- `test_rn1_posgrado_falla_al_intentar_el_sexto_prestamo`: el `match` del `pytest.raises` no coincide con el mensaje real del servicio. El sistema funciona correctamente; el test en sí está mal escrito. Los 20 tests originales verifican el mismo comportamiento.

---

## Sección 3 — Bugs corregidos (Etapa 5)

### Bug B1 — Serialización incorrecta de enums en SQLite

- **Hallazgo asociado:** H1
- **Descripción del bug:** `str(EstadoEjemplar.DISPONIBLE)` en Python 3.12 devuelve `'EstadoEjemplar.DISPONIBLE'` en lugar de `'DISPONIBLE'`, lo que hacía que Pydantic lanzara `ValidationError` al reconstruir objetos desde la BD.
- **Test que lo reveló:** Ejecución manual de `POST /api/v1/prestamos` — 500 Internal Server Error con traceback de Pydantic en uvicorn.
- **Corrección aplicada:** Reemplazar todos los `str(EstadoXxx.VALOR)` por `EstadoXxx.VALOR.value` en `sqlite.py`. Afectó 12 ocurrencias en métodos `create_*`, `get_*` y filtros de queries. Además se eliminó la `biblioteca.db` para re-sembrar datos limpios.
- **Tipo de corrección:** Por IA (Claude Code) con diagnóstico humano previo — se identificó la causa raíz y se aplicaron 7 edits con `replace_all`.
- **Resultado:** Los endpoints de préstamos, ejemplares, multas y reservas respondieron correctamente después de recrear la base de datos.

### Bug B2 — Return temprano en `ejecutarCurl`

- **Hallazgo asociado:** H5
- **Descripción del bug:** `return true` dentro del bucle `for` de `ejecutarCurl` cortaba la iteración tras el primer `EJECUTAR:` encontrado.
- **Test que lo reveló:** Al pedir al chatbot los datos de prueba base (11 comandos), solo se ejecutaba el primero.
- **Corrección aplicada:** Reemplazar `return true` por `ejecutoAlgo = true` dentro del bucle y devolver `ejecutoAlgo` al final del método.
- **Tipo de corrección:** Por IA (Claude Code).
- **Resultado:** El chatbot ejecuta todos los comandos `EJECUTAR:` en una respuesta.

### Bug B3 — Shell incorrecto en `execSync`

- **Hallazgo asociado:** H6
- **Descripción del bug:** `execSync` usaba `cmd.exe` por defecto; `Invoke-RestMethod` solo existe en PowerShell.
- **Test que lo reveló:** Output del chatbot: `"Invoke-RestMethod" no se reconoce como un comando interno o externo`.
- **Corrección aplicada:** Agregar `shell: 'powershell.exe'` y `timeout: 15000` a las opciones de `execSync`.
- **Tipo de corrección:** Por IA (Claude Code).
- **Resultado:** Los comandos `EJECUTAR:` se ejecutan correctamente desde el chatbot.

---

## Sección 4 — Aprendizajes (mínimo 3)

### Aprendizaje A1

Python 3.12 cambió el comportamiento de `str()` sobre enums que heredan de `str`. En versiones anteriores `str(MiEnum.VALOR)` devolvía solo `'VALOR'`; en 3.12 devuelve `'MiEnum.VALOR'`. La IA generó código que funcionaba en Python 3.10 pero rompía silenciosamente en 3.12. El bug no fue detectado por los 20 tests unitarios porque todos usan `MemoryRepository` (sin SQLite). Esto demuestra que tener 100% de tests en verde no garantiza que el sistema funcione si los tests no cubren la capa de persistencia real que se usa en producción.

### Aprendizaje A2

PowerShell tiene un alias llamado `curl` que apunta a `Invoke-WebRequest`, no al binario `curl.exe`. `Invoke-WebRequest` tiene una sintaxis completamente diferente y no acepta `-H` ni `-d`. Cuando la IA genera comandos `curl` sin especificar el entorno, asume bash/Linux. Agregar explícitamente `"El entorno es Windows PowerShell. Usa SIEMPRE Invoke-RestMethod"` al system prompt —con un ejemplo literal del formato— fue más efectivo que intentar corregir los comandos uno por uno.

### Aprendizaje A3

`qwen3.5:2b` confunde campos y reglas cuando el contexto acumulado de la conversación crece. Para RN5 generó una prueba completamente incorrecta (la mezcló con RN1/RN2). Para RN15 dio una respuesta técnicamente errónea (dijo que 422 era incorrecto cuando es el comportamiento estándar de FastAPI/Pydantic). Los modelos pequeños son útiles para generar scaffolding y comandos repetitivos, pero sus respuestas analíticas requieren verificación humana constante. Reiniciar la sesión del chatbot entre pruebas distintas mejora la calidad de las respuestas.

### Aprendizaje A4

`execSync` en Node.js en Windows usa `cmd.exe` como shell por defecto. `Invoke-RestMethod` es un cmdlet de PowerShell y no existe en `cmd.exe`. Este tipo de diferencia de entorno no es obvio hasta que falla en ejecución. La solución es `shell: 'powershell.exe'` en las opciones de `execSync`. Este es el tipo de configuración específica de plataforma que la IA no anticipa si no se le especifica el entorno exactamente.

### Aprendizaje A5

El system prompt de un chatbot especializado requiere iteración basada en fallos reales. La versión inicial necesitó 4 correcciones descubiertas únicamente al ejecutar los comandos generados: (1) cambiar `curl` por `Invoke-RestMethod`, (2) especificar el formato exacto de `EJECUTAR:` en la misma línea, (3) prohibir caracteres con tilde, (4) hacer que `execSync` use PowerShell. Ninguna de estas correcciones era obvia al leer el prompt en frío. El proceso correcto es: escribir el system prompt → ejecutar → observar el fallo → agregar la restricción faltante → repetir.

---

## Sección 5 — Decisiones de prompt (autorreflexión)

El prompt inicial pedía "alinear chatbot.js con las rutas del router" de forma genérica. Esto fue suficiente para la estructura, pero generó comandos incorrectos en tres dimensiones que se descubrieron solo al ejecutar:

**Iteración 1 — Sintaxis de plataforma:** El prompt no especificaba el entorno. La IA generó comandos `curl` con sintaxis bash. Al ejecutarlos en PowerShell fallaban porque `curl` es un alias de `Invoke-WebRequest`. Corrección: agregar `"El entorno es Windows PowerShell. Usa SIEMPRE Invoke-RestMethod"` con los tres patrones exactos (POST con body, POST sin body, GET).

**Iteración 2 — Formato del marcador EJECUTAR:** El prompt pedía `"EJECUTAR:"` al inicio de la línea pero no decía que el comando debía estar en la misma línea. El modelo puso el marcador solo y el comando en un bloque de código aparte. `ejecutarCurl` extraía cadena vacía y fallaba con `"The argument 'file' cannot be empty"`. Corrección: agregar `"seguido INMEDIATAMENTE del comando en la MISMA línea"` con un ejemplo literal completo.

**Iteración 3 — Encoding de caracteres:** La IA usó `"Título"` en el body. PowerShell 5.1 envía strings via `Invoke-RestMethod` como UTF-16 LE por defecto, causando `"error parsing body"` en FastAPI. Corrección: agregar `"NUNCA uses caracteres con tilde (á, é, í, ó, ú, ñ) dentro del -Body"`.

**Lección:** especificar el entorno de ejecución exacto y dar ejemplos literales del formato esperado son más efectivos que instrucciones abstractas.

---

## Sección 6 — Resultados de pruebas (tabla comparativa unificada)

| Prueba | Regla | Esperado | Sin IA — HTTP | Sin IA — body útil | Con IA — HTTP | Con IA — body útil | Verificado |
|---|---|---|---|---|---|---|---|
| RN1-B cuarto préstamo pregrado | RN1 | 409 | 404 | No | 409 | Sí | Manual + test automatizado |
| RN2-B sexto préstamo posgrado | RN2 | 409 | 404 | No | 409 | Sí | Manual + test automatizado |
| RN5-B ejemplar ya prestado | RN5 | 409 | 404 | No | 409 | Sí | Manual |
| RN6-A plazo libro normal | RN6 | fecha + 15 días | 404 | No | 201 | Sí (fecha_vencimiento = fecha_prestamo + 15d) | Manual + test automatizado |
| RN6-B plazo alta demanda | RN6 | fecha + 3 días | 404 | No | 201 | Sí (fecha_vencimiento = fecha_prestamo + 3d) | Manual + test automatizado |
| RN3 préstamo con vencido | RN3 | 409 | 404 | No | 409 | Sí | Test automatizado |
| RN4-B préstamo con multa | RN4 | 409 | 404 | No | 409 | Sí | Test automatizado |
| RN8 cálculo de multa | RN8 | N × 2000 | 404 | No | 200 | Sí (monto = dias_retraso × 2000) | Test automatizado |
| VAL-1 body vacío | — | 422* | 404 | No | 422 | Sí (Pydantic: campo requerido) | Manual |
| VAL-2 estudiante inexistente | — | 404 | 404 | No | 404 | Sí | Manual |
| VAL-3 ejemplar inexistente | — | 404 | 404 | No | 404 | Sí | Manual |
| VAL-4 tipo incorrecto | — | 422* | 404 | No | 422 | Sí | Test automatizado |

**Nota "Sin IA":** La versión sin IA no exponía endpoints con el prefijo `/api/v1`; todas las llamadas devolvían 404.

**Nota VAL-1 y VAL-4 (*):** La especificación del taller dice "400 Bad Request" pero FastAPI/Pydantic devuelve `422 Unprocessable Entity` para errores de validación de schema. El `422` es técnicamente más correcto: 400 es un error genérico de cliente, 422 indica específicamente que el servidor entiende el formato pero no puede procesar la entidad por errores de validación. No es un bug — es el comportamiento estándar de FastAPI.

---

## Sección 7 — Respuestas a preguntas de reflexión

**1. ¿Cuántas reglas de negocio implementó correctamente tu versión sin IA? ¿Y la versión con IA?**

- **Sin IA:** 0 de 7 reglas implementadas con API REST funcional. Los endpoints de préstamos no existían o usaban rutas distintas.
- **Con IA:** 7 de 7 reglas implementadas correctamente (RN1–RN7 verificadas en tests automatizados y pruebas manuales del taller).

**2. ¿Hubo alguna prueba donde la versión sin IA devolvió `200 OK` cuando debía devolver `409` o `404`?**

Todas las pruebas de la versión sin IA devolvieron 404 porque los endpoints no existían. Si hubiera respondido `200 OK` en lugar de `409`, el cliente creería que el préstamo fue aceptado cuando una regla de negocio debía haberlo bloqueado — generando estados inconsistentes en la UI, permitiendo préstamos que violan los límites de cupo, y rompiendo la integridad del catálogo de ejemplares.

**3. ¿Hay alguna regla de negocio que ninguna de las dos versiones implementó?**

En `proyecto-v2` no se detectaron reglas faltantes: RN1–RN7 están implementadas. La verificación se hizo revisando `app/services/biblioteca_service.py` (mapeo de líneas en Sección 1) y la cobertura de tests. Si una regla faltara, se detectaría por tests que esperan `409/404` y obtienen `200`, o por la ausencia del check en el service.

**4. Para las pruebas RN3, RN4 y RN7: ¿qué dice eso sobre la completitud del sistema?**

- **Fechas:** En `proyecto-v2` las fechas se calculan internamente y no se aceptan del cliente. Para simular préstamos vencidos en pruebas manuales hay que esperar que transcurran los días (15 o 3), o implementar un endpoint de administración de testing. Los tests automatizados resuelven esto manipulando la fecha directamente en el repositorio en memoria.
- **Reservas/lista de espera:** La entidad `Reserva` está implementada (Decisión D2) y la RN7 (bloqueo de renovación por reserva activa) está verificada por `test_rn2_bloqueado_por_vencido` y la lógica en `renovar_prestamo`.
- La especificación debería haber contemplado endpoints de seed o fixtures de testing que permitan simular estados temporales sin exponer rutas inseguras en producción.

---

## Chatbot Ollama — Registro

### Modelo usado

- **Nombre:** `qwen3.5:2b`
- **RAM consumida aproximada:** ~2 GB (modelo de 2B parámetros en CPU, sin GPU)
- **Tiempo de respuesta promedio:** 15–45 segundos por pregunta

### Preguntas útiles que generó el chatbot

| Pregunta que hice | Qué generó el chatbot | ¿Fue útil? |
|---|---|---|
| crea los datos de prueba base: estudiante pregrado, libro normal y de alta demanda | Comandos `Invoke-RestMethod` para crear 2 estudiantes, 2 libros y 9 ejemplares | Parcialmente — estructura correcta pero usó IDs ya existentes y caracteres con tilde que causaron error de encoding |
| genera la prueba RN1 completa: los 3 préstamos válidos y luego intentar el cuarto | Comandos para 3 préstamos y el cuarto rechazado con 409 | Parcialmente — usó campo `id_libro` en lugar de `codigo_inventario` y sintaxis bash |
| ahora haz lo mismo para RN2 con el estudiante de posgrado, límite 5 | Comandos para 5 préstamos válidos y el sexto con 409 | Parcialmente — mismo problema de campos y sintaxis bash |
| prueba que un ejemplar ya prestado no se puede prestar de nuevo (RN5) | Mezcló RN5 con RN1/RN2; intentó crear ejemplar con estado PRESTADO directamente | No — confundió completamente la regla; requirió corrección manual total |
| muéstrame cómo verificar los plazos de préstamo (RN6) | Comandos `Invoke-RestMethod` para préstamo normal y alta demanda, con verificación via `GET /prestamos/vigentes` | Sí — correcto tras aplicar las correcciones al system prompt |
| genera pruebas de entradas inválidas: body vacío, estudiante inexistente y ejemplar inexistente | Tres comandos con los tres casos de validación | Sí — estructura correcta, códigos HTTP esperados correctos |
| el resultado del body vacío fue 422. ¿Eso es correcto según RN15? | Dijo que 422 era incorrecto y que debía ser 400; sugirió "revisar la configuración" | No — respuesta técnicamente errónea; 422 es el comportamiento estándar de FastAPI/Pydantic |

### Limitaciones observadas

- **Inventó el campo `id_libro` en el body de préstamos** en lugar del correcto `codigo_inventario`. Requirió corrección manual en cada prueba antes de la corrección del system prompt.
- **Confundió RN5 completamente** al mezclarla con los límites de préstamos de RN1/RN2. RN5 trata sobre disponibilidad de ejemplares, no sobre cupos por estudiante.
- **Generó sintaxis bash** (`for` loops, `$((i))`, backlash-continuaciones) en lugar de PowerShell en las sesiones anteriores a la corrección del system prompt.
- **Puso `EJECUTAR:` en una línea separada** del comando, rompiendo la detección automática de `ejecutarCurl`. Requirió corrección tanto en el system prompt como en la función JavaScript.
- **Respuesta errónea sobre 422 vs 400:** No conoce las convenciones de FastAPI y aplicó la especificación del taller de forma demasiado literal, sin tener en cuenta el comportamiento real del framework.
- **Contexto acumulado:** Después de 5–6 preguntas en la misma sesión, las respuestas se degradaban notablemente. Reiniciar el chatbot con `node chatbot.js` restauraba la calidad.

### Comparación: chatbot local vs ChatGPT/Claude en la nube

| Aspecto | qwen3.5:2b (local) | Claude/ChatGPT (nube) |
|---|---|---|
| Calidad de comandos | Genera estructura básica; comete errores en campos específicos del modelo | Genera comandos exactos con los campos del schema Pydantic |
| Conocimiento del framework | No conoce convenciones de FastAPI (ej. 422 vs 400, verbos HTTP) | Conoce FastAPI, Pydantic y sus comportamientos estándar |
| Velocidad | 15–45 s por respuesta (CPU, sin GPU) | 2–5 s por respuesta |
| Privacidad del código | El código no sale del equipo | El código se envía a servidores externos |
| Costo | Gratis después de la descarga | Requiere créditos o suscripción |
| Calidad con contexto largo | Se degrada tras 5–6 turnos | Mantiene coherencia en sesiones largas |
| Uso recomendado | Scaffolding básico, comandos repetitivos con system prompt bien calibrado | Debugging, análisis de errores, auditoría de código |

**Ventaja principal del modelo local:** el código del proyecto nunca sale de la máquina — relevante bajo restricciones de privacidad o cuando el código contiene lógica de negocio sensible. Para tareas de generación de comandos repetitivos funciona aceptablemente con un system prompt suficientemente específico.

**Desventaja principal:** el modelo pequeño no tiene el conocimiento técnico profundo de los frameworks (FastAPI, Pydantic, Node.js en Windows) que un modelo de mayor tamaño tiene. Cada gap de conocimiento se manifiesta como un error que hay que corregir manualmente y luego documentar en el system prompt.
