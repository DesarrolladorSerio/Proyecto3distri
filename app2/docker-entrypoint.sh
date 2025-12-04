#!/bin/bash
set -e

echo "Esperando a que PostgreSQL esté listo..."
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_DATABASE" -c '\q'; do
  echo "PostgreSQL no está listo - esperando..."
  sleep 2
done

echo "PostgreSQL está listo. Ejecutando migraciones..."
npx sequelize-cli db:migrate

echo "Ejecutando seeders..."
npx sequelize-cli db:seed:all || true

echo "Iniciando aplicación..."
exec npm start
