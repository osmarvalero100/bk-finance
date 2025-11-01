#!/usr/bin/env python3
"""
Script de configuración inicial para la API de Finanzas Personales
"""

import os
import sys
from app.core.database import engine, Base

def setup_database():
    """Crear tablas en la base de datos"""
    try:
        print("Creando tablas en la base de datos...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        sys.exit(1)

def check_requirements():
    """Verificar si las dependencias están instaladas"""
    try:
        import fastapi
        import sqlalchemy
        import pymysql
        import uvicorn
        print("✅ Todas las dependencias están instaladas")
    except ImportError as e:
        print(f"❌ Faltan dependencias: {e}")
        print("Ejecuta: pip install -r requirements.txt")
        sys.exit(1)

def check_env_file():
    """Verificar archivo .env"""
    if not os.path.exists('.env'):
        print("⚠️  Archivo .env no encontrado")
        print("Creando archivo .env con configuración por defecto...")
        with open('.env', 'w') as f:
            f.write("""# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost/finance_db

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
DEBUG=True
API_HOST=localhost
API_PORT=8000
""")
        print("✅ Archivo .env creado")
        print("⚠️  Edita el archivo .env con tus credenciales de base de datos")
    else:
        print("✅ Archivo .env encontrado")

def main():
    """Función principal"""
    print("🚀 Configuración inicial de la API de Finanzas Personales")
    print("=" * 60)

    check_requirements()
    check_env_file()
    setup_database()

    print("=" * 60)
    print("✅ Configuración completada exitosamente!")
    print()
    print("Para iniciar el servidor:")
    print("  uvicorn app.main:app --reload")
    print()
    print("Documentación de la API:")
    print("  http://localhost:8000/docs")
    print("  http://localhost:8000/redoc")

if __name__ == "__main__":
    main()