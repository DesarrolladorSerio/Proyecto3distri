"""
Chaos Engineering Utilities
Herramientas para simular fallos en el sistema distribuido
"""

import subprocess
import time
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class ChaosEngineering:
    """Clase para simular fallos controlados en el sistema"""
    
    @staticmethod
    def kill_container(container_name: str) -> bool:
        """
        Detener un container Docker
        
        Args:
            container_name: Nombre del container a detener
            
        Returns:
            True si se detuvo exitosamente, False en caso contrario
        """
        try:
            logger.info(f"Deteniendo container: {container_name}")
            result = subprocess.run(
                ["docker", "stop", container_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Container {container_name} detenido exitosamente")
                return True
            else:
                logger.error(f"Error al detener container: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout al detener container {container_name}")
            return False
        except Exception as e:
            logger.error(f"Excepción al detener container: {e}")
            return False
    
    @staticmethod
    def start_container(container_name: str) -> bool:
        """
        Iniciar un container Docker
        
        Args:
            container_name: Nombre del container a iniciar
            
        Returns:
            True si se inició exitosamente, False en caso contrario
        """
        try:
            logger.info(f"Iniciando container: {container_name}")
            result = subprocess.run(
                ["docker", "start", container_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Container {container_name} iniciado exitosamente")
                return True
            else:
                logger.error(f"Error al iniciar container: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout al iniciar container {container_name}")
            return False
        except Exception as e:
            logger.error(f"Excepción al iniciar container: {e}")
            return False
    
    @staticmethod
    def restart_container(container_name: str) -> bool:
        """
        Reiniciar un container Docker
        
        Args:
            container_name: Nombre del container a reiniciar
            
        Returns:
            True si se reinició exitosamente, False en caso contrario
        """
        try:
            logger.info(f"Reiniciando container: {container_name}")
            result = subprocess.run(
                ["docker", "restart", container_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"Container {container_name} reiniciado exitosamente")
                return True
            else:
                logger.error(f"Error al reiniciar container: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout al reiniciar container {container_name}")
            return False
        except Exception as e:
            logger.error(f"Excepción al reiniciar container: {e}")
            return False
    
    @staticmethod
    def get_container_status(container_name: str) -> Optional[str]:
        """
        Obtener el estado de un container
        
        Args:
            container_name: Nombre del container
            
        Returns:
            Estado del container o None si no existe
        """
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Status}}", container_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                status = result.stdout.strip()
                logger.debug(f"Container {container_name} status: {status}")
                return status
            else:
                logger.warning(f"No se pudo obtener estado de {container_name}")
                return None
                
        except Exception as e:
            logger.error(f"Excepción al obtener estado del container: {e}")
            return None
    
    @staticmethod
    def is_container_healthy(container_name: str) -> bool:
        """
        Verificar si un container está saludable
        
        Args:
            container_name: Nombre del container
            
        Returns:
            True si está healthy, False en caso contrario
        """
        try:
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Health.Status}}", container_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                health = result.stdout.strip()
                logger.debug(f"Container {container_name} health: {health}")
                return health == "healthy"
            else:
                # Si no tiene healthcheck, verificar solo si está running
                status = ChaosEngineering.get_container_status(container_name)
                return status == "running"
                
        except Exception as e:
            logger.error(f"Excepción al verificar health del container: {e}")
            return False
    
    @staticmethod
    def wait_for_container_healthy(container_name: str, timeout: int = 60) -> bool:
        """
        Esperar hasta que un container esté saludable
        
        Args:
            container_name: Nombre del container
            timeout: Tiempo máximo de espera en segundos
            
        Returns:
            True si se vuelve healthy, False si expira el timeout
        """
        logger.info(f"Esperando a que {container_name} esté healthy...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if ChaosEngineering.is_container_healthy(container_name):
                elapsed = time.time() - start_time
                logger.info(f"Container {container_name} healthy después de {elapsed:.2f}s")
                return True
            time.sleep(2)
        
        logger.error(f"Timeout esperando a que {container_name} esté healthy")
        return False
    
    @staticmethod
    def simulate_network_partition(container_name: str, target_container: str) -> bool:
        """
        Simular partición de red entre dos containers
        
        Args:
            container_name: Container que será aislado
            target_container: Container del cual será aislado
            
        Returns:
            True si se aplicó exitosamente, False en caso contrario
        """
        try:
            logger.info(f"Simulando partición de red entre {container_name} y {target_container}")
            
            # Obtener IP del target container
            result = subprocess.run(
                ["docker", "inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", target_container],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"No se pudo obtener IP de {target_container}")
                return False
            
            target_ip = result.stdout.strip()
            
            # Bloquear tráfico hacia esa IP usando iptables
            result = subprocess.run(
                ["docker", "exec", container_name, "iptables", "-A", "OUTPUT", "-d", target_ip, "-j", "DROP"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"Partición de red aplicada exitosamente")
                return True
            else:
                logger.error(f"Error al aplicar partición de red: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Excepción al simular partición de red: {e}")
            return False
    
    @staticmethod
    def get_container_logs(container_name: str, lines: int = 50) -> Optional[str]:
        """
        Obtener logs de un container
        
        Args:
            container_name: Nombre del container
            lines: Número de líneas a obtener
            
        Returns:
            Logs del container o None si hay error
        """
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(lines), container_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"Error al obtener logs: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Excepción al obtener logs: {e}")
            return None


class FailureScenarios:
    """Escenarios de fallo predefinidos"""
    
    def __init__(self, chaos: ChaosEngineering):
        self.chaos = chaos
    
    def simulate_app_crash(self, app_container: str, replica_container: str) -> dict:
        """
        Simular caída de aplicación y medir tiempo de recuperación
        
        Args:
            app_container: Container de la aplicación principal
            replica_container: Container de la réplica
            
        Returns:
            Dict con métricas del escenario
        """
        logger.info(f"=== Iniciando escenario: App Crash ===")
        
        start_time = time.time()
        
        # 1. Detener aplicación principal
        crash_time = time.time()
        if not self.chaos.kill_container(app_container):
            return {"success": False, "error": "Failed to kill app container"}
        
        # 2. Esperar a que la réplica tome control
        recovery_start = time.time()
        if not self.chaos.wait_for_container_healthy(replica_container, timeout=60):
            return {"success": False, "error": "Replica did not become healthy"}
        
        recovery_time = time.time() - recovery_start
        total_time = time.time() - crash_time
        
        logger.info(f"Tiempo de recuperación: {recovery_time:.2f}s")
        logger.info(f"Tiempo total de escenario: {total_time:.2f}s")
        
        return {
            "success": True,
            "recovery_time": recovery_time,
            "total_time": total_time,
            "crashed_container": app_container,
            "active_container": replica_container
        }
    
    def simulate_db_failover(self, primary_db: str, replica_db: str) -> dict:
        """
        Simular failover de base de datos
        
        Args:
            primary_db: Container de BD principal
            replica_db: Container de BD réplica
            
        Returns:
            Dict con métricas del escenario
        """
        logger.info(f"=== Iniciando escenario: DB Failover ===")
        
        # 1. Detener BD principal
        crash_time = time.time()
        if not self.chaos.kill_container(primary_db):
            return {"success": False, "error": "Failed to kill primary DB"}
        
        # 2. Esperar a que réplica esté lista
        if not self.chaos.wait_for_container_healthy(replica_db, timeout=60):
            return {"success": False, "error": "Replica DB did not become healthy"}
        
        failover_time = time.time() - crash_time
        
        logger.info(f"Tiempo de failover de BD: {failover_time:.2f}s")
        
        return {
            "success": True,
            "failover_time": failover_time,
            "primary_db": primary_db,
            "active_db": replica_db
        }
