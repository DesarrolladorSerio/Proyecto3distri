"""
Report Generator
Genera reportes HTML y JSON de los resultados de las pruebas
"""

import json
import logging
from typing import Dict, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generador de reportes de pruebas"""
    
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_json_report(self, data: Dict, filename: str = None) -> str:
        """
        Generar reporte en formato JSON
        
        Args:
            data: Datos del reporte
            filename: Nombre del archivo (opcional)
            
        Returns:
            Path del archivo generado
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Reporte JSON generado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error al generar reporte JSON: {e}")
            raise
    
    def generate_html_report(self, data: Dict, filename: str = None) -> str:
        """
        Generar reporte en formato HTML
        
        Args:
            data: Datos del reporte
            filename: Nombre del archivo (opcional)
            
        Returns:
            Path del archivo generado
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.html"
        
        filepath = self.output_dir / filename
        
        try:
            html_content = self._generate_html_content(data)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Reporte HTML generado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error al generar reporte HTML: {e}")
            raise
    
    def _generate_html_content(self, data: Dict) -> str:
        """Generar contenido HTML del reporte"""
        
        summary = data.get('summary', {})
        validations = data.get('validations', {})
        
        # Estadísticas de respuesta
        response_stats = summary.get('response_stats', {})
        
        # Estadísticas de disponibilidad
        availability_stats = summary.get('availability_stats', {})
        
        # Estadísticas de failover
        failover_stats = summary.get('failover_stats', {})
        
        # Generar sección de validaciones
        validation_rows = self._generate_validation_rows(validations)
        
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Pruebas - Sistema Distribuido</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
            font-size: 1.8em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .stat-card h3 {{
            color: #667eea;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        
        .stat-card .unit {{
            font-size: 0.9em;
            color: #666;
            margin-left: 5px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        
        tr:hover {{
            background: #f5f7fa;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        
        .badge.pass {{
            background: #10b981;
            color: white;
        }}
        
        .badge.fail {{
            background: #ef4444;
            color: white;
        }}
        
        .badge.warning {{
            background: #f59e0b;
            color: white;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #eee;
            border-radius: 15px;
            overflow: hidden;
            margin-top: 10px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}
        
        .footer {{
            background: #f5f7fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Reporte de Pruebas</h1>
            <p>Sistema de Gestión Médica Distribuido</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="content">
            <!-- Resumen Ejecutivo -->
            <div class="section">
                <h2>🎯 Resumen Ejecutivo</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Duración de Pruebas</h3>
                        <div class="value">{summary.get('test_duration_s', 0):.1f}<span class="unit">s</span></div>
                    </div>
                    <div class="stat-card">
                        <h3>Total de Requests</h3>
                        <div class="value">{response_stats.get('count', 0)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Tasa de Éxito</h3>
                        <div class="value">{response_stats.get('success_rate', 0) * 100:.1f}<span class="unit">%</span></div>
                    </div>
                    <div class="stat-card">
                        <h3>Disponibilidad</h3>
                        <div class="value">{availability_stats.get('availability_percentage', 0):.1f}<span class="unit">%</span></div>
                    </div>
                </div>
            </div>
            
            <!-- Performance -->
            <div class="section">
                <h2>⚡ Performance</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Tiempo Promedio</h3>
                        <div class="value">{response_stats.get('avg_response_time_ms', 0):.0f}<span class="unit">ms</span></div>
                    </div>
                    <div class="stat-card">
                        <h3>P95 Latencia</h3>
                        <div class="value">{response_stats.get('p95_response_time_ms', 0):.0f}<span class="unit">ms</span></div>
                    </div>
                    <div class="stat-card">
                        <h3>P99 Latencia</h3>
                        <div class="value">{response_stats.get('p99_response_time_ms', 0):.0f}<span class="unit">ms</span></div>
                    </div>
                    <div class="stat-card">
                        <h3>Max Latencia</h3>
                        <div class="value">{response_stats.get('max_response_time_ms', 0):.0f}<span class="unit">ms</span></div>
                    </div>
                </div>
            </div>
            
            <!-- Failover -->
            <div class="section">
                <h2>🔄 Failover & Recovery</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Total Failovers</h3>
                        <div class="value">{failover_stats.get('total_failovers', 0)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Exitosos</h3>
                        <div class="value">{failover_stats.get('successful_failovers', 0)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Tiempo Detección</h3>
                        <div class="value">{failover_stats.get('avg_detection_time_s', 0):.1f}<span class="unit">s</span></div>
                    </div>
                    <div class="stat-card">
                        <h3>Tiempo Recuperación</h3>
                        <div class="value">{failover_stats.get('avg_total_time_s', 0):.1f}<span class="unit">s</span></div>
                    </div>
                </div>
            </div>
            
            <!-- Validaciones SLA/SLO -->
            <div class="section">
                <h2>✅ Validaciones SLA/SLO</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Métrica</th>
                            <th>Target</th>
                            <th>Actual</th>
                            <th>Threshold</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        {validation_rows}
                    </tbody>
                </table>
            </div>
            
            <!-- Disponibilidad -->
            <div class="section">
                <h2>📈 Disponibilidad</h2>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {availability_stats.get('availability_percentage', 0):.1f}%">
                        {availability_stats.get('availability_percentage', 0):.2f}%
                    </div>
                </div>
                <div style="margin-top: 20px;">
                    <p><strong>Total Checks:</strong> {availability_stats.get('total_checks', 0)}</p>
                    <p><strong>Checks Exitosos:</strong> {availability_stats.get('available_checks', 0)}</p>
                    <p><strong>Checks Fallidos:</strong> {availability_stats.get('unavailable_checks', 0)}</p>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Sistema de Gestión Médica Distribuido - Framework de Pruebas v1.0</p>
            <p>© 2024 - Testing Framework</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_validation_rows(self, validations: Dict) -> str:
        """Generar filas HTML para la tabla de validaciones"""
        rows = []
        
        for category, tests in validations.items():
            if not isinstance(tests, list):
                tests = [tests]
            
            for test in tests:
                metric = test.get('metric', 'Unknown')
                target = test.get('target', '-')
                passed = test.get('passed', False)
                
                # Determinar valor actual y threshold
                if 'actual_ms' in test:
                    actual = f"{test['actual_ms']:.0f} ms"
                    threshold = f"{test['threshold_ms']:.0f} ms"
                elif 'actual_s' in test:
                    actual = f"{test['actual_s']:.2f} s"
                    threshold = f"{test['threshold_s']:.2f} s"
                elif 'actual_percentage' in test:
                    actual = f"{test['actual_percentage']:.2f}%"
                    threshold = f"{test['threshold_percentage']:.2f}%"
                else:
                    actual = "N/A"
                    threshold = "N/A"
                
                badge_class = "pass" if passed else "fail"
                badge_text = "✓ PASS" if passed else "✗ FAIL"
                
                row = f"""
                        <tr>
                            <td><strong>{metric}</strong></td>
                            <td>{target}</td>
                            <td>{actual}</td>
                            <td>{threshold}</td>
                            <td><span class="badge {badge_class}">{badge_text}</span></td>
                        </tr>
                """
                rows.append(row)
        
        return "\n".join(rows) if rows else "<tr><td colspan='5'>No hay validaciones disponibles</td></tr>"
    
    def generate_summary(self, metrics_summary: Dict, validations: Dict) -> Dict:
        """
        Generar resumen completo para reportes
        
        Args:
            metrics_summary: Resumen de métricas del MetricsCollector
            validations: Resultados de validaciones SLA/SLO
            
        Returns:
            Dict con resumen completo
        """
        # Contar validaciones pasadas/fallidas
        total_validations = 0
        passed_validations = 0
        
        for category, tests in validations.items():
            if not isinstance(tests, list):
                tests = [tests]
            
            for test in tests:
                total_validations += 1
                if test.get('passed', False):
                    passed_validations += 1
        
        return {
            "summary": metrics_summary,
            "validations": validations,
            "validation_summary": {
                "total": total_validations,
                "passed": passed_validations,
                "failed": total_validations - passed_validations,
                "pass_rate": (passed_validations / total_validations * 100) if total_validations > 0 else 0
            }
        }
