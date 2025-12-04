"""
Test de SLO (Service Level Objectives)
Pruebas para validar objetivos de nivel de servicio
"""

import time
import logging
import requests
import yaml
import json
from typing import Dict

from utils.metrics_collector import MetricsCollector, SLAValidator
from utils.chaos_engineering import ChaosEngineering

logger = logging.getLogger(__name__)


class SLOTests:
    """Suite de pruebas de SLO"""
    
    def __init__(self, config: Dict, metrics: MetricsCollector):
        self.config = config
        self.metrics = metrics
        self.services = config.get('services', {})
        self.slo = config.get('slo', {})
        self.sla = config.get('sla', {})
        self.chaos = ChaosEngineering()
        self.validator = SLAValidator(self.sla, self.slo)
    
    def test_failure_detection_time(self, service_name: str = "app1") -> Dict:
        """
        Test de tiempo de detección de caída de servicio
        
        Args:
            service_name: Nombre del servicio a probar
            
        Returns:
            Dict con métricas de detección
        """
        logger.info(f"=== Testing Failure Detection Time for {service_name} ===")
        
        containers = self.config.get('containers', {})
        container = containers.get(service_name, service_name)
        
        # Verificar que esté healthy inicialmente
        if not self.chaos.is_container_healthy(container):
            logger.warning(f"{container} no está healthy, iniciando...")
            self.chaos.start_container(container)
            time.sleep(10)
        
        # Detener container y medir tiempo hasta detección
        logger.info(f"Deteniendo {container}...")
        kill_time = time.time()
        
        if not self.chaos.kill_container(container):
            return {"success": False, "error": "Failed to kill container"}
        
        # Simular healthcheck intentando conectar
        healthcheck_interval = self.config.get('testing', {}).get('healthcheck_interval', 5)
        max_detection_time = self.slo.get('detection_time_max', 10)
        
        detected = False
        detection_time = 0
        
        while detection_time < max_detection_time + 5:
            time.sleep(healthcheck_interval)
            detection_time = time.time() - kill_time
            
            # Intentar healthcheck
            try:
                service_url = self.services.get(service_name)
                response = requests.get(f"{service_url}/health", timeout=2)
                if response.status_code != 200:
                    detected = True
                    break
            except:
                # Fallo de conexión = detectado
                detected = True
                break
        
        # Validar
        validation = self.validator.validate_detection_time(detection_time)
        
        logger.info(f"✓ Detection completado:")
        logger.info(f"  Tiempo de detección: {detection_time:.2f}s")
        logger.info(f"  Target: ≤ {max_detection_time}s")
        logger.info(f"  Resultado: {'PASS' if validation['passed'] else 'FAIL'}")
        
        # Restaurar
        self.chaos.start_container(container)
        time.sleep(10)
        
        return {
            "success": True,
            "service": service_name,
            "detection_time_s": detection_time,
            "validation": validation
        }
    
    def test_db_failover_time(self, db_type: str = "postgres") -> Dict:
        """
        Test de tiempo de failover de base de datos
        
        Args:
            db_type: Tipo de BD (mariadb o postgres)
            
        Returns:
            Dict con métricas de failover
        """
        logger.info(f"=== Testing {db_type.upper()} Failover Time ===")
        
        containers = self.config.get('containers', {})
        
        if db_type == "mariadb":
            primary = containers.get('mariadb_master', 'app1-mariadb-master')
            replica = containers.get('mariadb_replica', 'app1-mariadb-replica')
        else:
            primary = containers.get('postgres_primary', 'app2-postgres_primary')
            replica = containers.get('postgres_replica', 'app2-postgres_replica')
        
        # Detener primary
        logger.info(f"Deteniendo {primary}...")
        failover_start = time.time()
        
        if not self.chaos.kill_container(primary):
            return {"success": False, "error": f"Failed to kill {primary}"}
        
        # Esperar a que réplica esté operativa
        if not self.chaos.wait_for_container_healthy(replica, timeout=40):
            self.chaos.start_container(primary)
            return {"success": False, "error": f"Replica did not become healthy"}
        
        failover_time = time.time() - failover_start
        
        # Registrar métrica
        self.metrics.record_failover(
            scenario=f"{db_type.upper()} Failover",
            detection_time_s=5.0,
            failover_time_s=failover_time,
            total_time_s=failover_time,
            success=True,
            primary_service=primary,
            fallback_service=replica
        )
        
        # Validar
        validation = self.validator.validate_failover_time(failover_time, target="db")
        
        logger.info(f"✓ Failover completado:")
        logger.info(f"  Tiempo de failover: {failover_time:.2f}s")
        logger.info(f"  Target: ≤ {self.slo.get('db_failover_time_max', 20)}s")
        logger.info(f"  Resultado: {'PASS' if validation['passed'] else 'FAIL'}")
        
        # Restaurar
        self.chaos.start_container(primary)
        time.sleep(15)
        
        return {
            "success": True,
            "db_type": db_type,
            "failover_time_s": failover_time,
            "validation": validation
        }
    
    def test_app_failover_time(self, app_name: str = "app1") -> Dict:
        """
        Test de tiempo de failover de aplicación
        
        Args:
            app_name: Nombre de la aplicación
            
        Returns:
            Dict con métricas de failover completo
        """
        logger.info(f"=== Testing {app_name.upper()} Complete Failover ===")
        
        containers = self.config.get('containers', {})
        primary = containers.get(app_name, app_name)
        replica = containers.get(f"{app_name}_replica", f"{app_name}-replica")
        
        # Tiempo total: detección + failover + estabilización
        total_start = time.time()
        
        # 1. Detener primary
        logger.info(f"1. Deteniendo {primary}...")
        crash_time = time.time()
        
        if not self.chaos.kill_container(primary):
            return {"success": False, "error": "Failed to kill primary"}
        
        # 2. Tiempo de detección (simular healthcheck)
        detection_time = self.slo.get('detection_time_max', 10) / 2  # Promedio
        time.sleep(detection_time)
        
        # 3. Failover a réplica
        logger.info(f"2. Esperando failover a {replica}...")
        failover_start = time.time()
        
        if not self.chaos.wait_for_container_healthy(replica, timeout=30):
            self.chaos.start_container(primary)
            return {"success": False, "error": "Failover failed"}
        
        failover_time = time.time() - failover_start
        total_time = time.time() - crash_time
        
        # Registrar métrica
        self.metrics.record_failover(
            scenario=f"{app_name.upper()} Complete Failover",
            detection_time_s=detection_time,
            failover_time_s=failover_time,
            total_time_s=total_time,
            success=True,
            primary_service=primary,
            fallback_service=replica
        )
        
        # Validar
        validation = self.validator.validate_failover_time(total_time, target="app")
        
        logger.info(f"✓ Complete Failover:")
        logger.info(f"  Detección: {detection_time:.2f}s")
        logger.info(f"  Failover: {failover_time:.2f}s")
        logger.info(f"  Total: {total_time:.2f}s")
        logger.info(f"  Target: ≤ {self.slo.get('app_failover_time_max', 30)}s")
        logger.info(f"  Resultado: {'PASS' if validation['passed'] else 'FAIL'}")
        
        # Restaurar
        self.chaos.start_container(primary)
        time.sleep(10)
        
        return {
            "success": True,
            "app_name": app_name,
            "detection_time_s": detection_time,
            "failover_time_s": failover_time,
            "total_time_s": total_time,
            "validation": validation
        }
    
    def test_log_response_time(self, error_event: str = "test_error") -> Dict:
        """
        Test de tiempo de registro en logs
        
        Args:
            error_event: Evento a registrar
            
        Returns:
            Dict con tiempo de logging
        """
        logger.info("=== Testing Log Response Time ===")
        
        # Generar error y medir tiempo hasta aparecer en logs
        log_start = time.time()
        
        # Simular error en middleware
        middleware_url = self.services.get('middleware', 'http://localhost:8080')
        
        try:
            # Endpoint inexistente para generar error
            requests.get(f"{middleware_url}/nonexistent-endpoint-{int(time.time())}", timeout=5)
        except:
            pass
        
        # Esperar un poco
        time.sleep(1)
        
        # Verificar logs del middleware
        container = self.config.get('containers', {}).get('middleware', 'middleware-app')
        logs = self.chaos.get_container_logs(container, lines=50)
        
        log_time = time.time() - log_start
        
        # Verificar si el error aparece en logs
        logged = logs is not None and "404" in logs
        
        validation = {
            "metric": "log_time",
            "actual_s": log_time,
            "threshold_s": self.slo.get('log_time_max', 5),
            "passed": log_time <= self.slo.get('log_time_max', 5) and logged
        }
        
        logger.info(f"✓ Log Response:")
        logger.info(f"  Tiempo de logging: {log_time:.2f}s")
        logger.info(f"  Logged: {logged}")
        logger.info(f"  Target: < {self.slo.get('log_time_max', 5)}s")
        logger.info(f"  Resultado: {'PASS' if validation['passed'] else 'FAIL'}")
        
        return {
            "success": True,
            "log_time_s": log_time,
            "logged": logged,
            "validation": validation
        }
    
    def test_retry_intervals(self, duration_seconds: int = 60) -> Dict:
        """
        Test de intervalos de reintento del middleware
        
        Args:
            duration_seconds: Duración del monitoreo
            
        Returns:
            Dict con estadísticas de reintentos
        """
        logger.info("=== Testing Retry Intervals ===")
        
        # Detener App1 para forzar reintentos
        containers = self.config.get('containers', {})
        app1_primary = containers.get('app1', 'app1')
        
        logger.info(f"Deteniendo {app1_primary} para forzar reintentos...")
        self.chaos.kill_container(app1_primary)
        
        # Monitorear logs del middleware
        middleware = containers.get('middleware', 'middleware-app')
        
        logger.info(f"Monitoreando reintentos por {duration_seconds}s...")
        time.sleep(duration_seconds)
        
        # Obtener logs
        logs = self.chaos.get_container_logs(middleware, lines=200)
        
        # Analizar logs para encontrar reintentos
        # Esto es simplificado, en producción parsear timestamps
        retry_count = logs.count("retry") if logs else 0
        
        # Calcular intervalo promedio
        avg_interval = duration_seconds / retry_count if retry_count > 0 else 0
        
        # Validar
        min_interval = self.slo.get('retry_interval_min', 5)
        max_interval = self.slo.get('retry_interval_max', 10)
        
        validation = {
            "metric": "retry_interval",
            "avg_interval_s": avg_interval,
            "min_threshold_s": min_interval,
            "max_threshold_s": max_interval,
            "passed": min_interval <= avg_interval <= max_interval if avg_interval > 0 else False
        }
        
        logger.info(f"✓ Retry Intervals:")
        logger.info(f"  Reintentos detectados: {retry_count}")
        logger.info(f"  Intervalo promedio: {avg_interval:.2f}s")
        logger.info(f"  Target: {min_interval}-{max_interval}s")
        logger.info(f"  Resultado: {'PASS' if validation['passed'] else 'PARTIAL'}")
        
        # Restaurar
        self.chaos.start_container(app1_primary)
        time.sleep(10)
        
        return {
            "success": True,
            "retry_count": retry_count,
            "avg_interval_s": avg_interval,
            "validation": validation
        }
    
    def test_normal_response_time(self, num_requests: int = 100) -> Dict:
        """
        Test de tiempo de respuesta bajo condiciones normales
        
        Args:
            num_requests: Número de requests
            
        Returns:
            Dict con métricas de respuesta
        """
        logger.info("=== Testing Normal Response Time ===")
        
        middleware_url = self.services.get('middleware', 'http://localhost:8080')
        
        for i in range(num_requests):
            try:
                start_time = time.time()
                response = requests.get(f"{middleware_url}/health", timeout=10)
                response_time = (time.time() - start_time) * 1000
                
                self.metrics.record_response(
                    url=middleware_url,
                    status_code=response.status_code,
                    response_time_ms=response_time,
                    success=response.status_code == 200
                )
                
            except Exception as e:
                logger.error(f"Request failed: {e}")
        
        stats = self.metrics.get_response_stats()
        
        validation = self.validator.validate_response_time(
            stats.get('avg_response_time_ms', 0),
            target="normal"
        )
        
        logger.info(f"✓ Normal Response Time:")
        logger.info(f"  Promedio: {stats['avg_response_time_ms']:.0f}ms")
        logger.info(f"  P95: {stats['p95_response_time_ms']:.0f}ms")
        logger.info(f"  Target: < {self.slo.get('normal_response_time_max', 2000)}ms")
        logger.info(f"  Resultado: {'PASS' if validation['passed'] else 'FAIL'}")
        
        return {
            "total_requests": num_requests,
            "response_stats": stats,
            "validation": validation
        }


def run_slo_tests(config_path: str = "./config/test_config.yaml") -> Dict:
    """
    Ejecutar todas las pruebas de SLO
    
    Args:
        config_path: Path al archivo de configuración
        
    Returns:
        Dict con resultados
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    metrics = MetricsCollector()
    tests = SLOTests(config, metrics)
    
    results = {
        "test_suite": "slo",
        "tests": {}
    }
    
    logger.info("=== Iniciando pruebas de SLO ===")
    
    # Test 1: Tiempo de respuesta normal
    results["tests"]["normal_response_time"] = tests.test_normal_response_time(100)
    time.sleep(2)
    
    # Test 2: Tiempo de logging
    results["tests"]["log_response_time"] = tests.test_log_response_time()
    time.sleep(2)
    
    # Tests destructivos - comentar si no se desean ejecutar
    logger.warning("Tests destructivos desactivados por defecto")
    
    # Test 3: Detección de caída
    # results["tests"]["failure_detection"] = tests.test_failure_detection_time("app1")
    # time.sleep(10)
    
    # Test 4: Failover de PostgreSQL
    # Nota: App2 usa NGINX para balancear las INSTANCIAS DE LA APP
    # Las BDs (PostgreSQL primary/replica) son componentes separados del load balancer
    # Este test valida failover de BD, no de NGINX
    # results["tests"]["postgres_failover"] = tests.test_db_failover_time("postgres")
    # time.sleep(15)
    
    # Test 5: Failover de MariaDB
    # results["tests"]["mariadb_failover"] = tests.test_db_failover_time("mariadb")
    # time.sleep(15)
    
    # Test 6: Failover completo de App1
    # results["tests"]["app1_failover"] = tests.test_app_failover_time("app1")
    # time.sleep(10)
    
    # Test 7: Intervalos de reintento
    # results["tests"]["retry_intervals"] = tests.test_retry_intervals(60)
    
    results["metrics"] = metrics.get_summary()
    
    logger.info("=== Pruebas de SLO completadas ===")
    
    return results


if __name__ == "__main__":
    results = run_slo_tests()
    print(json.dumps(results, indent=2))
