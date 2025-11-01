from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os

class Settings(BaseSettings):
    """Configuración de la aplicación"""

    # Database
    DATABASE_URL: str = Field(default="mysql+pymysql://username:password@localhost/finance_db")

    # JWT
    SECRET_KEY: str = Field(default="your-super-secret-key-change-this-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    # API
    API_HOST: str = Field(default="localhost")
    API_PORT: int = Field(default=8000)
    DEBUG: bool = Field(default=True)

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000", "http://localhost:8080"])

    class Config:
        env_file = ".env"
        case_sensitive = False

# Crear instancia global de configuración
settings = Settings()