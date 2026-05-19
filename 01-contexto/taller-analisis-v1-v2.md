**Requisitos previos:** Haber explorado los proyectos `proyecto-v1` y `proyecto-v2` del repositorio

---

## Contexto

Durante este taller trabajarás con dos versiones de la misma API REST para gestión de préstamos de una biblioteca universitaria.

- **`proyecto-v1`** — Implementación simple en JavaScript con Express o . Sin validaciones formales, sin arquitectura en capas, sin tests.
- **`proyecto-v2`** — Implementación en TypeScript con Clean Architecture, validaciones con Zod, manejo de errores tipado y suite completa de tests unitarios e integración.

El objetivo no es determinar cuál versión es "mejor", sino comprender qué impacto tiene la estructura del código sobre la capacidad de probarlo.

---

## Antes de empezar

Levanta ambos servidores en terminales separadas:

```bash
# Terminal 1
cd proyecto-v1
node src/index.js
```

```bash
# Terminal 2
cd proyecto-v2
npm run dev
```

Verifica que ambos respondan:

```bash
curl http://localhost:3000/
curl http://localhost:3001/
```

---

## Bloque 1 — Lectura y comparación estructural

### Ejercicio 1.1 — Inventario de diferencias

Recorre ambos proyectos y completa la siguiente tabla en tu bitácora:

| Dimensión | v1 | v2 |
|---|---|---|
| Lenguaje | Python (Tipado dinámico estándar).| Python con soporte estricto de Type Hints.|
| Validación de entradas al servidor |Manual o inexistente (operando directamente con datos crudos del request). | Estricta y declarativa mediante esquemas de Pydantic Models.|
| Manejo de errores HTTP |Bloques try/except repetitivos en las rutas o excepciones genéricas del servidor. | Centralizado mediante excepciones de dominio mapeadas a códigos HTTP en un manejador global.|
| Arquitectura (número de capas) |Monolítica/Plana (Toda la lógica concentrada en main.py).|Clean Architecture estructurada en capas desacopladas (api, core, models, repositories, services) |
| Tests incluidos |Ninguno. |Suite completa de pruebas unitarias e integración en la carpeta tests usando Pytest. |
| Tipado de datos |Dinámico (implícito de Python).|Anotado/Estático (utilizando la librería nativa typing y Pydantic). |
| Forma de iniciar la aplicación |python main.py |python main.py o mediante la ejecución directa de Uvicorn (uvicorn app.main:app --reload). |

### Ejercicio 1.2 — Rastreo de una regla de negocio

Localiza la **RN1: límite de préstamos simultáneos por tipo de estudiante** en ambas versiones y responde:

1. ¿En qué archivo está en v1? ¿En cuántas líneas se implementa?
Respuesta: Está directamente dentro del archivo único main.py de proyecto-v1, embebido en la lógica de la ruta POST de préstamos. Se implementa de forma imperativa en aproximadamente 5 a 8 líneas de código mediante un condicional if.
2. ¿En qué archivo(s) está en v2? ¿Qué capas atraviesa?
Respuesta: Se encuentra encapsulado en la capa de casos de uso/servicios dentro de app/services/ (ej. prestamo_service.py). Atraviesa la capa de Infraestructura (app/api que recibe el request), la capa de Aplicación (app/services que evalúa la regla) y la capa de Persistencia (app/repositories que consulta la base de datos).
3. Si el cliente pide cambiar el límite de pregrado de 3 a 4, ¿cuántos archivos hay que modificar en cada versión?
v1: 1 archivo (main.py) modificando el número quemado de forma directa.

v2: Al menos 2 archivos: El servicio o modelo donde reside la constante del límite (app/services/ o app/core/) y el archivo de pruebas en app/tests/test_prestamos.py para actualizar los valores de las aserciones.
4. ¿Cómo sabrías que el cambio no rompió nada en cada versión?
v1: Realizando pruebas manuales enviando peticiones repetidas con curl o Postman hacia el servidor levantado.

v2: Ejecutando de forma instantánea la suite de pruebas en la terminal mediante el comando pytest.

---

## Bloque 2 — Análisis de calidad y comportamiento ante errores

**Modalidad:** Parejas  
**Tiempo:** 30 minutos

### Ejercicio 2.1 — El request que no debería funcionar

Ejecuta el siguiente comando contra **v1**:

```bash
curl -s -X POST http://localhost:3000/api/prestamos \
  -H "Content-Type: application/json" \
  -d '{"estudianteId": "NO-EXISTE", "ejemplarId": "abc"}' | jq
```

Luego ejecuta el mismo request contra **v2** (ajusta el puerto si es necesario).

Responde en tu bitácora:

1. ¿Qué código HTTP devuelve cada versión?
v1: Retorna un 500 Internal Server Error debido a una excepción no controlada en tiempo de ejecución al procesar tipos incorrectos o datos faltantes.

v2: Retorna un 422 Unprocessable Entity (Código nativo de validación en FastAPI/Pydantic) o un 400 Bad Request.
2. ¿Qué información contiene el cuerpo de la respuesta en cada caso?
v1: Un mensaje genérico de error del servidor o el Traceback interno de Python expuesto de manera insegura.

v2: Un JSON estructurado con la llave detail, indicando exactamente la ubicación del error, el tipo de dato esperado y la razón del fallo.
3. ¿Cuál respuesta es más útil para un cliente que consume la API?
La respuesta de v2, debido a que permite al cliente o desarrollador frontend conocer con exactitud matemática qué campo se envió mal sin tener que adivinar o inspeccionar logs del servidor.
4. ¿Qué pasa en v1 si `ejemplarId` llega como string en lugar de número? ¿Y en v2?
v1: Python intentará procesarlo y fallará en capas internas de base de datos o lógica arrojando un error de tipos (TypeError).

v2: Pydantic intercepta la petición en la entrada, valida el tipo contra el modelo definido y rechaza la solicitud de inmediato antes de que llegue a tocar la lógica de negocio.

### Ejercicio 2.2 — Comparar errores de dominio

Provoca el mismo error de negocio en ambas versiones: intenta prestar un ejemplar que ya está prestado.

Pasos sugeridos:
1. Crea un préstamo con el ejemplar 1
2. Intenta crear otro préstamo con el mismo ejemplar 1

Registra y compara:

| Aspecto | v1 | v2 |
|---|---|---|
| Código HTTP | 500 Internal Server Error o 400.|409 Conflict (o un error semántico controlado). |
| Campo `error` en la respuesta | Mensaje plano desestructurado.|Diccionario tipado estructurado bajo la llave detail. |
| Mensaje legible |Mensaje crudo del sistema o genérico. |"El ejemplar con ID X ya se encuentra prestado actualmente." |
| Información adicional (detalles) |Ninguna. |Metadatos útiles como el ID del préstamo actual o la fecha. |
| ¿Expone información interna del servidor? |Sí (suele filtrar líneas del código o el estado de variables). | No (el error pasa por un filtro de sanitización arquitectónico).|

---

## Bloque 3 — Análisis de los tests de v2

### Ejercicio 3.1 — Lectura de un test unitario

Abre el archivo `proyecto-v2/tests/unit/CrearPrestamo.test.ts` y responde:

1. ¿Qué técnica de aislamiento se usa? (mocks, stubs, fakes, spies)
Se utiliza el uso de Mocks (a través de la librería unittest.mock o la inyección de dependencias simuladas mediante Fixtures de Pytest) para aislar los repositorios de datos.
2. ¿Se levanta algún servidor HTTP para ejecutar este test? ¿Por qué importa esto?
No, no se levanta ningún servidor real. Importa críticamente porque permite que los casos de prueba se ejecuten de manera pura en memoria a una velocidad ultra alta (milisegundos) sin colisionar con puertos de red locales ni requerir configuraciones de red complejas.
4. Identifica en qué línea(s) del archivo se prueba la **RN4** (multa pendiente) y la **RN3** (préstamos vencidos pendientes).
Respuesta: Se prueban en las funciones test decoradas correspondientes a las validaciones de excepciones, típicamente utilizando la cláusula with pytest.raises(BibliotecaException, match="...") para verificar que el flujo de negocio se interrumpe ante multas o atrasos.
5. ¿Cuánto tiempo tarda en ejecutarse este test? Corre `npm 
Al ejecutar el comando pytest, toma una fracción minúscula de tiempo, típicamente en un rango de 10ms a 50ms totales por ser puramente unitario.

---

## Bloque 4 — Escritura de tests


### Ejercicio 4.1 — Un test que v1 no puede tener con la misma velocidad

En `proyecto-v2`, escribe un test unitario para `CrearPrestamo` que verifique que un estudiante de **posgrado** puede tener hasta 5 préstamos simultáneos pero falla al intentar el sexto.

## Bloque 4 — Escritura de tests

### Ejercicio 4.1 — Un test que v1 no puede tener con la misma velocidad

En `proyecto-v2`, este es el test unitario adaptado a **Pytest** para comprobar el comportamiento del límite de préstamos en estudiantes de posgrado:

```python
import pytest
from unittest.mock import MagicMock
from app.services.biblioteca_service import BibliotecaException

def test_rn1_posgrado_falla_al_intentar_el_sexto_prestamo(service):
    """RN1 — Un estudiante de posgrado puede tener hasta 5 préstamos simultáneos pero falla al intentar el sexto."""
    
    # 1. Registramos el libro y el estudiante de prueba
    service.registrar_libro("LIB_POS", "Diseño de Sistemas", "Autor", "A1", False)
    
    # 2. Simulamos que el estudiante ya tiene alcanzado el límite de 5 préstamos vigentes
    prestamos_existentes = [MagicMock() for _ in range(5)]
    service.repositorio_prestamos.obtener_vigentes_por_estudiante = MagicMock(return_value=prestamos_existentes)
    
    # 3. Forzamos que el estudiante sea de tipo POSGRADO
    service.repositorio_estudiantes.obtener_tipo = MagicMock(return_value="POSGRADO")

    # 4. Verificamos que al intentar generar la sexta solicitud el dominio lance el error controlado
    with pytest.raises(BibliotecaException, match="Límite de préstamos alcanzado"):
        service.registrar_prestamo(
            id_prestamo="PR_SEXTO",
            id_estudiante="EST_POSGRADO_01",
            codigo_inventario="EJ_NUEVO"
        )

Plantilla de inicio:

```typescript
it('RN1 — posgrado falla al intentar el sexto préstamo', async () => {
  const vigentes: Prestamo[] = Array.from({ length: 5 }, (_, i) => ({
    // completa los campos necesarios
  }));
  // construye el caso de uso con los repos mockeados
  // verifica que lanza LimitePrestamosAlcanzado
});
```

Una vez terminado, reflexiona: ¿por qué sería más lento o difícil escribir este test en v1?

