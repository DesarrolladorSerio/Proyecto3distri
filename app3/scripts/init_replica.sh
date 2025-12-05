#!/bin/bash
set -e

echo "Waiting for primary to be ready..."
until mysql -h mysql_primary -u root -prootpass -e "SELECT 1" &> /dev/null; do
    echo "Primary not ready yet..."
    sleep 2
done

echo "Configuring replication on replica..."
mysql -h localhost -u root -prootpass <<-EOSQL
    STOP SLAVE;
    CHANGE MASTER TO
        MASTER_HOST='mysql_primary',
        MASTER_USER='repl',
        MASTER_PASSWORD='replpass',
        MASTER_LOG_FILE='mysql-bin.000001',
        MASTER_LOG_POS=4;
    START SLAVE;
EOSQL

echo "MySQL replica configured successfully"
