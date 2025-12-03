from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime
from src.models.appointment import Appointment
from src.config.database import db
from src.services.middleware_client import MiddlewareClient
from src.config.config import Config
from src.routes.patient_routes import login_required

appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/appointments')
@login_required
def list_appointments():
    """Lista de citas del paciente"""
    patient_rut = session['patient_rut']
    
    # Obtener citas de la base de datos local
    appointments = Appointment.query.filter_by(patient_rut=patient_rut)\
                                   .order_by(Appointment.appointment_date.desc())\
                                   .all()
    
    # Obtener médicos disponibles para crear nuevas citas
    middleware = MiddlewareClient(Config.MIDDLEWARE_URL)
    doctors = middleware.get_available_doctors()
    
    return render_template('appointments.html',
                         patient_rut=patient_rut,
                         appointments=appointments,
                         doctors=doctors)

@appointment_bp.route('/appointments/create', methods=['POST'])
def create_appointment():
    """Crear una nueva cita médica"""
    try:
        data = request.form
        
        appointment = Appointment(
            patient_rut=data.get('patient_rut'),
            patient_name=data.get('patient_name'),
            doctor_name=data.get('doctor_name'),
            specialty=data.get('specialty'),
            appointment_date=datetime.fromisoformat(data.get('appointment_date')),
            notes=data.get('notes', '')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify(appointment.to_dict()), 201
        else:
            return redirect(url_for('appointment.list_appointments'))
            
    except Exception as e:
        db.session.rollback()
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify({'error': str(e)}), 400
        else:
            return f"Error al crear cita: {e}", 400

@appointment_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
def cancel_appointment(appointment_id):
    """Cancelar una cita médica"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment.status = 'cancelled'
        appointment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify(appointment.to_dict())
        else:
            return redirect(url_for('appointment.list_appointments'))
            
    except Exception as e:
        db.session.rollback()
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify({'error': str(e)}), 400
        else:
            return f"Error al cancelar cita: {e}", 400

@appointment_bp.route('/api/appointments', methods=['GET', 'POST'])
def api_appointments():
    """API REST para gestión de citas"""
    if request.method == 'GET':
        patient_rut = request.args.get('patient_rut')
        if patient_rut:
            appointments = Appointment.query.filter_by(patient_rut=patient_rut).all()
        else:
            appointments = Appointment.query.all()
        
        return jsonify([apt.to_dict() for apt in appointments])
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            appointment = Appointment(
                patient_rut=data.get('patient_rut'),
                patient_name=data.get('patient_name'),
                doctor_name=data.get('doctor_name'),
                specialty=data.get('specialty'),
                appointment_date=datetime.fromisoformat(data.get('appointment_date')),
                notes=data.get('notes', '')
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            return jsonify(appointment.to_dict()), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
