const readline = require("readline");
const { execSync } = require("child_process");

const BASE_URL = "http://localhost:8000";
const OLLAMA_URL = "http://localhost:11434/api/chat";
const MODELO = "qwen3.5:2b"; // cambia a llama3.2:3b si tu máquina tiene menos de 8 GB

const SYSTEM_PROMPT = `
Eres un asistente de QA especializado en probar una API REST de biblioteca universitaria.

BASE URL del servidor: ${BASE_URL}

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
RN15 (Validación de Payload)      : Cualquier payload JSON con tipos erróneos o campos obligatorios vacíos enviado a endpoints POST debe ser interceptado -> 400 Bad Request (Pydantic ValidationError).

DECISIONES DE IMPLEMENTACIÓN:
- D1: Los días de multa se cuentan como días calendario (no hábiles). Fórmula: días_retraso × 2000 pesos.
- D2: El estado de un préstamo puede ser: VIGENTE, VENCIDO, DEVUELTO.
- D3: El pago de multas es manual y total (endpoint POST /api/v1/multas/{id_multa}/pago). No hay pagos parciales.
- D4: Las reservas tienen estado propio: ACTIVA, CANCELADA, COMPLETADA.

ENDPOINTS CONOCIDOS (proyecto-v2 / FastAPI — prefijo /api/v1):
- POST /api/v1/libros
    Registrar un libro nuevo.
    Body: {"id_libro": "LIB-001", "titulo": "Título", "autor": "Autor", "sala": "A", "alta_demanda": false}

- POST /api/v1/ejemplares
    Registrar un ejemplar nuevo asociado a un libro.
    Body: {"codigo_inventario": "EJ-001", "id_libro": "LIB-001"}

- GET  /api/v1/libros
    Catálogo de libros. Soporta query param: ?disponible=true | ?disponible=false

- GET  /api/v1/libros/{id_libro}
    Detalle de un libro por su ID.

- POST /api/v1/estudiantes
    Registrar un estudiante.
    Body: {"codigo_estudiante": "EST-001", "nombre": "Nombre Apellido", "nivel": "PREGRADO"} (nivel: "PREGRADO" o "POSGRADO")

- GET  /api/v1/estudiantes/{codigo_estudiante}/historial
    Historial completo de préstamos del estudiante.

- POST /api/v1/prestamos
    Solicitar un préstamo (aplica RN1–RN5, RN6).
    Body: {"codigo_estudiante": "EST-001", "codigo_inventario": "EJ-001"}

- POST /api/v1/prestamos/{id_prestamo}/devolucion
    Registrar devolución de un préstamo. Sin body. Genera multa automática si hay retraso (RN8).

- POST /api/v1/prestamos/{id_prestamo}/renovacion
    Renovar un préstamo. Sin body. Bloqueado si hay reserva activa (RN7) o está vencido (RN9).

- GET  /api/v1/prestamos/vigentes
    Listar todos los préstamos vigentes del sistema.

- GET  /api/v1/prestamos/vencidos
    Listar todos los préstamos vencidos del sistema.

- POST /api/v1/multas/{id_multa}/pago
    Registrar pago total de una multa (Decisión D3). Sin body.

- POST /api/v1/reservas
    Crear reserva para un libro (Decisión D2). Bloqueado si el estudiante ya tiene el libro (RN10).
    Body: {"codigo_estudiante": "EST-001", "id_libro": "LIB-001"}

INSTRUCCIONES DE COMPORTAMIENTO:
- Cuando el usuario pida probar una regla, genera los comandos exactos y completos para hacerlo.
- Primero genera los datos de prueba necesarios (crear estudiante, crear libro, crear ejemplar, etc.).
- Explica brevemente qué debe pasar y qué código HTTP se espera en cada paso.
- El entorno es Windows PowerShell. Usa SIEMPRE el formato Invoke-RestMethod, nunca curl:
    POST con body:   Invoke-RestMethod -Method Post -Uri "URL" -ContentType "application/json" -Body '{"campo": "valor"}'
    POST sin body:   Invoke-RestMethod -Method Post -Uri "URL"
    GET:             Invoke-RestMethod -Method Get  -Uri "URL"
- Para el body usa SIEMPRE comillas simples afuera y dobles adentro: -Body '{"campo": "valor"}'
- Si el usuario te pregunta por un error, analiza el código HTTP y el body de la respuesta.
- Si el usuario te pide ejecutar el comando, escribe "EJECUTAR:" seguido INMEDIATAMENTE del comando en la MISMA línea, sin salto de línea ni bloque de código. Ejemplo exacto:
    EJECUTAR: Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/estudiantes" -ContentType "application/json" -Body '{"codigo_estudiante": "EST-001", "nombre": "Juan", "nivel": "PREGRADO"}'
- NUNCA uses caracteres con tilde o especiales (á, é, í, ó, ú, ñ) dentro del -Body. Usa solo ASCII básico para evitar errores de encoding en PowerShell.
- Sé conciso. No repitas información que el usuario ya conoce.
`.trim();

const historial = [{ role: "system", content: SYSTEM_PROMPT }];

async function preguntarAlModelo(mensajeUsuario) {
  historial.push({ role: "user", content: mensajeUsuario });

  const respuesta = await fetch(OLLAMA_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: MODELO,
      messages: historial,
      stream: false,
    }),
  });

  if (!respuesta.ok) {
    throw new Error(`Ollama respondió ${respuesta.status}. ¿Está corriendo? Ejecuta: ollama serve`);
  }

  const datos = await respuesta.json();
  const contenido = datos.message.content;
  historial.push({ role: "assistant", content: contenido });
  return contenido;
}

function ejecutarCurl(respuestaModelo) {
  const lineas = respuestaModelo.split("\n");
  let ejecutoAlgo = false;

  for (let i = 0; i < lineas.length; i++) {
    const linea = lineas[i];
    // Acepta: "EJECUTAR: cmd", "**EJECUTAR:** cmd", "EJECUTAR:" con cmd en la línea siguiente
    if (/^\*{0,2}EJECUTAR:\*{0,2}/i.test(linea.trim())) {
      let comando = linea.replace(/^\*{0,2}EJECUTAR:\*{0,2}/i, "").trim();
      // Si el comando está vacío, toma la siguiente línea no vacía que no sea una cerca de código
      if (!comando) {
        for (let j = i + 1; j < lineas.length; j++) {
          const sig = lineas[j].trim();
          if (sig && !sig.startsWith("```")) {
            comando = sig;
            i = j;
            break;
          }
        }
      }
      if (!comando) continue;
      console.log(`\n[EJECUTANDO]: ${comando}\n`);
      try {
        const resultado = execSync(comando, { encoding: "utf-8", timeout: 15000, shell: "powershell.exe" });
        console.log("[RESULTADO]:\n" + resultado);
      } catch (err) {
        console.log("[RESULTADO]:\n" + (err.stdout || err.message));
      }
      ejecutoAlgo = true;
    }
  }
  return ejecutoAlgo;
}

async function iniciar() {
  console.log("=== Chatbot de Pruebas — Biblioteca UCaldas (proyecto-v2) ===");
  console.log(`Modelo: ${MODELO}`);
  console.log(`Servidor: ${BASE_URL}`);
  console.log('Escribe tu pregunta. Ejemplos:');
  console.log('  "crea los datos de prueba base: estudiante pregrado, libro normal y de alta demanda"');
  console.log('  "genera la prueba RN1 completa: los 3 préstamos válidos y luego el cuarto"');
  console.log('  "ejecuta la prueba RN6 para verificar los plazos de alta demanda vs normal"');
  console.log('  "prueba que un ejemplar ya prestado no se puede prestar de nuevo (RN5)"');
  console.log('Escribe "salir" para terminar.\n');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const preguntar = () => {
    rl.question("Tú: ", async (entrada) => {
      if (entrada.toLowerCase() === "salir") {
        console.log("Hasta luego.");
        rl.close();
        return;
      }

      if (!entrada.trim()) {
        preguntar();
        return;
      }

      try {
        const respuesta = await preguntarAlModelo(entrada);
        console.log(`\nChatbot: ${respuesta}\n`);
        ejecutarCurl(respuesta);
      } catch (err) {
        console.error(`Error: ${err.message}`);
      }

      preguntar();
    });
  };

  preguntar();
}

iniciar();
