from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime
from src.models.appointment import Appointment
from src.config.database import db
from src.services.middleware_client import MiddlewareClient
from src.config.config import Config
from src.routes.patient_routes import login_required
import logging

logger = logging.getLogger(__name__)

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
    """
    Crear una nueva cita médica
    Flujo completo:
    1. Registrar/obtener paciente en App2
    2. Obtener ID del médico desde nombre
    3. Crear consulta en App1
    4. Guardar cita en DB local (opcional)
    """
    try:
        data = request.form
        
        # Extraer datos del paciente
        patient_data = {
            'rut': data.get('patient_rut'),
            'nombre': data.get('patient_name'),
            'email': data.get('patient_email'),
            'telefono': data.get('patient_phone'),
            'direccion': data.get('patient_address')
        }
        
        # Paso 1: Registrar o obtener paciente en App2
        middleware = MiddlewareClient(Config.MIDDLEWARE_URL)
        patient = middleware.register_or_get_patient(patient_data)
        
        if not patient:
            logger.error(f"No se pudo registrar paciente: {patient_data['rut']}")
            if request.is_json or request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'No se pudo registrar el paciente en App2'}), 500
            else:
                return "Error: No se pudo registrar el paciente en el sistema administrativo", 500
        
        patient_id = patient.get('id')
        logger.info(f"Paciente obtenido/registrado: ID={patient_id}, RUT={patient_data['rut']}")
        
        # Paso 2: Obtener médicos y buscar ID por nombre
        doctors = middleware.get_available_doctors()
        doctor_name = data.get('doctor_name')
        doctor_id = None
        specialty = data.get('specialty', '')
        
        for doctor in doctors:
            if doctor.get('name') == doctor_name:
                doctor_id = doctor.get('id')
                break
        
        if not doctor_id:
            logger.error(f"Médico no encontrado: {doctor_name}")
            if request.is_json or request.headers.get('Accept') == 'application/json':
                return jsonify({'error': f'Médico no encontrado: {doctor_name}'}), 404
            else:
                return f"Error: Médico no encontrado: {doctor_name}", 404
        
        # Paso 3: Criar consulta en App1
        consultation_data = {
            'id_paciente': patient_id,
            'id_medico': doctor_id,
            'fecha': data.get('appointment_date'),
            'motivo': data.get('notes', ''),
            'diagnostico': '',  # Pendiente
            'tratamiento': '',  # Pendiente
        }
        
        consultation = middleware.create_consultation(consultation_data)
        
        if not consultation:
            logger.error(f"No se pudo crear consulta para paciente {patient_id}")
            if request.is_json or request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'No se pudo crear la consulta en App1'}), 500
            else:
                return "Error: No se pudo agendar la consulta médica", 500
        
        logger.info(f"Consulta creada exitosamente para paciente {patient_id}")
        
        # Paso 4: Guardar en DB local (opcional, para historial en App3)
        appointment = Appointment(
            patient_rut=data.get('patient_rut'),
            patient_name=data.get('patient_name'),
            doctor_name=doctor_name,
            specialty=specialty,
            appointment_date=datetime.fromisoformat(data.get('appointment_date')),
            notes=data.get('notes', '')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        logger.info(f"Cita guardada localmente: ID={appointment.id}")
        
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': True,
                'patient_id': patient_id,
                'appointment_id': appointment.id,
                'consultation': consultation
            }), 201
        else:
            return redirect(url_for('appointment.list_appointments'))
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en create_appointment: {e}")
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
