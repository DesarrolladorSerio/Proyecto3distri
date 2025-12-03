import time
from enum import Enum
from typing import Dict
from config import settings
import logging

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"  # Funcionando normalmente
    OPEN = "open"      # Circuito abierto, rechaza peticiones
    HALF_OPEN = "half_open"  # Probando si el servicio se recuperó

class CircuitBreaker:
    """
    Implementación del patrón Circuit Breaker
    """
    def __init__(self, name: str):
        self.name = name
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
    
    def can_execute(self) -> bool:
        """Verifica si se puede ejecutar una petición"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Verificar si debemos intentar cerrar el circuito
            if self.last_failure_time and \
               (time.time() - self.last_failure_time) > settings.CIRCUIT_BREAKER_TIMEOUT:
                logger.info(f"Circuit Breaker '{self.name}': Intentando HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    def record_success(self):
        """Registra una ejecución exitosa"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            # Si tenemos varios éxitos, cerramos el circuito
            if self.success_count >= 2:
                logger.info(f"Circuit Breaker '{self.name}': CLOSED (recuperado)")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        else:
            self.failure_count = 0
    
    def record_failure(self):
        """Registra una ejecución fallida"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            logger.warning(f"Circuit Breaker '{self.name}': OPEN (falló en HALF_OPEN)")
            self.state = CircuitState.OPEN
        elif self.failure_count >= settings.CIRCUIT_BREAKER_THRESHOLD:
            logger.error(
                f"Circuit Breaker '{self.name}': OPEN "
                f"({self.failure_count} fallos consecutivos)"
            )
            self.state = CircuitState.OPEN
    
    def get_state(self) -> str:
        return self.state.value

# Instancias globales de Circuit Breakers
circuit_breakers: Dict[str, CircuitBreaker] = {
    "app1": CircuitBreaker("app1"),
    "app2": CircuitBreaker("app2")
}

def get_circuit_breaker(service: str) -> CircuitBreaker:
    """Obtiene el Circuit Breaker para un servicio"""
    return circuit_breakers.get(service, CircuitBreaker(service))
