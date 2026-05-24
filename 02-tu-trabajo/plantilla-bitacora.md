# Bitácora del Taller — [Tu nombre]

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

¿Hubo algún momento en que la IA "dijo que terminó" pero al verificar tú descubriste que no? Descríbelo.

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
