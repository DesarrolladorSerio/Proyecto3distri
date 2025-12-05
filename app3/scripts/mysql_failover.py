#!/usr/bin/env python3
"""
MySQL Automatic Failover Monitor
Detecta cuando el primary cae y promueve automáticamente la réplica
"""
import time
import logging
import mysql.connector
from mysql.connector import Error
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MySQL-Failover')

# Configuración
PRIMARY_HOST = os.getenv('PRIMARY_HOST', 'mysql_primary')
REPLICA_HOST = os.getenv('REPLICA_HOST', 'mysql_replica')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'rootpass')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '5'))
MAX_FAILURES = int(os.getenv('MAX_FAILURES', '3'))

class MySQLFailover:
    def __init__(self):
        self.current_primary = PRIMARY_HOST
        self.failure_count = 0
        self.is_failover_active = False
        
    def check_health(self, host):
        """Verifica si el host está disponible"""
        try:
            conn = mysql.connector.connect(
                host=host,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=3
            )
            conn.ping(reconnect=False)
            conn.close()
            return True
        except Error as e:
            logger.warning(f"Health check failed for {host}: {e}")
            return False
    
    def promote_replica(self):
        """Promueve la réplica a primary"""
        logger.info(f"🚨 PROMOTING {REPLICA_HOST} to PRIMARY")
        
        try:
            conn = mysql.connector.connect(
                host=REPLICA_HOST,
                user=DB_USER,
                password=DB_PASSWORD
            )
            cursor = conn.cursor()
            
            # Detener la replicación
            cursor.execute("STOP SLAVE;")
            logger.info("✅ Stopped replication on replica")
            
            # Resetear la configuración de slave
            cursor.execute("RESET SLAVE ALL;")
            logger.info("✅ Reset slave configuration")
            
            # Habilitar escrituras (por si acaso estaba en read-only)
            cursor.execute("SET GLOBAL read_only = OFF;")
            cursor.execute("SET GLOBAL super_read_only = OFF;")
            logger.info("✅ Enabled writes on new primary")
            
            cursor.close()
            conn.close()
            
            self.current_primary = REPLICA_HOST
            self.is_failover_active = True
            logger.info(f"✅ FAILOVER COMPLETE: {REPLICA_HOST} is now the primary")
            
            return True
            
        except Error as e:
            logger.error(f"❌ Error during failover: {e}")
            return False
    
    def monitor(self):
        """Loop principal de monitoreo"""
        logger.info(f"🔍 Starting MySQL failover monitor")
        logger.info(f"   Primary: {PRIMARY_HOST}")
        logger.info(f"   Replica: {REPLICA_HOST}")
        logger.info(f"   Check interval: {CHECK_INTERVAL}s")
        
        while True:
            try:
                # Verificar el primary actual
                is_healthy = self.check_health(self.current_primary)
                
                if is_healthy:
                    self.failure_count = 0
                    if self.is_failover_active:
                        logger.info(f"✅ New primary {self.current_primary} is healthy")
                else:
                    self.failure_count += 1
                    logger.warning(
                        f"⚠️  Primary {self.current_primary} unhealthy "
                        f"({self.failure_count}/{MAX_FAILURES})"
                    )
                    
                    # Si alcanzamos el umbral de fallos, hacer failover
                    if self.failure_count >= MAX_FAILURES and not self.is_failover_active:
                        logger.error(f"🚨 PRIMARY {self.current_primary} IS DOWN!")
                        
                        # Verificar que la réplica esté disponible
                        if self.check_health(REPLICA_HOST):
                            self.promote_replica()
                        else:
                            logger.error(f"❌ CRITICAL: Replica {REPLICA_HOST} is also down!")
                
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Monitor stopped by user")
                sys.exit(0)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    monitor = MySQLFailover()
    monitor.monitor()
