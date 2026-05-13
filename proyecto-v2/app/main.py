from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.router import router

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="API REST para gestionar préstamos de libros en la biblioteca",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Registrar routers
app.include_router(router)


@app.get("/", tags=["root"])
def read_root():
    """Endpoint raíz de la API."""
    return {
        "mensaje": "Bienvenido a la Biblioteca API v2",
        "version": settings.version,
        "docs": "/docs"
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {"status": "OK"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
