import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class MiddlewareClient:
    """Cliente para comunicarse con el Middleware"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.timeout = 5  # segundos
    
    def get_patient_medical_history(self, patient_rut: str) -> Optional[Dict]:
        """Obtiene el historial médico del paciente desde App1 vía Middleware"""
        try:
            url = f"{self.base_url}/api/medical-history/{patient_rut}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener historial médico: {e}")
            # Retornar datos mock para desarrollo
            return self._mock_medical_history(patient_rut)
    
    def get_patient_payment_info(self, patient_rut: str) -> Optional[Dict]:
        """Obtiene información de pagos del paciente desde App2 vía Middleware"""
        try:
            url = f"{self.base_url}/api/payments/{patient_rut}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener información de pagos: {e}")
            # Retornar datos mock para desarrollo
            return self._mock_payment_info(patient_rut)
    
    def get_available_doctors(self, specialty: Optional[str] = None) -> List[Dict]:
        """Obtiene lista de médicos disponibles desde App1 vía Middleware"""
        try:
            url = f"{self.base_url}/api/doctors"
            params = {'specialty': specialty} if specialty else {}
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener médicos disponibles: {e}")
            # Retornar datos mock para desarrollo
            return self._mock_doctors(specialty)
    
    # Métodos mock para desarrollo (se eliminarán cuando el Middleware esté listo)
    
    def _mock_medical_history(self, patient_rut: str) -> Dict:
        """Datos mock de historial médico"""
        return {
            'patient_rut': patient_rut,
            'consultations': [
                {
                    'id': 1,
                    'date': '2024-11-15',
                    'doctor': 'Dr. García',
                    'specialty': 'Medicina General',
                    'diagnosis': 'Gripe estacional',
                    'treatment': 'Reposo y antifebriles'
                },
                {
                    'id': 2,
                    'date': '2024-10-20',
                    'doctor': 'Dra. López',
                    'specialty': 'Cardiología',
                    'diagnosis': 'Control rutinario',
                    'treatment': 'Mantener medicación actual'
                }
            ]
        }
    
    def _mock_payment_info(self, patient_rut: str) -> Dict:
        """Datos mock de información de pagos"""
        return {
            'patient_rut': patient_rut,
            'payments': [
                {
                    'id': 1,
                    'date': '2024-11-20',
                    'amount': 50000,
                    'method': 'Tarjeta de crédito',
                    'description': 'Consulta Medicina General'
                },
                {
                    'id': 2,
                    'date': '2024-10-25',
                    'amount': 80000,
                    'method': 'Efectivo',
                    'description': 'Consulta Cardiología'
                }
            ],
            'pending_invoices': [
                {
                    'id': 101,
                    'date': '2024-12-01',
                    'amount': 60000,
                    'description': 'Exámenes de laboratorio',
                    'due_date': '2024-12-15'
                }
            ],
            'total_debt': 60000
        }
    
    def _mock_doctors(self, specialty: Optional[str] = None) -> List[Dict]:
        """Datos mock de médicos disponibles"""
        all_doctors = [
            {
                'id': 1,
                'name': 'Dr. Juan García',
                'specialty': 'Medicina General',
                'available_slots': ['2024-12-10 09:00', '2024-12-10 10:00', '2024-12-11 14:00']
            },
            {
                'id': 2,
                'name': 'Dra. María López',
                'specialty': 'Cardiología',
                'available_slots': ['2024-12-10 11:00', '2024-12-12 09:00', '2024-12-12 10:00']
            },
            {
                'id': 3,
                'name': 'Dr. Pedro Martínez',
                'specialty': 'Pediatría',
                'available_slots': ['2024-12-09 15:00', '2024-12-10 15:00', '2024-12-11 16:00']
            }
        ]
        if specialty:
            return [d for d in all_doctors if d['specialty'].lower() == specialty.lower()]
        return all_doctors
    
    def register_or_get_patient(self, patient_data: Dict) -> Optional[Dict]:
        """
        Registra un paciente en App2 o retorna sus datos si ya existe.
        
        Args:
            patient_data: Dict con keys: rut, nombre, email, telefono, direccion
            
        Returns:
            Dict con datos del paciente incluyendo 'id', o None si falla
        """
        try:
            # Primero intentar obtener el paciente por RUT
            url = f"{self.base_url}/api/patient/{patient_data['rut']}"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                # Paciente existe, retornar sus datos
                patient = response.json()
                logger.info(f"Paciente ya registrado: {patient_data['rut']} (ID: {patient.get('id')})")
                return patient
            elif response.status_code == 404:
                # Paciente no existe, registrarlo
                logger.info(f"Paciente no encontrado, registrando: {patient_data['rut']}")
                url_create = f"{self.base_url}/api/patients"
                response_create = requests.post(url_create, json=patient_data, timeout=self.timeout)
                response_create.raise_for_status()
                new_patient = response_create.json()
                logger.info(f"Paciente creado exitosamente: {patient_data['rut']} (ID: {new_patient.get('id')})")
                return new_patient
            else:
                logger.error(f"Error inesperado al buscar paciente: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al registrar/obtener paciente: {e}")
            return None
    
    def create_consultation(self, consultation_data: Dict) -> Optional[Dict]:
        """
        Crea una consulta médica en App1 a través del middleware.
        
        Args:
            consultation_data: Dict con keys que serán mapeados a formato de App1
            
        Returns:
            Dict con respuesta de creación, o None si falla
        """
        try:
            url = f"{self.base_url}/api/consultations"
            
            # Asegurar que el formato sea correcto para la API del Middleware
            # El middleware luego lo convierte al formato de App1
            data = {
                "patient_id": str(consultation_data.get('id_paciente', consultation_data.get('patient_id', ''))),
                "doctor_id": int(consultation_data.get('id_medico', consultation_data.get('doctor_id', 0))),
                "specialty": consultation_data.get('specialty', ''),
                "diagnosis": consultation_data.get('diagnostico', consultation_data.get('diagnosis', '')),
                "treatment": consultation_data.get('tratamiento', consultation_data.get('treatment', '')),
                "notes": consultation_data.get('motivo', consultation_data.get('notes', '')),
                "fecha": consultation_data.get('fecha', consultation_data.get('appointment_date', ''))
            }
            
            response = requests.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Consulta creada exitosamente para paciente {data['patient_id']}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al crear consulta: {e}")
            return None
