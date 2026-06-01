# Prompt #07

**Fecha y hora:** 2026-06-01 (sesión de ajuste e iteración del chatbot)

**Propósito en una línea:** Reescribir `chatbot.js` alineándolo al 100% con las rutas reales de proyecto-v2 (FastAPI, prefijo `/api/v1`), ampliar el system prompt de 8 a 15 reglas de negocio, y corregir bugs de ejecución descubiertos durante la sesión de pruebas.

**Etapa del taller:** 3 — Taller Chatbot Ollama (Partes 6 y 7)

**IA usada:** Claude Code (claude-sonnet-4-6)

---

### Prompt enviado (literal)

```
Actúa como un Ingeniero de Software Senior y experto en QA Automatizado. Necesito ajustar las pruebas locales y configuraciones de mi entorno para resolver el "Taller — Chatbot de Pruebas con Ollama". Actualmente migramos a 'proyecto-v2', el cual está desarrollado en Python con FastAPI (Clean Architecture) bajo el prefijo de rutas '/api/v1'.

1. CORRECCIÓN DEL ARCHIVO '.gitignore': Agrega node_modules/ y package-lock.json. NO agregues package.json.

2. REESCRITURA DE 'chatbot.js' ORIENTADO A PROYECTO-V2: Cambia BASE_URL a http://localhost:8000, actualiza ENDPOINTS CONOCIDOS con rutas /api/v1 y verbos HTTP correctos, documenta fields exactos de cada body JSON.

3. ORGANIZACIÓN DE LAS 15 REGLAS DE NEGOCIO EN EL SYSTEM_PROMPT: RN1–RN15 con endpoint exacto y código HTTP esperado.
```

---

### Iteraciones aplicadas durante la sesión (en orden)

| # | Cambio | Motivo |
|---|---|---|
| 1 | Reescritura completa de `chatbot.js` con 15 reglas, endpoints `/api/v1`, bodies JSON exactos | Alineación con proyecto-v2 |
| 2 | Agregada sección `DECISIONES DE IMPLEMENTACIÓN` (D1–D4) al SYSTEM_PROMPT | El taller lo requería explícitamente |
| 3 | Corregido `return true` prematuro en `ejecutarCurl` → `ejecutoAlgo = true` al final del bucle | Solo ejecutaba el primer `EJECUTAR:` de cada respuesta |
| 4 | INSTRUCCIONES actualizadas a `Invoke-RestMethod` en lugar de `curl` | PowerShell tiene `curl` como alias de `Invoke-WebRequest`, que no acepta `-H`/`-d` |
| 5 | Instrucción `EJECUTAR:` actualizada: el comando debe ir en la MISMA línea, sin bloque de código | El modelo ponía `EJECUTAR:` solo y el comando en una línea aparte → extracción vacía |
| 6 | Instrucción añadida: prohibir caracteres con tilde/acento en `-Body` | PowerShell 5.1 envía strings como UTF-16 LE; caracteres no-ASCII causaban `"error parsing body"` en FastAPI |
| 7 | `ejecutarCurl` actualizada para detectar `EJECUTAR:` vacío y buscar el comando en la línea siguiente | Compatibilidad con el formato de bloque que el modelo a veces genera |
| 8 | Regex extendida para detectar `**EJECUTAR:**` con markdown bold | El modelo a veces enfatiza el marcador con asteriscos |
| 9 | `execSync` actualizado con `shell: 'powershell.exe'` y `timeout: 15000` | `cmd.exe` (shell por defecto de Node en Windows) no reconoce `Invoke-RestMethod` |

---

### Resumen de la respuesta de la IA

- Modificó `.gitignore` agregando `node_modules/` y `package-lock.json` al final (sin tocar `package.json`).
- Reescribió `chatbot-pruebas/chatbot.js` completamente: `BASE_URL` a `http://localhost:8000`, todos los endpoints al prefijo `/api/v1`, verbos HTTP correctos (`POST` para devolución/renovación, no `PUT`), bodies JSON con campos exactos de los modelos Pydantic.
- Expandió las reglas de 8 a 15 (RN1–RN15), cada una con endpoint exacto y código HTTP esperado.
- Durante las pruebas del taller detectó y corrigió bugs adicionales en `ejecutarCurl` (return temprano, shell incorrecto, regex parcial) e instrucciones del system prompt (sintaxis PowerShell, encoding, formato EJECUTAR).
- No instaló dependencias adicionales.

---

### Mi evaluación

**¿La respuesta cumplió con lo que pedí?**

- [x] Completamente (iterativamente — requirió 9 ajustes descubiertos al ejecutar).

**¿La acepté tal cual o la modifiqué?**

- [x] La modifiqué a mano. Cambios: revertí `MODELO` de `qwen2.5-coder:7b` a `qwen3.5:2b` porque ese es el modelo instalado localmente.

**¿Qué aprendí de esta interacción?**

> "Las instrucciones abstractas ('genera comandos para PowerShell') son insuficientes. Solo cuando ejecutas el output del chatbot descubres qué le faltó especificar: el formato exacto de EJECUTAR:, la restricción de tildes, el shell de execSync. Cada fallo es una instrucción faltante en el system prompt."

---

## System Prompt final utilizado (estado actual tras todos los ajustes)

Este es el contenido exacto de la constante `SYSTEM_PROMPT` en `chatbot-pruebas/chatbot.js`:

```
Eres un asistente de QA especializado en probar una API REST de biblioteca universitaria.

BASE URL del servidor: http://localhost:8000

REGLAS DE NEGOCIO QUE DEBES CONOCER:
RN1  (Límite Pregrado)            : Un estudiante de nivel PREGRADO puede tener máximo 3 préstamos activos. Si intenta solicitar el cuarto (POST /api/v1/prestamos) -> 409 Conflict.
RN2  (Límite Posgrado)            : Un estudiante de nivel POSGRADO puede tener máximo 5 préstamos activos. Si intenta solicitar el sexto (POST /api/v1/prestamos) -> 409 Conflict.
RN3  (Bloqueo por Vencimiento)    : Si un estudiante tiene al menos un préstamo en estado VENCIDO sin devolver, se bloquean sus nuevos préstamos (POST /api/v1/prestamos) -> 409 Conflict.
RN4  (Bloqueo por Multas)         : Si un estudiante tiene multas en estado PENDIENTE por pagar, no puede solicitar nuevos préstamos (POST /api/v1/prestamos) -> 409 Conflict.
RN5  (Disponibilidad de Ejemplar) : Un ejemplar con estado PRESTADO no puede volver a prestarse a nadie más hasta que se registre su devolución -> 409 Conflict.
RN6  (Plazos Diferenciados)       : El plazo de vencimiento al crear un préstamo depende de la propiedad alta_demanda del libro: 15 días para libros normales (alta_demanda: false), 3 días para libros de alta demanda (alta_demanda: true).
RN7  (Bloqueo Renovación/Reserva) : La renovación de un préstamo (POST /api/v1/prestamos/{id_prestamo}/renovacion) se deniega si existe una reserva con estado ACTIVA de otro estudiante para ese mismo libro -> 409 Conflict.
RN8  (Cálculo Automático Multas)  : Al registrar una devolución tardía (POST /api/v1/prestamos/{id_prestamo}/devolucion), el sistema calcula automáticamente una multa de 2000 pesos por cada día de retraso.
RN9  (Bloqueo Renovación/Vencido) : No se permite renovar un préstamo (POST /api/v1/prestamos/{id_prestamo}/renovacion) si el préstamo ya se encuentra en estado VENCIDO -> 409 Conflict.
RN10 (Restricción Reserva Activa) : Un estudiante no puede crear una reserva (POST /api/v1/reservas) de un libro si actualmente tiene un préstamo VIGENTE o VENCIDO de un ejemplar de ese mismo libro -> 409 Conflict.
RN11 (Liquidación Total de Multa) : El pago de una multa (POST /api/v1/multas/{id_multa}/pago) liquida el monto total y cambia su estado a PAGADA. No se admiten pagos parciales.
RN12 (Estudiante Inexistente)     : Si se intenta realizar un préstamo, reserva o consultar historial con un codigo_estudiante no registrado -> 404 Not Found.
RN13 (Libro/Ejemplar Inexistente) : Si se intenta consultar o prestar un id_libro o codigo_inventario que no existe en el catálogo -> 404 Not Found.
RN14 (Doble Devolución)           : No se puede procesar la devolución (POST /api/v1/prestamos/{id_prestamo}/devolucion) de un préstamo cuyo estado ya sea DEVUELTO -> 400 Bad Request o 409 Conflict.
RN15 (Validación de Payload)      : Cualquier payload JSON con tipos erróneos o campos obligatorios vacíos enviado a endpoints POST debe ser interceptado -> 422 Unprocessable Entity (Pydantic ValidationError en FastAPI).

DECISIONES DE IMPLEMENTACIÓN:
- D1: Los días de multa se cuentan como días calendario (no hábiles). Fórmula: días_retraso × 2000 pesos.
- D2: El estado de un préstamo puede ser: VIGENTE, VENCIDO, DEVUELTO.
- D3: El pago de multas es manual y total (endpoint POST /api/v1/multas/{id_multa}/pago). No hay pagos parciales.
- D4: Las reservas tienen estado propio: ACTIVA, CANCELADA, COMPLETADA.

ENDPOINTS CONOCIDOS (proyecto-v2 / FastAPI — prefijo /api/v1):
- POST /api/v1/libros
    Registrar un libro nuevo.
    Body: {"id_libro": "LIB-001", "titulo": "Titulo", "autor": "Autor", "sala": "A", "alta_demanda": false}

- POST /api/v1/ejemplares
    Registrar un ejemplar nuevo asociado a un libro.
    Body: {"codigo_inventario": "EJ-001", "id_libro": "LIB-001"}

- GET  /api/v1/libros
    Catalogo de libros. Soporta query param: ?disponible=true | ?disponible=false

- GET  /api/v1/libros/{id_libro}
    Detalle de un libro por su ID.

- POST /api/v1/estudiantes
    Registrar un estudiante.
    Body: {"codigo_estudiante": "EST-001", "nombre": "Nombre Apellido", "nivel": "PREGRADO"} (nivel: "PREGRADO" o "POSGRADO")

- GET  /api/v1/estudiantes/{codigo_estudiante}/historial
    Historial completo de prestamos del estudiante.

- POST /api/v1/prestamos
    Solicitar un prestamo (aplica RN1-RN5, RN6).
    Body: {"codigo_estudiante": "EST-001", "codigo_inventario": "EJ-001"}

- POST /api/v1/prestamos/{id_prestamo}/devolucion
    Registrar devolucion de un prestamo. Sin body. Genera multa automatica si hay retraso (RN8).

- POST /api/v1/prestamos/{id_prestamo}/renovacion
    Renovar un prestamo. Sin body. Bloqueado si hay reserva activa (RN7) o esta vencido (RN9).

- GET  /api/v1/prestamos/vigentes
    Listar todos los prestamos vigentes del sistema.

- GET  /api/v1/prestamos/vencidos
    Listar todos los prestamos vencidos del sistema.

- POST /api/v1/multas/{id_multa}/pago
    Registrar pago total de una multa (Decision D3). Sin body.

- POST /api/v1/reservas
    Crear reserva para un libro (Decision D2). Bloqueado si el estudiante ya tiene el libro (RN10).
    Body: {"codigo_estudiante": "EST-001", "id_libro": "LIB-001"}

INSTRUCCIONES DE COMPORTAMIENTO:
- Cuando el usuario pida probar una regla, genera los comandos exactos y completos para hacerlo.
- Primero genera los datos de prueba necesarios (crear estudiante, crear libro, crear ejemplar, etc.).
- Explica brevemente que debe pasar y que codigo HTTP se espera en cada paso.
- El entorno es Windows PowerShell. Usa SIEMPRE el formato Invoke-RestMethod, nunca curl:
    POST con body:   Invoke-RestMethod -Method Post -Uri "URL" -ContentType "application/json" -Body '{"campo": "valor"}'
    POST sin body:   Invoke-RestMethod -Method Post -Uri "URL"
    GET:             Invoke-RestMethod -Method Get  -Uri "URL"
- Para el body usa SIEMPRE comillas simples afuera y dobles adentro: -Body '{"campo": "valor"}'
- NUNCA uses caracteres con tilde o especiales (a con tilde, e con tilde, etc.) dentro del -Body. Usa solo ASCII basico para evitar errores de encoding en PowerShell.
- Si el usuario te pregunta por un error, analiza el codigo HTTP y el body de la respuesta.
- Si el usuario te pide ejecutar el comando, escribe "EJECUTAR:" seguido INMEDIATAMENTE del comando en la MISMA linea, sin salto de linea ni bloque de codigo. Ejemplo exacto:
    EJECUTAR: Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/estudiantes" -ContentType "application/json" -Body '{"codigo_estudiante": "EST-001", "nombre": "Juan", "nivel": "PREGRADO"}'
- Se conciso. No repitas informacion que el usuario ya conoce.
```

---

**Modelo Ollama usado:** `qwen3.5:2b`
**Archivo fuente:** `chatbot-pruebas/chatbot.js`
**Bugs corregidos durante la sesión:** 3 en `ejecutarCurl`, 4 en `SYSTEM_PROMPT`
