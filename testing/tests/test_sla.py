"""
Test de SLA (Service Level Agreements)
Pruebas para validar acuerdos de nivel de servicio
"""

import time
import logging
import requests
import yaml
import json
from typing import Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.metrics_collector import MetricsCollector, SLAValidator
from utils.chaos_engineering import ChaosEngineering

logger = logging.getLogger(__name__)


class SLATests:
    """Suite de pruebas de SLA"""
    
    def __init__(self, config: Dict, metrics: MetricsCollector):
        self.config = config
        self.metrics = metrics
        self.services = config.get('services', {})
        self.sla = config.get('sla', {})
        self.testing_config = config.get('testing', {})
        self.chaos = ChaosEngineering()
        self.validator = SLAValidator(self.sla, config.get('slo', {}))
    
    def test_availability_simulation(self, duration_hours: float = 1.0) -> Dict:
        """
        Simular disponibilidad durante un período
        
        Args:
            duration_hours: Duración de la simulación en horas
            
        Returns:
            Dict con métricas de disponibilidad
        """
        logger.info(f"=== Testing Availability (simulando {duration_hours}h) ===")
        
        duration_seconds = duration_hours * 3600
        check_interval = self.testing_config.get('healthcheck_interval', 5)
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        services_to_check = {
            'app1': self.services.get('app1'),
            'app2': self.services.get('app2'),
            'app3': self.services.get('app3'),
            'middleware': self.services.get('middleware')
        }
        
        check_count = 0
        
        while time.time() < end_time:
            check_count += 1
            logger.info(f"Availability check #{check_count}")
            
            for service_name, url in services_to_check.items():
                try:
                    response = requests.get(f"{url}/health", timeout=5)
                    is_available = response.status_code == 200
                    
                    self.metrics.record_availability(
                        service_name=service_name,
                        is_available=is_available,
                        response_time_ms=(response.elapsed.total_seconds() * 1000) if is_available else None
                    )
                    
                except Exception as e:
                    self.metrics.record_availability(
                        service_name=service_name,
                        is_available=False,
                        error=str(e)
                    )
            
            # Esperar hasta el siguiente check
            time.sleep(check_interval)
        
        # Calcular estadísticas
        stats = self.metrics.get_availability_stats()
        
        validation = self.validator.validate_availability(
            stats.get('availability_percentage', 0)
        )
        
        logger.info(f"✓ Disponibilidad: {stats['availability_percentage']:.2f}%")
        logger.info(f"  Target: {self.sla.get('availability_minimum', 0.96) * 100}%")
        logger.info(f"  Checks: {stats['total_checks']}")
        logger.info(f"  Resultado: {'PASS' if validation['passed'] else 'FAIL'}")
        
        return {
            "duration_hours": duration_hours,
            "total_checks": stats['total_checks'],
            "availability_percentage": stats['availability_percentage'],
            "validation": validation
        }
    
    def test_app3_response_time(self, num_requests: int = 100) -> Dict:
        """
        Test de tiempo de respuesta de App3
        
        Args:
            num_requests: Número de requests a realizar
            
        Returns:
            Dict con métricas de tiempo de respuesta
        """
        logger.info(f"=== Testing App3 Response Time ({num_requests} requests) ===")
        
        app3_url = self.services.get('app3', 'http://localhost:3003')
        
        for i in range(num_requests):
            try:
                start_time = time.time()
                response = requests.get(f"{app3_url}/", timeout=10)
                response_time = (time.time() - start_time) * 1000
                
                self.metrics.record_response(
                    url=app3_url,
                    status_code=response.status_code,
                    response_time_ms=response_time,
                    success=response.status_code == 200
                )
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Progress: {i+1}/{num_requests} requests")
                
            except Exception as e:
                logger.error(f"Request {i+1} failed: {e}")
                self.metrics.record_response(
                    url=app3_url,
                    status_code=0,
                    response_time_ms=0,
                    success=False,
                    error=str(e)
                )
        
        stats = self.metrics.get_response_stats()
        
        validation = self.validator.validate_response_time(
            stats.get('avg_response_time_ms', 0),
            target="app3"
        )
        
        logger.info(f"✓ App3 Response Time:")
        logger.info(f"  Promedio: {stats['avg_response_time_ms']:.0f}ms")
        logger.info(f"  P95: {stats['p95_response_time_ms']:.0f}ms")
        logger.info(f"  P99: {stats['p99_response_time_ms']:.0f}ms")
        logger.info(f"  Target: < {self.sla.get('app3_response_time_max', 3000)}ms")
        logger.info(f"  Resultado: {'PASS' if validation['passed'] else 'FAIL'}")
        
        return {
            "total_requests": num_requests,
            "response_stats": stats,
            "validation": validation
        }
    
    def test_load_performance(self, concurrent_users: int = 50, duration_seconds: int = 60) -> Dict:
        """
        Test de performance bajo carga
        
        Args:
            concurrent_users: Número de usuarios concurrentes
            duration_seconds: Duración del test
            
        Returns:
            Dict con métricas de performance
        """
        logger.info(f"=== Testing Load Performance ({concurrent_users} users, {duration_seconds}s) ===")
        
        app3_url = self.services.get('app3', 'http://localhost:3003')
        
        def make_request():
            try:
                start_time = time.time()
                response = requests.get(f"{app3_url}/", timeout=10)
                response_time = (time.time() - start_time) * 1000
                
                self.metrics.record_response(
                    url=app3_url,
                    status_code=response.status_code,
                    response_time_ms=response_time,
                    success=response.status_code == 200
                )
                
                return True
                
            except Exception as e:
                self.metrics.record_response(
                    url=app3_url,
                    status_code=0,
                    response_time_ms=0,
                    success=False,
                    error=str(e)
                )
                return False
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        request_count = 0
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            while time.time() < end_time:
                futures = []
                
                for _ in range(concurrent_users):
                    if time.time() >= end_time:
                        break
                    future = executor.submit(make_request)
                    futures.append(future)
                    request_count += 1
                
                # Esperar a que completen
                for future in as_completed(futures):
                    future.result()
                
                time.sleep(0.1)  # Pequeña pausa entre batches
        
        stats = self.metrics.get_response_stats()
        
        validation = self.validator.validate_response_time(
            stats.get('avg_response_time_ms', 0),
            target="app3"
        )
        
        logger.info(f"✓ Load Performance:")
        logger.info(f"  Total requests: {request_count}")
        logger.info(f"  Success rate: {stats['success_rate'] * 100:.1f}%")
        logger.info(f"  Avg response: {stats['avg_response_time_ms']:.0f}ms")
        logger.info(f"  P95: {stats['p95_response_time_ms']:.0f}ms")
        logger.info(f"  Resultado: {'PASS' if validation['passed'] else 'FAIL'}")
        
        return {
            "concurrent_users": concurrent_users,
            "duration_seconds": duration_seconds,
            "total_requests": request_count,
            "response_stats": stats,
            "validation": validation
        }
    
    def test_recovery_after_crash(self) -> Dict:
        """
        Test de recuperación tras caída de aplicación principal
        
        Returns:
            Dict con métricas de recuperación
        """
        logger.info("=== Testing Recovery After Crash ===")
        
        containers = self.config.get('containers', {})
        app1_primary = containers.get('app1', 'app1')
        app1_replica = containers.get('app1_replica', 'app1-replica')
        
        # Registrar estado inicial
        logger.info("Estado inicial: Verificando servicios...")
        initial_healthy = self.chaos.is_container_healthy(app1_primary)
        logger.info(f"App1 Primary healthy: {initial_healthy}")
        
        # Simular caída
        logger.info(f"Deteniendo {app1_primary}...")
        crash_time = time.time()
        
        if not self.chaos.kill_container(app1_primary):
            return {
                "success": False,
                "error": "Failed to kill primary container"
            }
        
        # Esperar a que réplica tome control
        logger.info("Esperando a que réplica tome control...")
        recovery_start = time.time()
        
        if not self.chaos.wait_for_container_healthy(app1_replica, timeout=60):
            # Reiniciar primary para cleanup
            self.chaos.start_container(app1_primary)
            return {
                "success": False,
                "error": "Replica did not become healthy in time"
            }
        
        recovery_time = time.time() - recovery_start
        total_recovery = time.time() - crash_time
        
        # Registrar métrica
        self.metrics.record_failover(
            scenario="App Crash Recovery",
            detection_time_s=5.0,  # Estimado basado en healthcheck interval
            failover_time_s=recovery_time,
            total_time_s=total_recovery,
            success=True,
            primary_service=app1_primary,
            fallback_service=app1_replica
        )
        
        # Validar contra SLA
        validation = self.validator.validate_recovery_time(total_recovery)
        
        logger.info(f"✓ Recovery completado:")
        logger.info(f"  Tiempo de recuperación: {total_recovery:.2f}s")
        logger.info(f"  Target: < {self.sla.get('recovery_time_max', 30)}s")
        logger.info(f"  Resultado: {'PASS' if validation['passed'] else 'FAIL'}")
        
        # Restaurar estado
        logger.info(f"Reiniciando {app1_primary}...")
        self.chaos.start_container(app1_primary)
        time.sleep(10)  # Esperar estabilización
        
        return {
            "success": True,
            "recovery_time_s": total_recovery,
            "validation": validation
        }
    
    def test_db_recovery_after_crash(self, db_type: str = "mariadb") -> Dict:
        """
        Test de recuperación de base de datos tras caída
        
        Args:
            db_type: Tipo de BD (mariadb o postgres)
            
        Returns:
            Dict con métricas de recuperación
        """
        logger.info(f"=== Testing {db_type.upper()} Recovery After Crash ===")
        
        containers = self.config.get('containers', {})
        
        if db_type == "mariadb":
            primary = containers.get('mariadb_master', 'app1-mariadb-master')
            replica = containers.get('mariadb_replica', 'app1-mariadb-replica')
        else:
            primary = containers.get('postgres_primary', 'app2-postgres_primary')
            replica = containers.get('postgres_replica', 'app2-postgres_replica')
        
        # Detener BD principal
        logger.info(f"Deteniendo {primary}...")
        crash_time = time.time()
        
        if not self.chaos.kill_container(primary):
            return {
                "success": False,
                "error": f"Failed to kill {primary}"
            }
        
        # Esperar a que réplica esté lista
        logger.info("Esperando a que réplica esté operativa...")
        
        if not self.chaos.wait_for_container_healthy(replica, timeout=60):
            # Reiniciar primary
            self.chaos.start_container(primary)
            return {
                "success": False,
                "error": f"Replica {replica} did not become healthy"
            }
        
        recovery_time = time.time() - crash_time
        
        # Validar contra SLA
        validation = {
            "metric": "db_recovery_time",
            "actual_s": recovery_time,
            "threshold_min_s": self.sla.get('db_recovery_time_min', 20),
            "threshold_max_s": self.sla.get('db_recovery_time_max', 40),
            "passed": recovery_time <= self.sla.get('db_recovery_time_max', 40)
        }
        
        logger.info(f"✓ DB Recovery completado:")
        logger.info(f"  Tiempo de recuperación: {recovery_time:.2f}s")
        logger.info(f"  Target: {validation['threshold_min_s']}-{validation['threshold_max_s']}s")
        logger.info(f"  Resultado: {'PASS' if validation['passed'] else 'FAIL'}")
        
        # Restaurar estado
        logger.info(f"Reiniciando {primary}...")
        self.chaos.start_container(primary)
        time.sleep(15)  # Esperar estabilización de BD
        
        return {
            "success": True,
            "db_type": db_type,
            "recovery_time_s": recovery_time,
            "validation": validation
        }


def run_sla_tests(config_path: str = "./config/test_config.yaml") -> Dict:
    """
    Ejecutar todas las pruebas de SLA
    
    Args:
        config_path: Path al archivo de configuración
        
    Returns:
        Dict con resultados de las pruebas
    """
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Cargar configuración
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Crear colector de métricas
    metrics = MetricsCollector()
    
    # Crear suite de tests
    tests = SLATests(config, metrics)
    
    results = {
        "test_suite": "sla",
        "tests": {}
    }
    
    logger.info("=== Iniciando pruebas de SLA ===")
    
    # Test 1: Tiempo de respuesta de App3
    results["tests"]["app3_response_time"] = tests.test_app3_response_time(num_requests=100)
    time.sleep(2)
    
    # Test 2: Performance bajo carga
    results["tests"]["load_performance"] = tests.test_load_performance(
        concurrent_users=config.get('testing', {}).get('concurrent_users', 50),
        duration_seconds=60
    )
    time.sleep(5)
    
    # Test 3: Disponibilidad (simulación corta)
    # Nota: Para test real de 1 mes, usar duration_hours=720
    results["tests"]["availability"] = tests.test_availability_simulation(duration_hours=0.0167)  # 1 minuto
    time.sleep(2)
    
    # Tests destructivos - comentar si no se desean ejecutar
    logger.warning("Ejecutando tests destructivos...")
    
    # Test 4: Recuperación tras caída de app
    # results["tests"]["app_recovery"] = tests.test_recovery_after_crash()
    # time.sleep(10)
    
    # Test 5: Recuperación de BD MariaDB
    # results["tests"]["mariadb_recovery"] = tests.test_db_recovery_after_crash("mariadb")
    # time.sleep(10)
    
    # Test 6: Recuperación de BD PostgreSQL
    # Nota: Este test es para la BD de App2, NO para el NGINX load balancer
    # NGINX balancea las instancias de la app, pero las BDs son independientes
    # results["tests"]["postgres_recovery"] = tests.test_db_recovery_after_crash("postgres")
    
    # Agregar métricas al resultado
    results["metrics"] = metrics.get_summary()
    
    logger.info("=== Pruebas de SLA completadas ===")
    
    return results


if __name__ == "__main__":
    results = run_sla_tests()
    print(json.dumps(results, indent=2))
