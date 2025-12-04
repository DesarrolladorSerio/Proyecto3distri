from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for, flash
from src.services.middleware_client import MiddlewareClient
from src.config.config import Config
from functools import wraps

patient_bp = Blueprint('patient', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'patient_rut' not in session:
            return redirect(url_for('patient.login'))
        return f(*args, **kwargs)
    return decorated_function

@patient_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        rut = request.form.get('rut', '').strip()
        if not rut:
            flash('Por favor ingrese un RUT válido', 'danger')
            return render_template('login.html')
        
        # Verificar que el RUT exista en la base de datos a través del middleware
        try:
            middleware = MiddlewareClient(Config.MIDDLEWARE_URL)
            # Intentar obtener el paciente desde App2 vía middleware
            url = f"{Config.MIDDLEWARE_URL}/api/patient/{rut}"
            import requests
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                # El paciente existe, permitir login
                patient = response.json()
                session['patient_rut'] = rut
                session['patient_name'] = patient.get('nombre', 'Paciente')
                flash(f'Bienvenido {patient.get("nombre", "")}!', 'success')
                return redirect(url_for('patient.dashboard'))
            elif response.status_code == 404:
                # El paciente no existe
                flash('RUT no existe en el sistema', 'danger')
            else:
                # Otro error
                flash('Error al verificar RUT. Intente nuevamente.', 'danger')
        except Exception as e:
            flash('Error de conexión. Intente nuevamente más tarde.', 'danger')
            current_app.logger.error(f"Error en login: {e}")
        
    return render_template('login.html')

@patient_bp.route('/logout')
def logout():
    session.pop('patient_rut', None)
    return redirect(url_for('patient.login'))

@patient_bp.route('/')
@login_required
def dashboard():
    """Dashboard principal del paciente"""
    patient_rut = session['patient_rut']
    return render_template('dashboard.html', patient_rut=patient_rut)

@patient_bp.route('/history')
@login_required
def medical_history():
    """Visualización del historial médico"""
    patient_rut = session['patient_rut']
    
    middleware = MiddlewareClient(Config.MIDDLEWARE_URL)
    history = middleware.get_patient_medical_history(patient_rut)
    
    return render_template('history.html', 
                         patient_rut=patient_rut,
                         history=history)

@patient_bp.route('/payments')
@login_required
def payment_info():
    """Visualización de información de pagos"""
    patient_rut = session['patient_rut']
    
    middleware = MiddlewareClient(Config.MIDDLEWARE_URL)
    payments = middleware.get_patient_payment_info(patient_rut)
    
    return render_template('payments.html',
                         patient_rut=patient_rut,
                         payments=payments)

@patient_bp.route('/api/patient/<patient_rut>/summary')
def patient_summary(patient_rut):
    """API para obtener resumen del paciente (historial + pagos)"""
    middleware = MiddlewareClient(Config.MIDDLEWARE_URL)
    
    history = middleware.get_patient_medical_history(patient_rut)
    payments = middleware.get_patient_payment_info(patient_rut)
    
    return jsonify({
        'patient_rut': patient_rut,
        'medical_history': history,
        'payment_info': payments
    })
