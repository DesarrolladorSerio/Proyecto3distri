# App3 – Portal del Paciente

## Descripción
Aplicación web diseñada para que los pacientes puedan consultar su información médica y administrativa a través del Middleware, y gestionar sus citas médicas.

**Arquitectura Distribuida:**
- **Base de Datos**: MySQL con replicación Maestro-Esclavo (solo datos)
- **Backend**: Flask (Python) - Instancia única (sin réplicas de aplicación)
- **Integración**: Consume datos del Middleware (App1 y App2)
- **Funcionalidad Local**: Gestión de citas médicas

## Tecnologías Principales
- **Backend**: Python 3.11, Flask 3.0
- **Base de Datos**: MySQL 8.0 (Cluster Primario-Réplica)
- **ORM**: SQLAlchemy
- **HTTP Client**: Requests (consumo de Middleware)
- **Infraestructura**: Docker & Docker Compose

## Requisitos Previos
- **Docker Desktop** instalado y ejecutándose.

## Instalación y Ejecución

### Usando Docker (Recomendado)
1. Abre una terminal en la carpeta `app3`.
2. Ejecuta el siguiente comando:
   ```bash
   docker-compose up --build
   ```
3. Espera a que termine el proceso de construcción e inicio.
4. Accede a la aplicación en: **http://localhost:3003**

### Primer Acceso
En el portal, usa el RUT `11111111-1` como paciente de prueba.

## Funcionalidades

### Para Pacientes
1. **Dashboard**: Vista general con acceso rápido a todas las funciones.
2. **Historial Médico**: Consultas, diagnósticos y tratamientos (vía Middleware → App1).
3. **Información de Pagos**: Facturas, pagos realizados y deudas pendientes (vía Middleware → App2).
4. **Gestión de Citas**:
   - Agendar nuevas citas médicas
   - Consultar citas programadas
   - Cancelar citas
   - Ver médicos disponibles

## API Endpoints

### Portal
- `GET /`: Dashboard del paciente
- `GET /history?rut={rut}`: Historial médico
- `GET /payments?rut={rut}`: Información de pagos
- `GET /appointments?rut={rut}`: Gestión de citas

### API REST
- `GET /api/patient/{rut}/summary`: Resumen completo (historial + pagos)
- `GET /api/appointments?patient_rut={rut}`: Listar citas
- `POST /api/appointments`: Crear cita
- `POST /appointments/{id}/cancel`: Cancelar cita

### Health Check
- `GET /health`: Estado del servicio

## Estructura del Proyecto
```
app3/
├── src/
│   ├── config/           # Configuración de Flask y BD
│   ├── models/           # Modelos SQLAlchemy (Appointment)
│   ├── routes/           # Rutas Flask
│   └── services/         # Cliente Middleware
├── templates/            # Plantillas Jinja2
│   ├── base.html         # Layout base
│   ├── dashboard.html    # Dashboard principal
│   ├── history.html      # Historial médico
│   ├── payments.html     # Información de pagos
│   └── appointments.html # Gestión de citas
├── static/               # CSS y JavaScript
│   ├── css/style.css     # Estilos
│   └── js/script.js      # Scripts
├── scripts/              # Scripts de BD
│   ├── init_primary.sh   # Configuración MySQL Primary
│   └── init_replica.sh   # Configuración MySQL Replica
├── app.py                # Punto de entrada
├── Dockerfile            # Imagen Docker
├── docker-compose.yml    # Orquestación completa
└── requirements.txt      # Dependencias Python
```

## Notas de Desarrollo

### Datos Mock
Actualmente, el Middleware no está implementado. La aplicación usa datos mock (simulados) para:
- Historial médico del paciente
- Información de pagos
- Lista de médicos disponibles

Estos datos se encuentran en `src/services/middleware_client.py` y serán reemplazados por llamadas reales al Middleware cuando esté disponible.

### Replicación de Base de Datos
- La réplica MySQL es **solo lectura**
- Se utiliza para consultas que no requieren escritura
- La aplicación escribe siempre en el nodo **Primary**
