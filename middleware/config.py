import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # URLs de las aplicaciones
    APP1_URL: str = os.getenv("APP1_URL", "http://localhost:5001")
    APP1_REPLICA_URL: str = os.getenv("APP1_REPLICA_URL", "http://localhost:5002")
    APP2_URL: str = os.getenv("APP2_URL", "http://localhost:3002")
    
    # Configuración de timeouts y reintentos
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "5"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: float = 1.0  # segundos
    
    # Circuit Breaker
    CIRCUIT_BREAKER_THRESHOLD: int = 5  # fallos consecutivos para abrir circuito
    CIRCUIT_BREAKER_TIMEOUT: int = 30  # segundos antes de intentar cerrar
    
    class Config:
        env_file = ".env"

settings = Settings()
