from flask import Flask
from flask_cors import CORS

from controllers.consultas_controller import consultas_bp
from controllers.medicos_controller import medicos_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(consultas_bp, url_prefix="/consultas")
    app.register_blueprint(medicos_bp, url_prefix="/medicos")

    @app.get("/")
    def home():
        return {"status": "ok", "app": "App1 - Gestión Médica"}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
