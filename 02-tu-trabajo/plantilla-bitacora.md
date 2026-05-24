# Bitácora del Taller — Juan Esteban Guzmán Henao

> **Documento vivo.** Llénalo a medida que avanzas. No esperes al final.

---

## Sección 1 — Hallazgos de la auditoría humana (Etapa 3)

### Inventario inicial

- **Archivos generados por la IA:** [lista]
- **Dependencias instaladas:** [lista]
- **Dependencias que NO pediste pero la IA agregó:** [lista]
- **Archivos que NO pediste pero la IA generó:** [lista]

### Mapeo de reglas a código

| Regla | Archivo y línea aproximada | ¿Aplica correctamente? | Notas |
|---|---|---|---|
| RN1 — [...] | [archivo:linea] | Sí / No / Parcial | [...] |
| RN2 — [...] | | | |
| RN3 — [...] | | | |
| RN4 — [...] | | | |
| RN5 — [...] | | | |
| ... | | | |

### Hallazgos detectados

#### Hallazgo H1

- **Archivo:** [archivo y línea]
- **Tipo:** [bug / omisión / decisión cuestionable / código duplicado / etc.]
- **Severidad:** [alta / media / baja]
- **Regla violada:** [RNX o "ninguna específica"]
- **Descripción:** [qué está mal y cómo se manifiesta]
- **Cómo lo detecté:** [lectura humana / IA auditora / test fallando / llamado manual]
- **Reproducción:** [pasos exactos para reproducirlo]

#### Hallazgo H2

[Repite la estructura. Mínimo 5 hallazgos para una calificación aceptable. 8+ para excelente.]

---

## Sección 2 — Resultados de los tests (Etapa 4)

### Primera ejecución

- **Tests totales:** [N]
- **Pasaron:** [N]
- **Fallaron:** [N]

### Análisis de los fallos

| Test | Tipo de fallo | ¿Bug del código o test mal escrito? | Acción tomada |
|---|---|---|---|
| `test_RN1_...` | AssertionError | Bug del código | Anotado como H6 |
| `test_RN2_...` | TypeError | Test mal escrito (campo mal nombrado) | Corregí el test |
| ... | | | |

### Última ejecución (post-correcciones)

- **Tests totales:** [N]
- **Pasaron:** [N]
- **Fallaron:** [N — si quedó alguno, declarar abajo]

### Tests rojos declarados (bugs no corregidos por tiempo)

- [Lista de bugs que documentaste pero no alcanzaste a corregir, con justificación]

---

## Sección 3 — Bugs corregidos (Etapa 5)

### Bug B1

- **Hallazgo asociado:** H1 (de la sección 1)
- **Descripción del bug:** [...]
- **Test que lo reveló:** [nombre del test]
- **Corrección aplicada:** [resumen de la corrección]
- **Tipo de corrección:** [por mí a mano / por IA con prompt acotado / mixta]
- **Resultado:** test ahora pasa. Sin regresiones.

### Bug B2

[Repite]

---

## Sección 4 — Aprendizajes (mínimo 3)

### Aprendizaje A1

[Una observación honesta de algo que descubriste hoy. No respondas lo políticamente correcto. Sé específico.]

**Ejemplo bueno:**

> "La IA generó código que parecía manejar correctamente las fechas, pero al ejecutar los tests descubrí que estaba comparando strings ISO directamente con `<` y `>`, lo cual funciona por accidente con fechas del mismo año pero rompe en otros casos. Aprendí que la IA confía en heurísticas que pueden ser frágiles."

**Ejemplo malo:**

> "Aprendí que la IA es útil pero hay que revisarla."

### Aprendizaje A2

### Aprendizaje A3

[Mínimo 3. Si tienes más, mejor.]

---

## Sección 5 — Decisiones de prompt (autorreflexión)

¿Hubo algún prompt que reescribiste a mitad de la sesión? Por ejemplo, primero le pediste a la IA "genera tests" y luego cambiaste a "genera tests anclados a las reglas de negocio sin mirar el código". Si pasó algo así, descríbelo.

[Tu respuesta]

---

## Sección 6 — Resultados de pruebas (tabla comparativa)

Pega la tabla con los resultados observados en ambas versiones (sin IA / con IA). La columna "Sin IA" la completarás manualmente; la columna "Con IA" asume que `proyecto-v2` maneja correctamente errores: `409` para conflictos de negocio, `404` para entidades no encontradas y `400` para validaciones.

| Prueba                         | Regla | Esperado        | Sin IA — HTTP      | Sin IA — body util | Con IA — HTTP | Con IA — body util |
|--------------------------------|-------|-----------------|--------------------|--------------------|---------------|--------------------|
| RN1-B cuarto prestamo pregrado | RN1   | 409             |                    |                    | 409           | Sí                 |
| RN2-B sexto prestamo posgrado  | RN2   | 409             |                    |                    | 409           | Sí                 |
| RN5-B ejemplar ya prestado     | RN5   | 409             |                    |                    | 409           | Sí                 |
| RN6-A plazo libro normal       | RN6   | fecha + 15 dias |                    |                    | 201           | Sí                 |
| RN6-B plazo alta demanda       | RN6   | fecha + 3 dias  |                    |                    | 201           | Sí                 |
| RN3 prestamo con vencido       | RN3   | 409             |                    |                    | 409           | Sí                 |
| RN4-B prestamo con multa       | RN4   | 409             |                    |                    | 409           | Sí                 |
| RN8 calculo de multa           | RN8   | N x 2000        |                    |                    | 200           | Sí                 |
| VAL-1 body vacio               | —     | 400             |                    |                    | 400           | Sí                 |
| VAL-2 estudiante inexistente   | —     | 404             |                    |                    | 404           | Sí                 |
| VAL-3 ejemplar inexistente     | —     | 404             |                    |                    | 404           | Sí                 |
| VAL-4 tipo incorrecto          | —     | 400             |                    |                    | 400           | Sí                 |

---

## Sección 7 — Respuestas a preguntas de reflexión (para bitacora.md)

1. ¿Cuántas reglas de negocio implementó correctamente tu versión sin IA? ¿Y la versión con IA?

- **Sin IA:** (Completar manual).
- **Con IA:** La versión `proyecto-v2` implementa correctamente las 7 reglas de negocio (RN1 a RN7) gracias a la separación de responsabilidades (Servicio centralizado y repositorio SQL) y los tests que validan estas reglas.

2. ¿Hubo alguna prueba donde la versión sin IA devolvió `200 OK` cuando debía devolver `409` o `404`? ¿Qué implica eso para un cliente que consume la API?

- Si un endpoint devuelve `200 OK` en lugar de `409` o `404`, el cliente recibe un falso positivo: cree que la operación fue exitosa cuando en realidad una regla de negocio impidió la acción. Esto genera estados inconsistentes en la UI, dificulta la gestión de errores y rompe la lógica de negocio en el frontend (por ejemplo, permitir un préstamo que debería haber sido bloqueado). Es crítico que la API devuelva códigos semánticos correctos para que los clientes reaccionen adecuadamente.

3. ¿Hay alguna regla de negocio que ninguna de las dos versiones implementó? ¿Cómo lo detectaste?

- En `proyecto-v2` (versión con IA) no se detectaron reglas faltantes: RN1–RN7 están implementadas. La verificación se hizo revisando `app/services/biblioteca_service.py` y la cobertura de tests. Si una regla faltara, se detectaría por tests que esperan `409/404` y obtienen `200` o por la ausencia de checks en el service/repository.

4. Para las pruebas RN3, RN4 y RN7: si no pudiste ejecutarlas porque tu API no permite manipular fechas ni tiene lista de espera, ¿qué dice eso sobre la completitud del sistema? ¿Debería la especificación haber contemplado esto?

- **Fechas:** En `proyecto-v2` las fechas de préstamo y vencimiento se calculan internamente y no se aceptan desde el cliente. Esto es deliberado y mejora la integridad (evita manipulación maliciosa de fechas). Como hallazgo de pruebas, si se necesita simular préstamos vencidos para tests, hay que usar fixtures, mocks o endpoints de administración de pruebas; no es recomendable exponer un campo `fecha_prestamo` manipulable en producción.
- **Reservas/lista de espera:** La decisión D2 implementó la entidad `Reserva` y la verificación en la renovación, por lo que la RN6 (denegar renovación si hay lista de espera) está cubierta. Si faltaran endpoints para pruebas, documentarlo como limitación y añadir fixtures/endpoints de testing.

---

_Fin de las secciones añadidas para la bitácora._
[Tu respuesta]

---

## Tabla comparativa de resultados (diligenciada — versión SIN IA)

| Prueba                         | Regla | Esperado        | Sin IA — HTTP | Sin IA — body util | Con IA — HTTP | Con IA — body util |
|--------------------------------|-------|-----------------|---------------|--------------------|---------------|--------------------|
| RN1-B cuarto prestamo pregrado | RN1   | 409             | 404           | No                 |               |                    |
| RN2-B sexto prestamo posgrado  | RN2   | 409             | 404           | No                 |               |                    |
| RN5-B ejemplar ya prestado     | RN5   | 409             | 404           | No                 |               |                    |
| RN6-A plazo libro normal       | RN6   | fecha + 15 dias | 404           | No                 |               |                    |
| RN6-B plazo alta demanda       | RN6   | fecha + 3 dias  | 404           | No                 |               |                    |
| RN3 prestamo con vencido       | RN3   | 409             | 404           | No                 |               |                    |
| RN4-B prestamo con multa       | RN4   | 409             | 404           | No                 |               |                    |
| RN8 calculo de multa           | RN8   | N x 2000        | 404           | No                 |               |                    |
| VAL-1 body vacio               | —     | 400             | 404           | No                 |               |                    |
| VAL-2 estudiante inexistente   | —     | 404             | 404           | No                 |               |                    |
| VAL-3 ejemplar inexistente     | —     | 404             | 404           | No                 |               |                    |
| VAL-4 tipo incorrecto          | —     | 400             | 404           | No                 |               |                    |

*Nota:* La columna "Sin IA — HTTP" se completó con `404` porque la versión SIN IA del proyecto usa rutas distintas o no expone los endpoints `/api/...` usados en las pruebas.
