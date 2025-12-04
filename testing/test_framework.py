"""
Test Framework Principal
Orquestador de todas las pruebas del sistema distribuido
"""

import argparse
import logging
import yaml
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Importar suites de pruebas
from tests.test_connectivity import run_connectivity_tests
from tests.test_sla import run_sla_tests
from tests.test_slo import run_slo_tests

# Importar utilidades
from utils.metrics_collector import MetricsCollector, SLAValidator
from utils.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


class TestFramework:
    """Framework principal de pruebas"""
    
    def __init__(self, config_path: str = "./config/test_config.yaml"):
        """
        Inicializar framework
        
        Args:
            config_path: Path al archivo de configuración
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.report_gen = ReportGenerator(
            output_dir=self.config.get('reporting', {}).get('output_dir', './reports')
        )
        self.all_results = {}
    
    def _load_config(self) -> Dict:
        """Cargar configuración desde YAML"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuración cargada desde {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Archivo de configuración no encontrado: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Error al parsear configuración YAML: {e}")
            sys.exit(1)
    
    def run_connectivity_tests(self) -> Dict:
        """Ejecutar pruebas de conectividad"""
        logger.info("\n" + "="*60)
        logger.info("ÁREA 1: CONECTIVIDAD Y COMUNICACIÓN")
        logger.info("="*60 + "\n")
        
        results = run_connectivity_tests(self.config_path)
        self.all_results['connectivity'] = results
        
        return results
    
    def run_sla_tests(self) -> Dict:
        """Ejecutar pruebas de SLA"""
        logger.info("\n" + "="*60)
        logger.info("ÁREA 2: SLA (Service Level Agreements)")
        logger.info("="*60 + "\n")
        
        results = run_sla_tests(self.config_path)
        self.all_results['sla'] = results
        
        return results
    
    def run_slo_tests(self) -> Dict:
        """Ejecutar pruebas de SLO"""
        logger.info("\n" + "="*60)
        logger.info("ÁREA 3: SLO (Service Level Objectives)")
        logger.info("="*60 + "\n")
        
        results = run_slo_tests(self.config_path)
        self.all_results['slo'] = results
        
        return results
    
    def run_all_tests(self) -> Dict:
        """Ejecutar todas las pruebas"""
        logger.info("\n" + "="*80)
        logger.info("INICIANDO SUITE COMPLETA DE PRUEBAS")
        logger.info("Sistema de Gestión Médica Distribuido")
        logger.info("="*80 + "\n")
        
        start_time = datetime.now()
        
        # Ejecutar cada suite
        self.run_connectivity_tests()
        self.run_sla_tests()
        self.run_slo_tests()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Consolidar resultados
        consolidated = {
            "framework_version": "1.0.0",
            "test_date": start_time.isoformat(),
            "total_duration_s": duration,
            "test_suites": self.all_results,
            "summary": self._generate_summary()
        }
        
        logger.info("\n" + "="*80)
        logger.info(f"PRUEBAS COMPLETADAS - Duración total: {duration:.2f}s")
        logger.info("="*80 + "\n")
        
        return consolidated
    
    def _generate_summary(self) -> Dict:
        """Generar resumen consolidado de todas las pruebas"""
        summary = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_suites_run": len(self.all_results)
        }
        
        # Contar tests por suite
        for suite_name, suite_results in self.all_results.items():
            tests = suite_results.get('tests', {})
            
            for test_name, test_result in tests.items():
                summary["total_tests"] += 1
                
                # Verificar si pasó
                if isinstance(test_result, dict):
                    if test_result.get('success', False):
                        summary["passed_tests"] += 1
                    else:
                        summary["failed_tests"] += 1
        
        if summary["total_tests"] > 0:
            summary["pass_rate"] = (summary["passed_tests"] / summary["total_tests"]) * 100
        else:
            summary["pass_rate"] = 0
        
        return summary
    
    def _compile_validations(self) -> Dict:
        """Compilar todas las validaciones SLA/SLO"""
        validations = {
            "sla": [],
            "slo": []
        }
        
        # Extraer validaciones de SLA
        sla_results = self.all_results.get('sla', {}).get('tests', {})
        for test_name, test_result in sla_results.items():
            if isinstance(test_result, dict) and 'validation' in test_result:
                validations['sla'].append(test_result['validation'])
        
        # Extraer validaciones de SLO
        slo_results = self.all_results.get('slo', {}).get('tests', {})
        for test_name, test_result in slo_results.items():
            if isinstance(test_result, dict) and 'validation' in test_result:
                validations['slo'].append(test_result['validation'])
        
        return validations
    
    def _compile_metrics_summary(self) -> Dict:
        """Compilar resumen de métricas de todas las suites"""
        # Tomar métricas de la suite más completa (SLA)
        sla_metrics = self.all_results.get('sla', {}).get('metrics', {})
        
        return sla_metrics
    
    def generate_reports(self, output_prefix: str = "test_report") -> Dict[str, str]:
        """
        Generar reportes en múltiples formatos
        
        Args:
            output_prefix: Prefijo para nombres de archivo
            
        Returns:
            Dict con paths de reportes generados
        """
        logger.info("Generando reportes...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Preparar datos para reporte
        metrics_summary = self._compile_metrics_summary()
        validations = self._compile_validations()
        
        report_data = self.report_gen.generate_summary(
            metrics_summary=metrics_summary,
            validations=validations
        )
        
        # Agregar resultados completos
        report_data['full_results'] = self.all_results
        
        generated_reports = {}
        
        # Generar JSON
        json_path = self.report_gen.generate_json_report(
            data=report_data,
            filename=f"{output_prefix}_{timestamp}.json"
        )
        generated_reports['json'] = json_path
        logger.info(f"✓ Reporte JSON generado: {json_path}")
        
        # Generar HTML
        html_path = self.report_gen.generate_html_report(
            data=report_data,
            filename=f"{output_prefix}_{timestamp}.html"
        )
        generated_reports['html'] = html_path
        logger.info(f"✓ Reporte HTML generado: {html_path}")
        
        # Crear symlink a "latest"
        self._create_latest_links(generated_reports)
        
        return generated_reports
    
    def _create_latest_links(self, reports: Dict[str, str]):
        """Crear enlaces simbólicos a los reportes más recientes"""
        try:
            output_dir = Path(self.config.get('reporting', {}).get('output_dir', './reports'))
            
            for format_type, report_path in reports.items():
                latest_path = output_dir / f"latest.{format_type}"
                report_file = Path(report_path)
                
                # Eliminar symlink existente si existe
                if latest_path.exists():
                    latest_path.unlink()
                
                # Crear nuevo symlink (en Windows puede requerir permisos)
                try:
                    latest_path.symlink_to(report_file.name)
                except OSError:
                    # Si falla symlink, copiar archivo
                    import shutil
                    shutil.copy2(report_path, latest_path)
                
                logger.debug(f"Latest link created: {latest_path}")
                
        except Exception as e:
            logger.warning(f"No se pudieron crear enlaces 'latest': {e}")
    
    def print_summary(self):
        """Imprimir resumen en consola"""
        summary = self._generate_summary()
        
        print("\n" + "="*80)
        print("RESUMEN DE PRUEBAS")
        print("="*80)
        print(f"Total de tests: {summary['total_tests']}")
        print(f"Tests exitosos: {summary['passed_tests']} ✓")
        print(f"Tests fallidos: {summary['failed_tests']} ✗")
        print(f"Tasa de éxito: {summary['pass_rate']:.1f}%")
        print(f"Suites ejecutadas: {summary['test_suites_run']}")
        print("="*80 + "\n")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Framework de Pruebas - Sistema Distribuido",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python test_framework.py --all               # Ejecutar todas las pruebas
  python test_framework.py --connectivity      # Solo pruebas de conectividad
  python test_framework.py --sla               # Solo pruebas de SLA
  python test_framework.py --slo               # Solo pruebas de SLO
  python test_framework.py --all --report      # Ejecutar todo y generar reportes
        """
    )
    
    parser.add_argument(
        '--config',
        default='./config/test_config.yaml',
        help='Path al archivo de configuración (default: ./config/test_config.yaml)'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Ejecutar todas las pruebas'
    )
    
    parser.add_argument(
        '--connectivity',
        action='store_true',
        help='Ejecutar solo pruebas de conectividad'
    )
    
    parser.add_argument(
        '--sla',
        action='store_true',
        help='Ejecutar solo pruebas de SLA'
    )
    
    parser.add_argument(
        '--slo',
        action='store_true',
        help='Ejecutar solo pruebas de SLO'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generar reportes HTML/JSON'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Modo verboso (DEBUG logging)'
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Crear framework
    framework = TestFramework(config_path=args.config)
    
    # Determinar qué ejecutar
    if args.all:
        framework.run_all_tests()
    else:
        if args.connectivity:
            framework.run_connectivity_tests()
        if args.sla:
            framework.run_sla_tests()
        if args.slo:
            framework.run_slo_tests()
        
        # Si no se especificó nada, mostrar ayuda
        if not (args.connectivity or args.sla or args.slo):
            parser.print_help()
            return
    
    # Generar reportes si se solicitó
    if args.report:
        framework.generate_reports()
    
    # Imprimir resumen
    framework.print_summary()


if __name__ == "__main__":
    main()
