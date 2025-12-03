from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.medical_routes import router as medical_router
from routes.administrative_routes import router as administrative_router
from utils.circuit_breaker import circuit_breakers
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Middleware - Sistema de Gestión Médica Distribuido",
    description="Capa de integración entre App3 (Portal del Paciente) y App1/App2",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(medical_router)
app.include_router(administrative_router)

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "service": "Middleware - Sistema de Gestión Médica",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "middleware",
        "circuit_breakers": {
            name: cb.get_state() 
            for name, cb in circuit_breakers.items()
        }
    }

@app.get("/status")
async def status():
    """Estado detallado del sistema"""
    return {
        "service": "middleware",
        "status": "running",
        "circuit_breakers": {
            name: {
                "state": cb.get_state(),
                "failure_count": cb.failure_count
            }
            for name, cb in circuit_breakers.items()
        }
    }

logger.info("Middleware iniciado correctamente")
