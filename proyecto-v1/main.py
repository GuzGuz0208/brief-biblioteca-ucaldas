from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI(title="API Biblioteca Universitaria", version="1.0.0")

# Modelos
class Libro(BaseModel):
    id: int
    titulo: str
    autor: str
    disponible: bool = True

class Prestamo(BaseModel):
    id: int
    libro_id: int
    usuario: str
    fecha_prestamo: str
    fecha_devolucion: Optional[str] = None

# Datos en memoria
libros = [
    Libro(id=1, titulo="El Quijote", autor="Miguel de Cervantes"),
    Libro(id=2, titulo="Cien años de soledad", autor="Gabriel García Márquez"),
    Libro(id=3, titulo="1984", autor="George Orwell"),
]

prestamos = []

# Endpoints
@app.get("/libros", response_model=list[Libro])
def listar_libros():
    """Lista todos los libros disponibles."""
    return libros

@app.post("/prestamos", response_model=Prestamo)
def crear_prestamo(libro_id: int, usuario: str):
    """Crea un préstamo para un libro si está disponible."""
    libro = next((l for l in libros if l.id == libro_id), None)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    if not libro.disponible:
        raise HTTPException(status_code=400, detail="Libro no disponible")
    
    libro.disponible = False
    prestamo_id = len(prestamos) + 1
    fecha_prestamo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prestamo = Prestamo(
        id=prestamo_id,
        libro_id=libro_id,
        usuario=usuario,
        fecha_prestamo=fecha_prestamo
    )
    prestamos.append(prestamo)
    return prestamo

@app.put("/prestamos/{prestamo_id}/devolver", response_model=Prestamo)
def devolver_libro(prestamo_id: int):
    """Devuelve un libro prestado."""
    prestamo = next((p for p in prestamos if p.id == prestamo_id and p.fecha_devolucion is None), None)
    if not prestamo:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado o ya devuelto")
    
    fecha_devolucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prestamo.fecha_devolucion = fecha_devolucion
    libro = next((l for l in libros if l.id == prestamo.libro_id), None)
    if libro:
        libro.disponible = True
    return prestamo

@app.get("/prestamos", response_model=list[Prestamo])
def consultar_prestamos_vigentes():
    """Consulta los préstamos vigentes (sin devolver)."""
    return [p for p in prestamos if p.fecha_devolucion is None]