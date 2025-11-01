from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

from app.core.config import settings
from app.core.database import engine, Base
from app.routers import auth, expenses, incomes, investments, financial_products, debts

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear aplicación FastAPI
app = FastAPI(
    title="API de Finanzas Personales",
    description="API REST para gestión completa de finanzas personales",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(expenses.router, prefix="/expenses", tags=["Gastos"])
app.include_router(incomes.router, prefix="/incomes", tags=["Ingresos"])
app.include_router(investments.router, prefix="/investments", tags=["Inversiones"])
app.include_router(financial_products.router, prefix="/financial-products", tags=["Productos Financieros"])
app.include_router(debts.router, prefix="/debts", tags=["Deudas"])

@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": "API de Finanzas Personales",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Manejador global de excepciones"""
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )