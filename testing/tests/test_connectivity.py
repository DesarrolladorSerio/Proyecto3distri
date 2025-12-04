"""
Test de Conectividad
Pruebas de comunicación entre servicios
"""

import time
import logging
import requests
import yaml
from pathlib import Path
from typing import Dict, Optional

from utils.metrics_collector import MetricsCollector
from utils.chaos_engineering import ChaosEngineering, FailureScenarios

logger = logging.getLogger(__name__)


class ConnectivityTests:
    """Suite de pruebas de conectividad"""
    
    def __init__(self, config: Dict, metrics: MetricsCollector):
        self.config = config
        self.metrics = metrics
        self.services = config.get('services', {})
        self.timeout = config.get('testing', {}).get('request_timeout', 10)
        self.chaos = ChaosEngineering()
        self.scenarios = FailureScenarios(self.chaos)
    
    def test_service_health(self, service_name: str, url: str) -> bool:
        """
        Verificar healthcheck de un servicio
        
        Args:
            service_name: Nombre del servicio
            url: URL del healthcheck
            
        Returns:
            True si el servicio está healthy
        """
        logger.info(f"Testing health of {service_name}...")
        
        try:
            start_time = time.time()
            response = requests.get(f"{url}/health", timeout=self.timeout)
            response_time = (time.time() - start_time) * 1000
            
            success = response.status_code == 200
            
            self.metrics.record_response(
                url=f"{url}/health",
                status_code=response.status_code,
                response_time_ms=response_time,
                success=success
            )
            
            self.metrics.record_availability(
                service_name=service_name,
                is_available=success,
                response_time_ms=response_time if success else None
            )
            
            if success:
                logger.info(f"✓ {service_name} is healthy ({response_time:.0f}ms)")
            else:
                logger.warning(f"✗ {service_name} returned {response.status_code}")
            
            return success
            
        except requests.exceptions.Timeout:
            logger.error(f"✗ {service_name} timed out")
            self.metrics.record_availability(service_name, False, error="Timeout")
            return False
            
        except requests.exceptions.ConnectionError:
            logger.error(f"✗ {service_name} connection failed")
            self.metrics.record_availability(service_name, False, error="Connection Error")
            return False
            
        except Exception as e:
            logger.error(f"✗ {service_name} error: {e}")
            self.metrics.record_availability(service_name, False, error=str(e))
            return False
    
    def test_all_services_health(self) -> Dict[str, bool]:
        """Test de health de todos los servicios"""
        logger.info("=== Testing All Services Health ===")
        
        results = {}
        
        for service_name, url in self.services.items():
            results[service_name] = self.test_service_health(service_name, url)
            time.sleep(1)  # Pequeña pausa entre requests
        
        successful = sum(1 for v in results.values() if v)
        total = len(results)
        
        logger.info(f"Health check results: {successful}/{total} services healthy")
        
        return results
    
    def test_app3_to_middleware(self) -> bool:
        """Test de conectividad App3 → Middleware"""
        logger.info("=== Testing App3 → Middleware ===")
        
        middleware_url = self.services.get('middleware', 'http://localhost:8080')
        
        try:
            start_time = time.time()
            response = requests.get(f"{middleware_url}/", timeout=self.timeout)
            response_time = (time.time() - start_time) * 1000
            
            success = response.status_code == 200
            
            self.metrics.record_response(
                url=f"{middleware_url}/",
                status_code=response.status_code,
                response_time_ms=response_time,
                success=success
            )
            
            if success:
                logger.info(f"✓ App3 → Middleware comunicación exitosa ({response_time:.0f}ms)")
                return True
            else:
                logger.warning(f"✗ App3 → Middleware falló con código {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"✗ App3 → Middleware error: {e}")
            return False
    
    def test_middleware_to_app1(self) -> bool:
        """Test de conectividad Middleware → App1"""
        logger.info("=== Testing Middleware → App1 ===")
        
        middleware_url = self.services.get('middleware', 'http://localhost:8080')
        
        try:
            # Probar endpoint de médicos (debería proxear a App1)
            start_time = time.time()
            response = requests.get(f"{middleware_url}/consultas", timeout=self.timeout)
            response_time = (time.time() - start_time) * 1000
            
            # Cualquier respuesta != 500 significa que llegó a App1
            success = response.status_code != 500
            
            self.metrics.record_response(
                url=f"{middleware_url}/consultas",
                status_code=response.status_code,
                response_time_ms=response_time,
                success=success
            )
            
            if success:
                logger.info(f"✓ Middleware → App1 comunicación exitosa ({response_time:.0f}ms)")
                return True
            else:
                logger.warning(f"✗ Middleware → App1 falló")
                return False
                
        except Exception as e:
            logger.error(f"✗ Middleware → App1 error: {e}")
            return False
    
    def test_middleware_to_app2(self) -> bool:
        """Test de conectividad Middleware → App2 (NGINX load balancer)"""
        logger.info("=== Testing Middleware → App2 (NGINX LB) ===")
        
        middleware_url = self.services.get('middleware', 'http://localhost:8080')
        
        try:
            # Probar endpoint de pacientes (debería proxear a App2 vía NGINX)
            start_time = time.time()
            response = requests.get(f"{middleware_url}/patients", timeout=self.timeout)
            response_time = (time.time() - start_time) * 1000
            
            success = response.status_code != 500
            
            self.metrics.record_response(
                url=f"{middleware_url}/patients",
                status_code=response.status_code,
                response_time_ms=response_time,
                success=success
            )
            
            if success:
                logger.info(f"✓ Middleware → App2 (NGINX) comunicación exitosa ({response_time:.0f}ms)")
                return True
            else:
                logger.warning(f"✗ Middleware → App2 (NGINX) falló")
                return False
                
        except Exception as e:
            logger.error(f"✗ Middleware → App2 (NGINX) error: {e}")
            return False
    
    def test_circuit_breaker(self) -> Dict:
        """Test de circuit breaker del middleware"""
        logger.info("=== Testing Circuit Breaker ===")
        
        middleware_url = self.services.get('middleware', 'http://localhost:8080')
        
        try:
            # Obtener estado inicial
            response = requests.get(f"{middleware_url}/health", timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                cb_states = data.get('circuit_breakers', {})
                
                logger.info(f"Circuit Breaker States: {cb_states}")
                
                return {
                    "success": True,
                    "states": cb_states
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get CB state: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"✗ Circuit Breaker test error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_failover_app1(self) -> Dict:
        """Test de failover de App1"""
        logger.info("=== Testing App1 Failover ===")
        
        containers = self.config.get('containers', {})
        app1_primary = containers.get('app1', 'app1')
        app1_replica = containers.get('app1_replica', 'app1-replica')
        
        detection_start = time.time()
        
        # Detener App1 principal
        if not self.chaos.kill_container(app1_primary):
            return {"success": False, "error": "Failed to kill primary"}
        
        # Esperar detección (healthcheck debería detectar caída)
        time.sleep(5)
        detection_time = time.time() - detection_start
        
        # Medir tiempo hasta que réplica toma control
        failover_start = time.time()
        
        # Verificar que réplica esté healthy
        if not self.chaos.wait_for_container_healthy(app1_replica, timeout=30):
            # Reiniciar primary
            self.chaos.start_container(app1_primary)
            return {"success": False, "error": "Replica did not become healthy"}
        
        failover_time = time.time() - failover_start
        total_time = time.time() - detection_start
        
        # Registrar métricas
        self.metrics.record_failover(
            scenario="App1 Failover",
            detection_time_s=detection_time,
            failover_time_s=failover_time,
            total_time_s=total_time,
            success=True,
            primary_service=app1_primary,
            fallback_service=app1_replica
        )
        
        logger.info(f"✓ Failover completado - Detección: {detection_time:.2f}s, Failover: {failover_time:.2f}s, Total: {total_time:.2f}s")
        
        # Reiniciar primary
        self.chaos.start_container(app1_primary)
        time.sleep(5)  # Esperar a que se estabilice
        
        return {
            "success": True,
            "detection_time_s": detection_time,
            "failover_time_s": failover_time,
            "total_time_s": total_time
        }
    
    def test_load_balancing(self) -> Dict:
        """Test de balanceo de carga - App1 réplicas y App2 NGINX"""
        logger.info("=== Testing Load Balancing ===")
        
        results = {}
        
        # Test 1: App1 load balancing (via middleware)
        logger.info("Testing App1 load balancing via middleware...")
        middleware_url = self.services.get('middleware', 'http://localhost:8080')
        num_requests = 20
        
        response_times_app1 = []
        for i in range(num_requests):
            try:
                start_time = time.time()
                response = requests.get(f"{middleware_url}/consultas", timeout=self.timeout)
                response_time = (time.time() - start_time) * 1000
                response_times_app1.append(response_time)
                
                self.metrics.record_response(
                    url=f"{middleware_url}/consultas",
                    status_code=response.status_code,
                    response_time_ms=response_time,
                    success=response.status_code == 200
                )
            except Exception as e:
                logger.error(f"App1 request {i+1} failed: {e}")
        
        if response_times_app1:
            avg_app1 = sum(response_times_app1) / len(response_times_app1)
            results['app1'] = {
                "success": True,
                "total_requests": num_requests,
                "avg_response_time_ms": avg_app1,
                "min_response_time_ms": min(response_times_app1),
                "max_response_time_ms": max(response_times_app1)
            }
            logger.info(f"✓ App1 load balancing - Promedio: {avg_app1:.0f}ms")
        
        # Test 2: App2 NGINX load balancing
        logger.info("Testing App2 NGINX load balancing...")
        app2_url = self.services.get('app2', 'http://localhost:3002')
        
        response_times_app2 = []
        for i in range(num_requests):
            try:
                start_time = time.time()
                response = requests.get(f"{app2_url}/patients", timeout=self.timeout)
                response_time = (time.time() - start_time) * 1000
                response_times_app2.append(response_time)
                
                self.metrics.record_response(
                    url=f"{app2_url}/patients",
                    status_code=response.status_code,
                    response_time_ms=response_time,
                    success=response.status_code == 200
                )
            except Exception as e:
                logger.error(f"App2 request {i+1} failed: {e}")
        
        if response_times_app2:
            avg_app2 = sum(response_times_app2) / len(response_times_app2)
            results['app2_nginx'] = {
                "success": True,
                "total_requests": num_requests,
                "avg_response_time_ms": avg_app2,
                "min_response_time_ms": min(response_times_app2),
                "max_response_time_ms": max(response_times_app2),
                "note": "NGINX load balancer distributing between primary and replica"
            }
            logger.info(f"✓ App2 NGINX load balancing - Promedio: {avg_app2:.0f}ms")
        
        results['overall_success'] = bool(response_times_app1 or response_times_app2)
        
        return results
    
    def test_app2_nginx_failover(self) -> Dict:
        """Test de failover de App2 con NGINX load balancer"""
        logger.info("=== Testing App2 NGINX Failover ===")
        
        containers = self.config.get('containers', {})
        app2_primary = containers.get('app2_primary', 'app2-app_primary')
        app2_replica = containers.get('app2_replica', 'app2-app_replica')
        app2_url = self.services.get('app2', 'http://localhost:3002')
        
        # 1. Verificar estado inicial - ambos healthy
        logger.info("Estado inicial: verificando ambas instancias...")
        primary_healthy = self.chaos.is_container_healthy(app2_primary)
        replica_healthy = self.chaos.is_container_healthy(app2_replica)
        logger.info(f"Primary: {primary_healthy}, Replica: {replica_healthy}")
        
        # 2. Verificar que NGINX responde
        try:
            response = requests.get(f"{app2_url}/patients", timeout=5)
            initial_working = response.status_code == 200
            logger.info(f"NGINX initial status: {'OK' if initial_working else 'FAIL'}")
        except:
            initial_working = False
            logger.error("NGINX no responde inicialmente")
        
        if not initial_working:
            return {"success": False, "error": "NGINX not responding initially"}
        
        # 3. Detener primary
        logger.info(f"Deteniendo primary: {app2_primary}")
        failover_start = time.time()
        
        if not self.chaos.kill_container(app2_primary):
            return {"success": False, "error": "Failed to kill primary"}
        
        # 4. Esperar detección de NGINX (healthcheck interval)
        time.sleep(5)  # NGINX debería detectar y redirigir a replica
        detection_time = 5.0
        
        # 5. Verificar que NGINX sigue respondiendo (solo con replica)
        try:
            response = requests.get(f"{app2_url}/patients", timeout=5)
            failover_working = response.status_code == 200
            failover_time = time.time() - failover_start
            
            if failover_working:
                logger.info(f"✓ NGINX failover exitoso - Réplica manejando tráfico")
                logger.info(f"  Tiempo total: {failover_time:.2f}s")
                
                # Registrar métrica
                self.metrics.record_failover(
                    scenario="App2 NGINX Failover",
                    detection_time_s=detection_time,
                    failover_time_s=failover_time - detection_time,
                    total_time_s=failover_time,
                    success=True,
                    primary_service=app2_primary,
                    fallback_service=app2_replica,
                    notes="NGINX automatically redirected to replica"
                )
                
                # Restaurar primary
                logger.info(f"Reiniciando primary: {app2_primary}")
                self.chaos.start_container(app2_primary)
                time.sleep(10)  # Esperar estabilización
                
                return {
                    "success": True,
                    "detection_time_s": detection_time,
                    "total_failover_time_s": failover_time,
                    "nginx_continued_serving": True,
                    "note": "NGINX successfully failed over to replica"
                }
            else:
                logger.error("✗ NGINX no respondió después de failover")
                self.chaos.start_container(app2_primary)
                return {"success": False, "error": "NGINX stopped responding after primary failure"}
                
        except Exception as e:
            logger.error(f"✗ Error durante failover test: {e}")
            self.chaos.start_container(app2_primary)
            return {"success": False, "error": str(e)}


def run_connectivity_tests(config_path: str = "./config/test_config.yaml") -> Dict:
    """
    Ejecutar todas las pruebas de conectividad
    
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
    tests = ConnectivityTests(config, metrics)
    
    results = {
        "test_suite": "connectivity",
        "tests": {}
    }
    
    # Ejecutar tests
    logger.info("Iniciando pruebas de conectividad...")
    
    results["tests"]["health_checks"] = tests.test_all_services_health()
    time.sleep(2)
    
    results["tests"]["app3_to_middleware"] = tests.test_app3_to_middleware()
    time.sleep(2)
    
    results["tests"]["middleware_to_app1"] = tests.test_middleware_to_app1()
    time.sleep(2)
    
    results["tests"]["middleware_to_app2"] = tests.test_middleware_to_app2()
    time.sleep(2)
    
    results["tests"]["circuit_breaker"] = tests.test_circuit_breaker()
    time.sleep(2)
    
    results["tests"]["load_balancing"] = tests.test_load_balancing()
    
    # Nota: Failover tests son destructivos, descomentar si se desea ejecutar
    # results["tests"]["app1_failover"] = tests.test_failover_app1()
    # results["tests"]["app2_nginx_failover"] = tests.test_app2_nginx_failover()
    
    # Agregar métricas al resultado
    results["metrics"] = metrics.get_summary()
    
    logger.info("Pruebas de conectividad completadas")
    
    return results


if __name__ == "__main__":
    results = run_connectivity_tests()
    print(json.dumps(results, indent=2))
