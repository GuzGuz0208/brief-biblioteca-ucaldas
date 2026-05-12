# Especificación Formal — Sistema de Préstamo de Libros

> **Autor:** Juan Manuel Carmona y Juan Esteban Guzmán
> **Fecha:** 05/05/2026
> **Versión:** 1.0
> **Brief de origen:** Correo de Diana Restrepo, Coordinadora de Biblioteca

> Lo que está entre corchetes `[...]` es lo que tú debes escribir.

---

## 1. Propósito del sistema

Nos piden una plataforma para gestionar el prestamo de libros en una biblioteca, nos ponenen restricciones como que hay dos tipos de usuarios pregado y postgrado la idea es que un estudiante pueda prestar un libro, Temdremos que gestionar el ciclo de vida del prestamo, aplicar restricciones requeridas, tener en cuenta las multas.

---

## 2. Alcance

**Incluido en esta versión:**

* Podremos consultar los libros por su código único, título, autor y ubicación, viendo en tiempo real cuáles ejemplares están libres.

* El sistema permitirá registrar un préstamo validando automáticamente si el estudiante cumple con el máximo de 3 libros para pregrado y 5 para posgrado.

* Se diferencian plazos según el tipo de libro, 15 días para libros normales y 3 días para los de "alta demanda".

* Al registrar que un libro vuelve, la API calculará automáticamente si tiene multa y generará la deuda de 2.000 pesos por cada día de retraso.

* El sistema impedirá nuevos préstamos si el estudiante tiene libros vencidos o multas sin pagar.

* El sistema permitirá extender el plazo (por otros 15 o 3 días) siempre y cuando el libro no tenga solicitudes pendientes de otros estudiantes.

* Opción de ver qué préstamos están activos actualmente, quiénes tienen libros vencidos y el historial completo de lo que un estudiante ha prestado antes.

* Toda la información se manejará en la memoria del servidor (momentáneamente)

**Explícitamente fuera del alcance:**

* Todo lo relacionado con los profesores investigadores, sus límites de 10 libros y 30 días se seguirá manejando de forma manual por fuera de la API.

* No habrá guardado de información a largo plazo (momentáneamente).

* No desarrollaremos la aplicación móvil ni el portal web, solo la API que los hará funcionar.

* La API calcula la multa, pero el registro del pago real del dinero y el "limpiar" esa deuda se queda fuera por ahora.

---

## 3. Modelo de datos

### Entidad: Libro

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id_libro` | `String` | sí | Identificador interno del sistema |
| `titulo` | `String` | sí | nombre del libro |
| `autor` | `String` | sí | autor del libro |
| `sala` | `String` | sí | sala donde esta el libro |
| `alta demanda` | `Boolean` | sí | determina el tiempo de prestamo |

### Entidad: Ejemplar

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `codigo-inventario` | `String` | sí | codigo de barrras del libro |
| `id_libro` | `String` | sí | Llave foranea que conecta con Libro |
| `estado` | `Enum` | sí | Valores: DISPONIBLE, PRESTADO, EXTRAVIADO. |

### Entidad: Estudiante

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `codigo-estudiante` | `String` | sí | codigo unico del estudiandnte |
| `nombre` | `String` | sí | Nombre del estudiante |
| `nivel` | `Enum` | sí | PREGRADO (máx. 3 libros) o POSGRADO (máx. 5 libros). |

### Entidad: Préstamo

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id-prestamo` | `String` | sí | identificador unico |
| `codigo_inventario` | `String` | sí | llave foranea Ejemplar |
| `codigo-estudinate` | `String` | sí | lalve foranea Estudinate |
| `fecha-prestamo` | `DateTime` | sí | fecha y hora en la que se presto el libro |
| `fecha-vencimiento` | `DateTime` | sí | fecha limite para devolver |
| `fecha-devolucion` | `DateTime` | no | fecha en la que se decocio el libro |
| `estado` | `Enum` | sí | VIGENTE, VENCIDO, o DEVUELTO. |

### Entidad: Multa

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id-multa` | `String` | sí | identificador unico de multa |
| `id-prestamo` | `String` | sí | llave foranea Prestamo |
| `codigo-estudinate` | `String` | sí | lalve foranea Estudinate |
| `dias-retraso` | `Integer` | sí | diferencia de dias entre la fecha vencimiento y devolución |
| `monto-total` | `Integer` | sí | dias de retraso multimplicado por 2.000 |
| `estado` | `Enum` | sí | PENDIENTE (bloquea al estudiante) o PAGADA |

### Diagrama de relaciones
Libro 1 --- N Ejemplar
Estudiante 1 --- N Prestamo
Ejemplar 1 --- N Prestamo (a lo largo del tiempo)
Prestamo 0..1 --- 1 Multa

---

## 4. Endpoints REST

| Método | Ruta | Propósito | Body / Query | Respuesta éxito | Códigos error posibles |
|---|---|---|---|---|---|
| `GET` | `/libros` | Consultar catálogo: permite ver todos los libros y filtrar por disponibilidad para saber qué hay en sala | Query: `?disponible=true` | `200` con lista de libros y sus ejemplares | - |
| `GET` | `/libros/:id` | Detalle de libro: ver la información técnica de un libro específico y el estado de cada uno de sus ejemplares | - | `200` con objeto de libro (título, autor, sala y ejemplares) | `404` |
| `POST` | `/prestamos` | Solicitar préstamo: registra la salida de un libro y valida cupo, multas y préstamos vencidos | `{estudiante_id, ejemplar_id}` | `201` con detalle del préstamo y fecha de devolución | `400`, `404`, `409` |
| `POST` | `/prestamos/:id/devolucion` | Registrar devolución: recibe el libro y calcula automáticamente la multa por retraso si aplica | - | `200` con resumen de devolución y monto de multa | `404` |
| `POST` | `/prestamos/:id/renovacion` | Renovar préstamo: extiende el plazo si nadie más ha solicitado ese libro | - | `200` con préstamo actualizado y nueva fecha | `400`, `404` |
| `GET` | `/prestamos/vigentes` | Ver préstamos activos: lista todos los libros que actualmente están prestados | - | `200` con lista de préstamos vigentes | - |
| `GET` | `/prestamos/vencidos` | Alertas de mora: muestra únicamente los préstamos cuya fecha de entrega ya venció | - | `200` con lista de estudiantes en mora | - |
| `GET` | `/estudiantes/:id/historial` | Historial del estudiante: consulta todos los préstamos realizados anteriormente | - | `200` con lista histórica de libros y fechas | `404` |

---

## 5. Reglas de negocio

### RN1 — Límite de préstamos por tipo de estudiante

- **Trigger:** al recibir `POST /prestamos`.
- **Condición:**
  - Estudiante de pregrado: máximo 3 préstamos con `estado = "activo"`.
  - Estudiante de posgrado: máximo 5 préstamos con `estado = "activo"`.
- **Acción si cumple:** continuar con el flujo de creación.
- **Acción si no cumple:** retornar `409 Conflict` con `{error: "limite_prestamos_alcanzado", limite: N, actuales: M}`.

### RN2 — Bloqueo por préstamos vencidos

- **Trigger:** al recibir `POST /prestamos`.
- **Condición:** el estudiante asociado no debe tener ningún préstamo con `estado = "VENCIDO"`.
- **Acción si cumple:** continuar con el flujo de creación.
- **Acción si no cumple:** retornar `403 Forbidden` con `{error: "estudiante_con_vencimientos", mensaje: "Debe devolver los libros vencidos antes de solicitar nuevos."}`.

### RN3 — Bloqueo por multas pendientes

- **Trigger:** al recibir `POST /prestamos`.
- **Condición:** el estudiante asociado no debe tener registros en la tabla de multas con `estado = "PENDIENTE"`.
- **Acción si cumple:** continuar con el flujo de creación.
- **Acción si no cumple:** retornar `403 Forbidden` con `{error: "multas_pendientes", mensaje: "El estudiante tiene multas sin pagar."}`.

### RN4 — Disponibilidad del ejemplar

- **Trigger:** al recibir `POST /prestamos`.
- **Condición:** el ejemplar escaneado (por `codigo_inventario`) debe tener su `estado = "DISPONIBLE"`.
- **Acción si cumple:** procesar préstamo y cambiar el estado del ejemplar a `"PRESTADO"`.
- **Acción si no cumple:** retornar `409 Conflict` con `{error: "ejemplar_no_disponible", estado_actual: "[estado]"}`.

### RN5 — Cálculo dinámico del plazo de vencimiento

- **Trigger:** antes de guardar en memoria un `POST /prestamos` o al aprobar un `PUT /prestamos/{id}/renovacion`.
- **Condición:** se verifica la propiedad `alta_demanda` del libro asociado al ejemplar.
- **Acción si cumple** (`es true`): la `fecha_vencimiento` se asienta sumando exactamente 3 días a la fecha actual.
- **Acción si no cumple** (`es false`): la `fecha_vencimiento` se asienta sumando exactamente 15 días a la fecha actual. No hay retorno de error HTTP para esto, es una derivación lógica.

### RN6 — Restricción de renovación por lista de espera

- **Trigger:** al recibir `PUT /prestamos/{id}/renovacion`.
- **Condición:** no debe existir ninguna solicitud en la tabla de espera con `estado = "ACTIVA"` para el `id_libro` asociado al ejemplar prestado.
- **Acción si cumple:** aumentar en 1 el contador de renovaciones y extender la fecha de vencimiento utilizando la lógica de la RN5. Retornar `200 OK`.
- **Acción si no cumple:** retornar `409 Conflict` con `{error: "renovacion_denegada", motivo: "libro_solicitado_por_tercero"}`.

### RN7 — Cálculo y generación automática de multas

- **Trigger:** al recibir `POST /prestamos/{id}/devolucion` (o PUT).
- **Condición:** la fecha actual del sistema (momento de la devolución) debe ser menor o igual a la `fecha_vencimiento`.
- **Acción si cumple:** cambiar estado del préstamo a `"DEVUELTO"` y el del ejemplar a `"DISPONIBLE"`. Retornar `200 OK` confirmando la devolución exitosa.
- **Acción si no cumple:** registrar la devolución, liberar el ejemplar y calcular `dias_retraso`. Generar automáticamente un registro de multa por `(dias_retraso * 2000)` con estado `"PENDIENTE"`. Retornar `200 OK` con `{estado: "devuelto_con_retraso", multa_generada: monto, dias_retraso: dias}`.

---

## 6. Decisiones tomadas (lo que el correo no dice)

### D1 — Cálculo de días para multa

- **Contexto:** el correo no precisa si los días de retraso son calendario o hábiles.
- **Decisión:** usar días calendario.
- **Justificación:** es la interpretación más simple y se alinea con lo que la mayoría de bibliotecas hacen.

### D2 — Implementación de una lista de espera para reservas

- **Contexto:** el correo menciona que la renovación solo es posible si nadie más ha solicitado el libro, pero no explica cómo un estudiante puede pedir un libro que ya está prestado.
- **Decisión:** se implementará una funcionalidad de reserva o lista de espera. Cuando un libro no esté disponible, el estudiante podrá quedar registrado en una lista de espera asociada a ese libro.
- **Justificación:** esta decisión permite validar correctamente la regla de renovación. Si existe al menos una reserva activa sobre ese libro, el sistema bloqueará automáticamente la renovación del préstamo actual.

### D3 — Registro manual de pago de multas

- **Contexto:** el sistema calcula automáticamente la multa al momento de la devolución y bloquea al estudiante, pero el correo no explica cómo se registra que esa multa ya fue pagada.
- **Decisión:** se incluirá un endpoint para que el personal de biblioteca pueda registrar manualmente el pago de la multa y limpiar la deuda del estudiante.
- **Justificación:** como en esta primera versión no habrá integración con sistemas financieros ni pasarelas de pago, la solución más práctica es permitir que el personal confirme manualmente el pago recibido.

### D4 — Alta demanda definida a nivel de libro

- **Contexto:** no se especifica si la categoría de alta demanda aplica a cada ejemplar individual o al título completo del libro.
- **Decisión:** la condición de alta demanda se aplicará al libro como título general, no a cada ejemplar por separado.
- **Justificación:** esto evita inconsistencias entre ejemplares del mismo libro, simplifica la lógica del sistema y hace más clara la regla para los estudiantes y para el personal de biblioteca.

### D5 — Uso de códigos existentes como identificadores principales

- **Contexto:** el correo menciona que los estudiantes tienen un código único y los libros un código único de inventario, pero no define si deben crearse nuevos identificadores internos.
- **Decisión:** se usarán directamente los códigos existentes del estudiante y del inventario del libro como identificadores principales dentro de la API.
- **Justificación:** esto facilita la migración desde la hoja de cálculo actual, evita duplicidad de información y permite una implementación más rápida sin necesidad de generar nuevos IDs.

---

## 7. Códigos HTTP usados

| Código | Significado | Cuándo se usa |
|---|---|---|
| `200` | OK | GET exitosos |
| `201` | Created | POST exitosos que crean recursos |
| `400` | Bad Request | Body malformado o validación fallida |
| `404` | Not Found | Recurso no existe |
| `409` | Conflict | Reglas de negocio violadas (límite alcanzado, duplicado, etc.) |
| `500` | Internal Server Error | Error no controlado del servidor |

---

## 8. Restricciones técnicas

- **Stack:** Python + FastAPI
- **Persistencia:** datos en memoria. No usar base de datos.
- **TypeScript:** No.
- **Sin autenticación** en esta versión.
- **Sin frontend** en esta versión. Solo API REST.