from flask_sqlalchemy import SQLAlchemy
import time
import logging

logger = logging.getLogger(__name__)
db = SQLAlchemy()

def init_db(app):
    """Inicializa la base de datos con reintentos"""
    db.init_app(app)
    
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # Intenta crear las tablas
                db.create_all()
                logger.info("Base de datos inicializada correctamente")
                return
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Intento {attempt + 1}/{max_retries} falló: {e}. Reintentando en {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error(f"No se pudo conectar a la base de datos después de {max_retries} intentos")
                raise
