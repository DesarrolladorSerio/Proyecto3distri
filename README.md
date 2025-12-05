# Sistema de Gestión Médica Distribuido

Proyecto académico de sistemas distribuidos con tolerancia a fallos, replicación de datos y middleware.

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA DISTRIBUIDO                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐      ┌──────────────┐      ┌──────────┐      │
│  │  App 1   │      │  Middleware  │      │  App 3   │      │
│  │  Flask   │◄─────┤   FastAPI    │◄─────┤  Flask   │      │
│  │ (Médica) │      │              │      │(Paciente)│      │
│  └────┬─────┘      └──────┬───────┘      └────┬─────┘      │
│       │                   │                   │             │
│  ┌────▼──────┐      ┌─────▼──────┐      ┌────▼──────┐      │
│  │  MariaDB  │      │   App 2    │      │   MySQL   │      │
│  │Primary/Rep│      │  Node.js   │      │Primary/Rep│      │
│  └───────────┘      │(Admin+Nginx)│      └───────────┘      │
│                     └──────┬──────┘                         │
│                     ┌──────▼──────┐                         │
│                     │  PostgreSQL │                         │
│                     │ Primary/Rep │                         │
│                     └─────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## Componentes

### App 1 - Gestión de Consultas Médicas
- **Tecnología**: Python (Flask)
- **Base de Datos**: MariaDB (Maestro-Esclavo)
- **Puerto**: 5001 (Primary), 5002 (Replica)
- **Usuarios**: Médicos y enfermeros
- **Funcionalidades**: Consultas, diagnósticos, tratamientos, disponibilidad médica

### App 2 - Gestión Administrativa de Pacientes
- **Tecnología**: Node.js (Express)
- **Base de Datos**: PostgreSQL (Primary-Replica)
- **Puerto**: 3002 (Nginx load balancer)
- **Usuarios**: Administrativos, contadores
- **Funcionalidades**: Datos de pacientes, pagos, seguros, facturación

### App 3 - Portal del Paciente
- **Tecnología**: Python (Flask)
- **Base de Datos**: MySQL (Primary-Replica)
- **Puerto**: 3003
- **Usuarios**: Pacientes
- **Funcionalidades**: Historial médico, pagos, gestión de citas

### Middleware
- **Tecnología**: Python (FastAPI)
- **Puerto**: 8000
- **Función**: Integración entre App3 y App1/App2
- **Features**: Circuit Breaker, Retry, Failover, Transformación de datos

## Instalación y Ejecución

### Prerequisitos
- Docker Desktop instalado y ejecutándose
- Git

### Levantar todo el sistema
```bash
# Desde la raíz del proyecto
docker-compose up --build -d

# Ver logs
docker-compose logs -f

# Ver estado
docker-compose ps
```

### Detener el sistema
```bash
docker-compose down

# Eliminar también los volúmenes (datos)
docker-compose down -v
```

## Puertos

| Servicio | Puerto | URL |
|----------|--------|-----|
| **App1 Primary** | 5001 | http://localhost:5001 |
| **App1 Replica** | 5002 | http://localhost:5002 |
| **App2 (Nginx)** | 3002 | http://localhost:3002 |
| **App3** | 3003 | http://localhost:3003 |
| **Middleware** | 8000 | http://localhost:8000 |
| **Middleware Docs** | 8000 | http://localhost:8000/docs |
| **MariaDB Master** | 3306 | localhost:3306 |
| **PostgreSQL Primary** | 5433 | localhost:5433 |
| **PostgreSQL Replica** | 5434 | localhost:5434 |
| **MySQL Primary** | 3307 | localhost:3307 |
| **MySQL Replica** | 3308 | localhost:3308 |

## Primeros Pasos

1. **Levantar el sistema**:
   ```bash
   docker-compose up -d
   ```
   
2. **Esperar a que todo esté healthy** (~30 segundos):
   ```bash
   docker-compose ps
   ```

3. **Acceder al Portal del Paciente**:
   - URL: http://localhost:3003
   - RUT de prueba: `11111111-1`

4. **Ver documentación del Middleware**:
   - URL: http://localhost:8000/docs

5. **Verificar Circuit Breakers**:
   ```bash
   curl http://localhost:8000/health
   ```

## Pruebas de Tolerancia a Fallos

### ✨ Failover Automático de Bases de Datos

El sistema incluye **monitores automáticos** que detectan caídas y promueven réplicas sin intervención manual:

```bash
# Verificar estado de los monitores
docker logs mariadb-monitor --tail 10
docker logs postgres-monitor --tail 10
docker logs mysql-monitor --tail 10
```

### Probar Failover Automático MariaDB
```bash
# 1. Detener master
docker stop mariadb-master

# 2. Observar promoción automática (15-20 segundos)
docker logs -f mariadb-monitor

# 3. Verificar que App1 sigue funcionando
curl http://localhost:5001/

# 4. Reiniciar
docker start mariadb-master
```

**Resultado**: La réplica se promoverá automáticamente a master tras detectar 3 fallos consecutivos.

### Probar Failover Automático PostgreSQL
```bash
# 1. Detener primary
docker stop postgres_primary

# 2. Monitor ejecuta pg_promote() automáticamente
docker logs -f postgres-monitor

# 3. App2 sigue funcionando via réplica promovida
curl http://localhost:3002/patients
```

### Probar Failover Automático MySQL
```bash
# 1. Detener primary
docker stop mysql_primary

# 2. Monitor promueve réplica automáticamente
docker logs -f mysql-monitor

# 3. App3 sigue disponible
curl http://localhost:3003/health
```

### Probar Failover de App1
```bash
# Detener App1 Primary
docker stop app1

# Verificar que App3 sigue funcionando (usa réplica)
curl http://localhost:3003/history?rut=11111111-1

# Reiniciar
docker start app1
```

### Probar Circuit Breaker
```bash
# Detener ambas instancias de App1
docker stop app1 app1-replica

# Hacer varias peticiones (el circuit breaker se abrirá)
curl http://localhost:8000/api/medical-history/11111111-1

# Ver estado
curl http://localhost:8000/health

# Reiniciar
docker start app1 app1-replica
```

### Probar Replicación de Bases de Datos

**PostgreSQL (App2)**:
```bash
# Crear un paciente
curl -X POST http://localhost:3002/patients \
  -H "Content-Type: application/json" \
  -d '{"rut":"99999999-9","nombre":"Test","email":"test@test.com","telefono":"123","direccion":"Test St"}'

# Verificar en Primary
docker exec app2-postgres_primary-1 psql -U admin -d app2 -c "SELECT * FROM patients WHERE rut='99999999-9';"

# Verificar en Replica
docker exec app2-postgres_replica-1 psql -U admin -d app2 -c "SELECT * FROM patients WHERE rut='99999999-9';"
```

**MySQL (App3)**:
```bash
# Crear una cita
curl -X POST http://localhost:3003/api/appointments \
  -H "Content-Type: application/json" \
  -d '{"patient_rut":"11111111-1","patient_name":"Test","doctor_name":"Dr. Test","specialty":"General","appointment_date":"2024-12-15T10:00:00"}'

# Verificar en Primary
docker exec app3-mysql_primary-1 mysql -u admin -padmin -D app3 -e "SELECT * FROM appointments;"

# Verificar en Replica
docker exec app3-mysql_replica-1 mysql -u admin -padmin -D app3 -e "SELECT * FROM appointments;"
```

## Monitoreo

### Ver logs de todos los servicios
```bash
docker-compose logs -f
```

### Ver logs de un servicio específico
```bash
docker-compose logs -f middleware
docker-compose logs -f app3
docker-compose logs -f nginx
```

### Ver estado de salud
```bash
# Todos los servicios
docker-compose ps

# Solo servicios saludables
docker-compose ps | grep healthy
```

## Estructura del Proyecto

```
Proyecto3distri/
├── app1/                   # App 1 - Gestión Médica
│   ├── app1/              # Código Flask
│   ├── db/                # Scripts de base de datos
│   └── docker-compose.yml # (individual, no usado)
├── app2/                   # App 2 - Gestión Administrativa
│   ├── src/               # Código Node.js
│   ├── scripts/           # Scripts de replicación
│   ├── nginx.conf         # Configuración Nginx
│   └── docker-compose.yml # (individual, no usado)
├── app3/                   # App 3 - Portal del Paciente
│   ├── src/               # Código Flask
│   ├── templates/         # Vistas HTML
│   ├── static/            # CSS/JS
│   ├── scripts/           # Scripts MySQL
│   └── docker-compose.yml # (individual, no usado)
├── middleware/             # Middleware - Integración
│   ├── clients/           # Clientes HTTP
│   ├── routes/            # Endpoints API
│   ├── utils/             # Circuit Breaker, Retry
│   └── docker-compose.yml # (individual, no usado)
└── docker-compose.yml      # ⭐ MAESTRO (usar este)
```

## SLA/SLO

### Acuerdos de Nivel de Servicio (SLA)
- **Disponibilidad mínima mensual**: 96%
- **Tiempo máximo de respuesta App3**: 3 segundos
- **Recuperación ante caída**: < 30 segundos
- **Recuperación de BD**: ≤ 20-40 segundos

### Objetivos de Nivel de Servicio (SLO)
- **Detección de caída**: ≤ 5-10 segundos
- **Activación de réplica BD**: ≤ 10-20 segundos
- **Failover de aplicación**: ≤ 15-30 segundos
- **Registro de fallos**: < 5 segundos
- **Reintentos Middleware**: Cada 5-10 segundos

## Troubleshooting

### Los contenedores no inician
```bash
# Ver errores
docker-compose logs

# Recrear desde cero
docker-compose down -v
docker-compose up --build
```

### Error de conexión entre servicios
```bash
# Verificar la red
docker network ls
docker network inspect proyecto3distri_medical_system

# Verificar que todos estén en la misma red
docker-compose ps
```

### Base de datos no replica
```bash
# Ver logs de las réplicas
docker logs app2-postgres_replica-1
docker logs app3-mysql_replica-1

# Verificar estado de replicación
docker exec app2-postgres_replica-1 psql -U admin -d app2 -c "SELECT * FROM pg_stat_replication;"
```

## Documentación Adicional

- [App 1 README](app1/README.md)
- [App 2 README](app2/README.md)
- [App 3 README](app3/README.md)
- [Middleware README](middleware/README.md)

## Autores

Proyecto académico - Sistemas Distribuidos

## Licencia

Uso académico únicamente
