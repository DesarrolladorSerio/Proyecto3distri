#!/bin/bash
set -e

echo "Esperando a que el servidor primario esté listo..."
sleep 20

echo "Configurando servidor MySQL réplica..."

# Obtener la posición del log binario del maestro
MASTER_STATUS=$(mysql -h mysql_primary -u root -prootpass -e "SHOW MASTER STATUS\G" 2>/dev/null || echo "")

if [ -z "$MASTER_STATUS" ]; then
    echo "No se pudo conectar al servidor primario. Reintentando..."
    sleep 10
    MASTER_STATUS=$(mysql -h mysql_primary -u root -prootpass -e "SHOW MASTER STATUS\G")
fi

LOG_FILE=$(echo "$MASTER_STATUS" | grep "File:" | awk '{print $2}')
LOG_POS=$(echo "$MASTER_STATUS" | grep "Position:" | awk '{print $2}')

echo "Configurando réplica con LOG_FILE=$LOG_FILE y LOG_POS=$LOG_POS"

# Configurar la réplica
mysql -u root -p${MYSQL_ROOT_PASSWORD} <<-EOSQL
    CHANGE MASTER TO
        MASTER_HOST='mysql_primary',
        MASTER_USER='replicator',
        MASTER_PASSWORD='replicator_password',
        MASTER_LOG_FILE='${LOG_FILE}',
        MASTER_LOG_POS=${LOG_POS};
    
    START SLAVE;
EOSQL

echo "Réplica configurada correctamente."

# Verificar estado
mysql -u root -p${MYSQL_ROOT_PASSWORD} -e "SHOW SLAVE STATUS\G"
