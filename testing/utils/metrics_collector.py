"""
Metrics Collector
Recolecta y almacena métricas del sistema durante las pruebas
"""

import time
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ResponseMetric:
    """Métrica de respuesta de un request"""
    timestamp: float
    url: str
    status_code: int
    response_time_ms: float
    success: bool
    error: Optional[str] = None


@dataclass
class AvailabilityMetric:
    """Métrica de disponibilidad de un servicio"""
    timestamp: float
    service_name: str
    is_available: bool
    response_time_ms: Optional[float] = None
    error: Optional[str] = None


@dataclass
class FailoverMetric:
    """Métrica de un evento de failover"""
    timestamp: float
    scenario: str
    detection_time_s: float
    failover_time_s: float
    total_time_s: float
    success: bool
    primary_service: str
    fallback_service: str
    notes: Optional[str] = None


class MetricsCollector:
    """Colector de métricas del sistema"""
    
    def __init__(self):
        self.response_metrics: List[ResponseMetric] = []
        self.availability_metrics: List[AvailabilityMetric] = []
        self.failover_metrics: List[FailoverMetric] = []
        self.start_time = time.time()
        
    def record_response(self, url: str, status_code: int, response_time_ms: float, 
                       success: bool, error: Optional[str] = None):
        """Registrar una respuesta HTTP"""
        metric = ResponseMetric(
            timestamp=time.time(),
            url=url,
            status_code=status_code,
            response_time_ms=response_time_ms,
            success=success,
            error=error
        )
        self.response_metrics.append(metric)
        logger.debug(f"Response recorded: {url} - {status_code} - {response_time_ms:.2f}ms")
    
    def record_availability(self, service_name: str, is_available: bool, 
                           response_time_ms: Optional[float] = None,
                           error: Optional[str] = None):
        """Registrar disponibilidad de un servicio"""
        metric = AvailabilityMetric(
            timestamp=time.time(),
            service_name=service_name,
            is_available=is_available,
            response_time_ms=response_time_ms,
            error=error
        )
        self.availability_metrics.append(metric)
        logger.debug(f"Availability recorded: {service_name} - {'UP' if is_available else 'DOWN'}")
    
    def record_failover(self, scenario: str, detection_time_s: float, 
                       failover_time_s: float, total_time_s: float,
                       success: bool, primary_service: str, fallback_service: str,
                       notes: Optional[str] = None):
        """Registrar un evento de failover"""
        metric = FailoverMetric(
            timestamp=time.time(),
            scenario=scenario,
            detection_time_s=detection_time_s,
            failover_time_s=failover_time_s,
            total_time_s=total_time_s,
            success=success,
            primary_service=primary_service,
            fallback_service=fallback_service,
            notes=notes
        )
        self.failover_metrics.append(metric)
        logger.info(f"Failover recorded: {scenario} - {total_time_s:.2f}s - {'SUCCESS' if success else 'FAILED'}")
    
    def get_response_stats(self) -> Dict:
        """Obtener estadísticas de respuestas"""
        if not self.response_metrics:
            return {
                "count": 0,
                "avg_response_time_ms": 0,
                "min_response_time_ms": 0,
                "max_response_time_ms": 0,
                "p50_response_time_ms": 0,
                "p95_response_time_ms": 0,
                "p99_response_time_ms": 0,
                "success_rate": 0
            }
        
        response_times = [m.response_time_ms for m in self.response_metrics]
        response_times.sort()
        
        count = len(response_times)
        successes = sum(1 for m in self.response_metrics if m.success)
        
        return {
            "count": count,
            "avg_response_time_ms": sum(response_times) / count,
            "min_response_time_ms": response_times[0],
            "max_response_time_ms": response_times[-1],
            "p50_response_time_ms": response_times[int(count * 0.50)],
            "p95_response_time_ms": response_times[int(count * 0.95)],
            "p99_response_time_ms": response_times[int(count * 0.99)],
            "success_rate": successes / count if count > 0 else 0
        }
    
    def get_availability_stats(self, service_name: Optional[str] = None) -> Dict:
        """Obtener estadísticas de disponibilidad"""
        metrics = self.availability_metrics
        
        if service_name:
            metrics = [m for m in metrics if m.service_name == service_name]
        
        if not metrics:
            return {
                "total_checks": 0,
                "available_checks": 0,
                "unavailable_checks": 0,
                "availability_percentage": 0
            }
        
        total = len(metrics)
        available = sum(1 for m in metrics if m.is_available)
        
        return {
            "total_checks": total,
            "available_checks": available,
            "unavailable_checks": total - available,
            "availability_percentage": (available / total * 100) if total > 0 else 0
        }
    
    def get_failover_stats(self) -> Dict:
        """Obtener estadísticas de failovers"""
        if not self.failover_metrics:
            return {
                "total_failovers": 0,
                "successful_failovers": 0,
                "failed_failovers": 0,
                "avg_detection_time_s": 0,
                "avg_failover_time_s": 0,
                "avg_total_time_s": 0
            }
        
        total = len(self.failover_metrics)
        successful = sum(1 for m in self.failover_metrics if m.success)
        
        avg_detection = sum(m.detection_time_s for m in self.failover_metrics) / total
        avg_failover = sum(m.failover_time_s for m in self.failover_metrics) / total
        avg_total = sum(m.total_time_s for m in self.failover_metrics) / total
        
        return {
            "total_failovers": total,
            "successful_failovers": successful,
            "failed_failovers": total - successful,
            "avg_detection_time_s": avg_detection,
            "avg_failover_time_s": avg_failover,
            "avg_total_time_s": avg_total
        }
    
    def get_summary(self) -> Dict:
        """Obtener resumen completo de métricas"""
        elapsed_time = time.time() - self.start_time
        
        return {
            "test_duration_s": elapsed_time,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.now().isoformat(),
            "response_stats": self.get_response_stats(),
            "availability_stats": self.get_availability_stats(),
            "failover_stats": self.get_failover_stats(),
            "total_metrics": {
                "responses": len(self.response_metrics),
                "availability_checks": len(self.availability_metrics),
                "failovers": len(self.failover_metrics)
            }
        }
    
    def export_to_json(self, filepath: str):
        """Exportar métricas a archivo JSON"""
        try:
            data = {
                "summary": self.get_summary(),
                "response_metrics": [asdict(m) for m in self.response_metrics],
                "availability_metrics": [asdict(m) for m in self.availability_metrics],
                "failover_metrics": [asdict(m) for m in self.failover_metrics]
            }
            
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Métricas exportadas a {filepath}")
            
        except Exception as e:
            logger.error(f"Error al exportar métricas: {e}")
    
    def import_from_json(self, filepath: str):
        """Importar métricas desde archivo JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.response_metrics = [ResponseMetric(**m) for m in data.get('response_metrics', [])]
            self.availability_metrics = [AvailabilityMetric(**m) for m in data.get('availability_metrics', [])]
            self.failover_metrics = [FailoverMetric(**m) for m in data.get('failover_metrics', [])]
            
            logger.info(f"Métricas importadas desde {filepath}")
            
        except Exception as e:
            logger.error(f"Error al importar métricas: {e}")


class SLAValidator:
    """Validador de SLA/SLO"""
    
    def __init__(self, sla_config: Dict, slo_config: Dict):
        self.sla = sla_config
        self.slo = slo_config
    
    def validate_response_time(self, avg_response_time_ms: float, target: str = "normal") -> Dict:
        """Validar tiempo de respuesta contra SLA/SLO"""
        if target == "app3":
            threshold = self.sla.get("app3_response_time_max", 3000)
        else:
            threshold = self.slo.get("normal_response_time_max", 2000)
        
        passed = avg_response_time_ms <= threshold
        
        return {
            "metric": "response_time",
            "target": target,
            "actual_ms": avg_response_time_ms,
            "threshold_ms": threshold,
            "passed": passed,
            "margin_ms": threshold - avg_response_time_ms
        }
    
    def validate_availability(self, availability_percentage: float) -> Dict:
        """Validar disponibilidad contra SLA"""
        threshold = self.sla.get("availability_minimum", 0.96) * 100
        passed = availability_percentage >= threshold
        
        return {
            "metric": "availability",
            "actual_percentage": availability_percentage,
            "threshold_percentage": threshold,
            "passed": passed,
            "margin_percentage": availability_percentage - threshold
        }
    
    def validate_recovery_time(self, recovery_time_s: float) -> Dict:
        """Validar tiempo de recuperación contra SLA"""
        threshold = self.sla.get("recovery_time_max", 30)
        passed = recovery_time_s <= threshold
        
        return {
            "metric": "recovery_time",
            "actual_s": recovery_time_s,
            "threshold_s": threshold,
            "passed": passed,
            "margin_s": threshold - recovery_time_s
        }
    
    def validate_detection_time(self, detection_time_s: float) -> Dict:
        """Validar tiempo de detección contra SLO"""
        threshold = self.slo.get("detection_time_max", 10)
        passed = detection_time_s <= threshold
        
        return {
            "metric": "detection_time",
            "actual_s": detection_time_s,
            "threshold_s": threshold,
            "passed": passed,
            "margin_s": threshold - detection_time_s
        }
    
    def validate_failover_time(self, failover_time_s: float, target: str = "app") -> Dict:
        """Validar tiempo de failover contra SLO"""
        if target == "db":
            threshold = self.slo.get("db_failover_time_max", 20)
        else:
            threshold = self.slo.get("app_failover_time_max", 30)
        
        passed = failover_time_s <= threshold
        
        return {
            "metric": "failover_time",
            "target": target,
            "actual_s": failover_time_s,
            "threshold_s": threshold,
            "passed": passed,
            "margin_s": threshold - failover_time_s
        }
