FROM node:18

WORKDIR /usr/src/app

# Instalar cliente de PostgreSQL para el healthcheck
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY package*.json ./

RUN npm install

COPY . .

# Copiar y dar permisos al script de inicio
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 3002

CMD ["docker-entrypoint.sh"]
