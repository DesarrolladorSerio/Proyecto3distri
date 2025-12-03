# Middleware - Sistema de Gestión Médica Distribuido

## Descripción
Middleware que actúa como capa de integración entre **App3** (Portal del Paciente) y las aplicaciones backend **App1** (Gestión Médica) y **App2** (Gestión Administrativa).

**Funciones principales:**
- **Transformación de datos**: Normaliza estructuras de App1 y App2
- **Comunicación API**: Punto único de entrada para App3
- **Tolerancia a fallos**: Circuit Breaker, retry con exponential backoff, failover
- **Registro y monitoreo**: Logs centralizados de errores y conexiones

## Tecnologías
- **Framework**: FastAPI (Python 3.11)
- **HTTP Client**: httpx (asíncrono)
- **Infraestructura**: Docker & Docker Compose

## Arquitectura

```
App3 → Middleware → App1 (Gestión Médica)
                 → App2 (Gestión Administrativa)
```

El Middleware **NO** accede directamente a las bases de datos. Solo consume las APIs REST de App1 y App2.

## Instalación y Ejecución

### Usando Docker (Recomendado)
```bash
docker-compose up --build -d
```

### Acceso
- API: `http://localhost:8000`
- Documentación interactiva: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Endpoints Disponibles

### Para App3

#### Datos Médicos (App1)
- `GET /api/medical-history/{patient_rut}`: Historial médico del paciente
- `GET /api/doctors?specialty={specialty}`: Médicos disponibles

#### Datos Administrativos (App2)
- `GET /api/payments/{patient_rut}`: Información de pagos y facturas
- `GET /api/patient/{patient_rut}`: Datos personales del paciente

### Monitoreo
- `GET /health`: Estado del servicio y circuit breakers
- `GET /status`: Estado detallado del sistema
- `GET /`: Información general

## Tolerancia a Fallos

### Circuit Breaker
El Middleware implementa el patrón Circuit Breaker para cada servicio backend (App1 y App2):

**Estados:**
- **CLOSED**: Funcionando normalmente
- **OPEN**: Servicio caído, rechaza peticiones (usa fallback)
- **HALF_OPEN**: Probando recuperación del servicio

**Configuración:**
- Umbral de fallos: 5 consecutivos
- Timeout: 30 segundos antes de reintentar
- Verificación en: `GET /health`

### Retry con Exponential Backoff
- Reintentos automáticos: 3 (configurable)
- Delay inicial: 1 segundo
- Incremento: exponencial (1s, 2s, 4s)

### Failover
- **App1**: Si falla el primario, intenta con `app1-replica`
- **App2**: Si falla, retorna datos mock con mensaje de error

## Estructura del Proyecto

```
middleware/
├── clients/
│   ├── app1_client.py    # Cliente HTTP para App1
│   └── app2_client.py    # Cliente HTTP para App2
├── routes/
│   ├── medical_routes.py # Endpoints médicos
│   └── administrative_routes.py # Endpoints administrativos
├── utils/
│   ├── circuit_breaker.py # Patrón Circuit Breaker
│   └── retry.py           # Lógica de reintentos
├── app.py                 # Aplicación FastAPI principal
├── config.py              # Configuración y settings
├── Dockerfile             # Imagen Docker
├── docker-compose.yml     # Orquestación
├── requirements.txt       # Dependencias Python
└── .env.example           # Variables de entorno
```

## Variables de Entorno

```env
APP1_URL=http://localhost:5001
APP1_REPLICA_URL=http://localhost:5002
APP2_URL=http://localhost:3002
REQUEST_TIMEOUT=5
MAX_RETRIES=3
```

## Transformación de Datos

El Middleware normaliza los datos de App1 y App2 a un formato unificado para App3:

### Historial Médico (App1 → App3)
```json
{
  "patient_rut": "11111111-1",
  "consultations": [
    {
      "id": 1,
      "date": "2024-11-15",
      "doctor": "Dr. García",
      "specialty": "Medicina General",
      "diagnosis": "...",
      "treatment": "..."
    }
  ]
}
```

### Pagos (App2 → App3)
```json
{
  "patient_rut": "11111111-1",
  "payments": [...],
  "pending_invoices": [...],
  "total_debt": 60000
}
```

## Limitaciones

> **⚠️ SPOF (Single Point of Failure)**
> 
> El Middleware es actualmente una instancia única. Si falla, App3 no puede acceder a datos de App1 ni App2.
> 
> **Mitigación**: Los Circuit Breakers evitan cascading failures, y App3 tiene datos mock como fallback.

## Monitoreo y Logs

```bash
# Ver logs del Middleware
docker logs middleware -f

# Verificar estado de Circuit Breakers
curl http://localhost:8000/health
```

## Integración con App3

En App3, actualizar `src/services/middleware_client.py`:
```python
MIDDLEWARE_URL = "http://localhost:8000"  # o la IP del contenedor
```

El Middleware reemplazará automáticamente los datos mock en App3.
