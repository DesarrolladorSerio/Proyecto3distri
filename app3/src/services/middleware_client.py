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
