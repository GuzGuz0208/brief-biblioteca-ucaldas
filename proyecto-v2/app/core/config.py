from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    app_name: str = "Biblioteca API v2"
    version: str = "2.0.0"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
