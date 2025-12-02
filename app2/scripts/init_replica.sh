#!/bin/bash
set -e

if [ ! -s "$PGDATA/PG_VERSION" ]; then
    echo "Replicando datos desde la primaria..."
    pg_basebackup -h postgres_primary -D ${PGDATA} -U ${POSTGRES_USER} -v -P --wal-method=stream
    
    echo "Creando standby.signal..."
    touch ${PGDATA}/standby.signal
    
    # Configurar información de conexión para la réplica
    echo "primary_conninfo = 'host=postgres_primary port=5432 user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}'" >> ${PGDATA}/postgresql.auto.conf
    
    chown -R postgres:postgres ${PGDATA}
    chmod 700 ${PGDATA}
fi

exec "$@"
