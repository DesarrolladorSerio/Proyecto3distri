#!/bin/bash
set -e

# Crear usuario de replicación
mysql -u root -p${MYSQL_ROOT_PASSWORD} <<-EOSQL
    CREATE USER IF NOT EXISTS 'repl'@'%' IDENTIFIED BY 'replpass';
    GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
    FLUSH PRIVILEGES;
EOSQL

echo "MySQL primary configured with replication user"
