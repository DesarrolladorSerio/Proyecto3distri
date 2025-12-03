#!/bin/bash
set -e

echo "Configurando servidor MySQL primario para replicación..."

# Crear usuario de replicación
mysql -u root -p${MYSQL_ROOT_PASSWORD} <<-EOSQL
    CREATE USER IF NOT EXISTS 'replicator'@'%' IDENTIFIED WITH mysql_native_password BY 'replicator_password';
    GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';
    FLUSH PRIVILEGES;
EOSQL

echo "Usuario de replicación creado correctamente."
