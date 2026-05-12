# API REST Biblioteca Universitaria - Versión 1

Esta es una API REST construida con FastAPI para gestionar una biblioteca universitaria. Los datos se almacenan en memoria.

## Instalación

1. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Ejecución

Ejecuta el servidor con:
```
uvicorn main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`.

## Documentación

Visita `http://127.0.0.1:8000/docs` para la documentación interactiva de Swagger.

## Endpoints

- `GET /libros`: Lista todos los libros.
- `POST /prestamos?libro_id={id}&usuario={usuario}`: Crea un préstamo.
- `PUT /prestamos/{id}/devolver`: Devuelve un libro.
- `GET /prestamos`: Lista préstamos vigentes.