# App2 – Gestión Administrativa de Pacientes

## Descripción
Aplicación backend RESTful diseñada para la gestión administrativa de pacientes, pagos y facturación. Está construida sobre **Node.js** y **Express**, utilizando **PostgreSQL** como base de datos relacional gestionada a través del ORM **Sequelize**.

El proyecto incluye un frontend básico (HTML/JS) para interactuar con la API y está totalmente dockerizado para un despliegue rápido.

## Tecnologías Principales
- **Backend**: Node.js (v18), Express
- **Base de Datos**: PostgreSQL 15
- **ORM**: Sequelize
- **Validación**: Joi
- **Infraestructura**: Docker, Docker Compose

## Requisitos Previos
- **Docker Desktop** instalado y ejecutándose.
- (Opcional) Node.js y npm instalados localmente si se desea ejecutar sin contenedores.

## Instalación y Ejecución

### Opción 1: Usando Docker (Recomendado)
Esta es la forma más sencilla, ya que configura automáticamente la base de datos, ejecuta las migraciones y carga datos de prueba.

1. Abre una terminal en la carpeta del proyecto.
2. Ejecuta el siguiente comando:
   ```bash
   docker-compose up --build
   ```
3. Espera a que termine el proceso de construcción e inicio.
4. Accede a la aplicación en: **http://localhost:3002**

### Opción 2: Ejecución Manual (Local)
Si prefieres correrlo nativamente en tu máquina:

1. Instala las dependencias:
   ```bash
   npm install
   ```
2. Asegúrate de tener una instancia de PostgreSQL corriendo y crea una base de datos llamada `app2`.
3. Configura las variables de entorno en un archivo `.env` (puedes copiar `.env.example`).
4. Ejecuta las migraciones y seeds:
   ```bash
   npx sequelize-cli db:migrate
   npx sequelize-cli db:seed:all
   ```
5. Inicia el servidor:
   ```bash
   npm start
   ```

## Uso de la Aplicación

### Frontend
Al acceder a `http://localhost:3002`, verás una interfaz con tres pestañas:
- **Pacientes**: Permite listar, crear y eliminar pacientes.
- **Pagos**: Permite registrar pagos y ver el historial de pagos por paciente.
- **Facturas**: Permite generar facturas y consultarlas por paciente.

### API Endpoints
La aplicación expone una API REST JSON. Puedes probarla usando **Thunder Client** (importando el archivo `thunder-collection_App2.json` incluido) o cualquier cliente HTTP.

#### Pacientes
- `GET /patients`: Listar todos los pacientes.
- `GET /patients/:id`: Obtener detalle de un paciente.
- `POST /patients`: Crear paciente.
  - Body: `{ "rut": "...", "nombre": "...", "email": "...", ... }`
- `PUT /patients/:id`: Actualizar paciente.
- `DELETE /patients/:id`: Eliminar paciente.

#### Pagos
- `GET /payments/:patientId`: Listar pagos de un paciente.
- `POST /payments`: Registrar pago.
  - Body: `{ "patient_id": 1, "monto": 1000, "metodo_pago": "efectivo" }`

#### Facturas
- `GET /invoices/:patientId`: Listar facturas de un paciente.
- `POST /invoices`: Crear factura.
  - Body: `{ "patient_id": 1, "monto": 5000, "descripcion": "Consulta" }`

## Estructura del Proyecto
```
app2/
├── src/
│   ├── config/         # Configuración de base de datos
│   ├── controllers/    # Controladores (lógica de respuesta HTTP)
│   ├── middleware/     # Validaciones (Joi) y manejo de errores
│   ├── migrations/     # Scripts de creación de tablas
│   ├── models/         # Definición de modelos Sequelize
│   ├── routes/         # Definición de endpoints
│   ├── seeders/        # Datos iniciales de prueba
│   └── services/       # Lógica de negocio y acceso a datos
├── public/             # Archivos estáticos del frontend
├── app.js              # Punto de entrada de la aplicación
├── Dockerfile          # Definición de imagen Docker
└── docker-compose.yml  # Orquestación de servicios
```
