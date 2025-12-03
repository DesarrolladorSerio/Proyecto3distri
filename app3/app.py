from flask import Flask, jsonify
from src.config.config import Config
from src.config.database import init_db
from src.routes.patient_routes import patient_bp
from src.routes.appointment_routes import appointment_bp
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = 'supersecretkey' # En producción esto debería ir en .env
    
    # Inicializar base de datos
    init_db(app)
    
    # Registrar blueprints
    # Registrar blueprints
    app.register_blueprint(patient_bp)
    app.register_blueprint(appointment_bp)
    
    # Filtro para formatear fechas
    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%d-%m-%Y %H:%M'):
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                from dateutil import parser
                dt = parser.parse(value)
                return dt.strftime(format)
            except:
                return value
        return value.strftime(format)
    
    # Health check
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'app3'}), 200
    
    logger.info("App 3 - Portal del Paciente iniciado")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=Config.PORT, debug=True)
