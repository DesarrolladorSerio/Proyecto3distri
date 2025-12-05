# Framework de Experimentación - Sistema Distribuido

Framework completo de pruebas automatizadas para validar **Comunicación/Conectividad**, **Transparencia** y **SLA/SLO** en el sistema de gestión médica distribuido.

## 📋 Tabla de Contenidos

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Pruebas Disponibles](#pruebas-disponibles)
- [Interpretación de Resultados](#interpretación-de-resultados)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Requisitos

- **Python 3.8+**
- **Docker** y **Docker Compose**
- Sistema distribuido corriendo (docker compose up)

## 📦 Instalación

1. **Navegar al directorio de testing:**

```bash
cd testing
```

2. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

## ⚙️ Configuración

La configuración se encuentra en `config/test_config.yaml`. Aquí puedes ajustar:

- **URLs de servicios**
- **Nombres de containers Docker**
- **Targets de SLA/SLO**
- **Parámetros de testing** (duración, usuarios concurrentes, etc.)

### Configuración de SLA

```yaml
sla:
  availability_minimum: 0.96 # 96%
  app3_response_time_max: 3000 # 3 segundos
  recovery_time_max: 30 # 30 segundos
  db_recovery_time_max: 40 # 40 segundos
```

### Configuración de SLO

```yaml
slo:
  detection_time_max: 10 # 10 segundos
  db_failover_time_max: 20 # 20 segundos
  app_failover_time_max: 30 # 30 segundos
  log_time_max: 5 # 5 segundos
  normal_response_time_max: 2000 # 2 segundos
```

---

## 🚀 Uso

### Ejecutar Suite Completa

```bash
python test_framework.py --all --report
```

### Ejecutar Pruebas Específicas

```bash
# Solo conectividad
python test_framework.py --connectivity

# Solo SLA
python test_framework.py --sla

# Solo SLO
python test_framework.py --slo

# Múltiples suites
python test_framework.py --connectivity --sla --report
```

### Modo Verboso

```bash
python test_framework.py --all --verbose
```

---

## 📁 Estructura del Proyecto

```
testing/
├── config/
│   └── test_config.yaml        # Configuración centralizada
├── tests/
│   ├── __init__.py
│   ├── test_connectivity.py    # Pruebas de conectividad
│   ├── test_sla.py             # Pruebas de SLA
│   └── test_slo.py             # Pruebas de SLO
├── utils/
│   ├── __init__.py
│   ├── chaos_engineering.py    # Simulación de fallos
│   ├── metrics_collector.py    # Recolección de métricas
│   └── report_generator.py     # Generación de reportes
├── reports/                     # Reportes generados
│   ├── latest.html             # Último reporte HTML
│   └── latest.json             # Último reporte JSON
├── test_framework.py           # Framework principal
├── requirements.txt            # Dependencias Python
└── README.md                   # Este archivo
```

---

## 🧪 Pruebas Disponibles

### Área 1: Comunicación y Conectividad

- ✅ **Health Checks**: Verificar que todos los servicios respondan
- ✅ **App3 → Middleware**: Comunicación entre capa de presentación y middleware
- ✅ **Middleware → App1/App2**: Comunicación hacia servicios de backend
- ✅ **Circuit Breaker**: Verificar estado y funcionamiento
- ✅ **Load Balancing**: Distribución de carga entre réplicas
- ⚠️ **Failover** (destructivo): Cambio automático a réplica tras caída

### Área 2: SLA (Service Level Agreements)

- ✅ **Tiempo de Respuesta App3**: Medir latencia bajo carga
- ✅ **Performance bajo Carga**: Test con usuarios concurrentes
- ✅ **Disponibilidad**: Simular uptime/downtime
- ⚠️ **Recuperación tras Caída** (destructivo): Medir tiempo de recovery
- ⚠️ **Recuperación de BD** (destructivo): Failover de MariaDB/PostgreSQL

### Área 3: SLO (Service Level Objectives)

- ✅ **Tiempo de Respuesta Normal**: Medir bajo condiciones óptimas
- ✅ **Tiempo de Logging**: Verificar velocidad de registro
- ⚠️ **Detección de Caída** (destructivo): Tiempo hasta detectar fallo
- ⚠️ **Failover de BD** (destructivo): Activación de réplica
- ⚠️ **Failover de App** (destructivo): Cambio completo a réplica
- ⚠️ **Intervalos de Reintento**: Verificar retry logic del middleware

> **⚠️ IMPORTANTE**: Las pruebas marcadas como "destructivas" detienen containers temporalmente. Están **desactivadas por defecto** y deben habilitarse manualmente en el código.

---

## 📊 Interpretación de Resultados

### Reportes HTML

Los reportes HTML (`reports/latest.html`) incluyen:

- 📈 **Dashboard visual** con métricas clave
- 🎯 **Validaciones SLA/SLO** con PASS/FAIL
- ⚡ **Estadísticas de performance** (P50, P95, P99)
- 🔄 **Historial de failovers**
- 📉 **Gráficos de disponibilidad**

### Reportes JSON

Los reportes JSON (`reports/latest.json`) contienen:

- Todos los datos crudos de las pruebas
- Métricas detalladas timestamp por timestamp
- Validaciones con márgenes exactos
- Resumen ejecutivo

### Ejemplo de Validación PASS

```json
{
  "metric": "response_time",
  "actual_ms": 1850,
  "threshold_ms": 2000,
  "passed": true,
  "margin_ms": 150
}
```

### Ejemplo de Validación FAIL

```json
{
  "metric": "failover_time",
  "actual_s": 35,
  "threshold_s": 30,
  "passed": false,
  "margin_s": -5
}
```

---

## 🔍 Troubleshooting

### Error: "Container not found"

**Problema**: El framework no encuentra los containers Docker.

**Solución**:

1. Verificar que docker compose esté corriendo:
   ```bash
   docker compose ps
   ```
2. Actualizar nombres de containers en `config/test_config.yaml`

### Error: "Connection refused"

**Problema**: No puede conectar con un servicio.

**Solución**:

1. Verificar que los servicios estén healthy:
   ```bash
   docker compose ps
   ```
2. Verificar puertos en `config/test_config.yaml`
3. Revisar logs:
   ```bash
   docker compose logs middleware
   ```

### Los tests destructivos no se ejecutan

**Problema**: Los tests de failover están comentados.

**Solución**:
Los tests destructivos están **desactivados por defecto** para evitar afectar el sistema. Para habilitarlos:

1. Abrir el archivo de test correspondiente (`test_sla.py`, `test_slo.py`)
2. Descomentar las líneas del test deseado
3. Ejecutar nuevamente

**Ejemplo en `test_sla.py`:**

```python
# Descomentar esta línea:
# results["tests"]["app_recovery"] = tests.test_recovery_after_crash()

# Para habilitar:
results["tests"]["app_recovery"] = tests.test_recovery_after_crash()
```

### Error: "Timeout waiting for container to be healthy"

**Problema**: El container no se recupera en el tiempo esperado.

**Solución**:

1. Aumentar timeout en el código (default: 60s)
2. Verificar healthcheck del container:
   ```bash
   docker inspect <container-name> | grep -A 10 Health
   ```
3. Revisar logs del container

### Reportes no se generan

**Problema**: No aparecen archivos en `reports/`

**Solución**:

1. Verificar que se usó flag `--report`:
   ```bash
   python test_framework.py --all --report
   ```
2. Verificar permisos del directorio `reports/`
3. Revisar logs en consola para errores

---

## 📝 Notas Importantes

### Pruebas Destructivas

Las pruebas destructivas simulan fallos reales:

- ❌ Matan containers
- ❌ Rompen conexiones de red
- ❌ Saturan recursos

**Recomendaciones:**

- ✅ Ejecutar en **ambiente de desarrollo/testing**
- ✅ **No ejecutar en producción**
- ✅ Asegurar que hay backups
- ✅ Coordinar con el equipo

### Tiempos de Ejecución

- **Connectivity**: ~2-5 minutos
- **SLA** (sin destructivas): ~3-5 minutos
- **SLA** (con destructivas): ~10-15 minutos
- **SLO** (sin destructivas): ~2 minutos
- **SLO** (con destructivas): ~15-20 minutos
- **Suite completa** (sin destructivas): ~7-12 minutos
- **Suite completa** (con destructivas): ~25-40 minutos

### Frecuencia Recomendada

- **Connectivity**: Diario (CI/CD)
- **SLA/SLO** (sin destructivas): Diario
- **SLA/SLO** (destructivas): Semanal o antes de releases

---

## 🎯 Targets de Referencia

### SLA

| Métrica          | Target | Criticidad |
| ---------------- | ------ | ---------- |
| Disponibilidad   | ≥ 96%  | 🔴 Alta    |
| Respuesta App3   | < 3s   | 🔴 Alta    |
| Recuperación App | < 30s  | 🟡 Media   |
| Recuperación BD  | < 40s  | 🟡 Media   |

### SLO

| Métrica            | Target | Criticidad |
| ------------------ | ------ | ---------- |
| Detección de Caída | ≤ 10s  | 🟡 Media   |
| Failover BD        | ≤ 20s  | 🟡 Media   |
| Failover App       | ≤ 30s  | 🟡 Media   |
| Logs               | < 5s   | 🟢 Baja    |
| Reintentos         | 5-10s  | 🟢 Baja    |
| Respuesta Normal   | < 2s   | 🟡 Media   |

---

## 📞 Soporte

Para problemas o preguntas:

1. Revisar logs del framework
2. Revisar este README
3. Consultar código fuente (bien comentado)
4. Contactar al equipo de desarrollo

---

**Versión**: 1.0.0  
**Última actualización**: Diciembre 2024
