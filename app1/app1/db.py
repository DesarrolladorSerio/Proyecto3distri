import os
import time
import logging
import mysql.connector
from mysql.connector import Error

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('App1-DB')

# Cache del último host exitoso para optimizar conexiones
_last_successful_host = None

def get_connection(max_retries=5, retry_delay=2):
    """
    Obtiene una conexión a la base de datos con failover automático y reintentos.
    
    Orden de conexión:
    1. Intenta conectarse al host primary (DB_HOST)
    2. Si falla, intenta conectarse al host replica (DB_REPLICA_HOST)
    3. Reintenta hasta max_retries veces con delay entre intentos
    
    Args:
        max_retries: Número máximo de intentos de conexión
        retry_delay: Segundos de espera entre reintentos
        
    Returns:
        Connection object si tiene éxito, None si falla
    """
    global _last_successful_host
    
    # Configuración de hosts
    primary_host = os.getenv("DB_HOST", "mariadb-master")
    replica_host = os.getenv("DB_REPLICA_HOST", "mariadb-replica")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_USER", "appuser")
    password = os.getenv("DB_PASSWORD", "apppass")
    database = os.getenv("DB_NAME", "gestion_medica")
    
    # Lista de hosts a intentar (primary primero, luego replica)
    hosts_to_try = [primary_host, replica_host]
    
    # Si tenemos un último host exitoso, intentarlo primero
    if _last_successful_host and _last_successful_host in hosts_to_try:
        hosts_to_try.remove(_last_successful_host)
        hosts_to_try.insert(0, _last_successful_host)
    
    for attempt in range(max_retries):
        for host in hosts_to_try:
            try:
                logger.info(f"🔌 Intento {attempt + 1}/{max_retries}: Conectando a {host}...")
                
                conn = mysql.connector.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database,
                    connect_timeout=5
                )
                
                # Verificar que la conexión está activa
                conn.ping(reconnect=False)
                
                # Conexión exitosa
                _last_successful_host = host
                logger.info(f"✅ Conectado exitosamente a {host} ({database})")
                return conn
                
            except Error as e:
                logger.warning(f"⚠️  Conexión a {host} falló: {e}")
                continue  # Intentar siguiente host
        
        # Si llegamos aquí, todos los hosts fallaron en este intento
        if attempt < max_retries - 1:
            logger.warning(f"💤 Esperando {retry_delay}s antes del siguiente intento...")
            time.sleep(retry_delay)
    
    # Todos los intentos fallaron
    logger.error(f"❌ No se pudo conectar a ningún host después de {max_retries} intentos")
    logger.error(f"   Hosts intentados: {hosts_to_try}")
    return None
