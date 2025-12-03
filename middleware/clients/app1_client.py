import httpx
from typing import Dict, List, Optional
from config import settings
from utils.circuit_breaker import get_circuit_breaker
from utils.retry import retry_with_backoff
import logging

logger = logging.getLogger(__name__)

class App1Client:
    """Cliente HTTP para comunicarse con App1 (Gestión Médica)"""
    
    def __init__(self):
        self.base_url = settings.APP1_URL
        self.replica_url = settings.APP1_REPLICA_URL
        self.timeout = settings.REQUEST_TIMEOUT
        self.circuit_breaker = get_circuit_breaker("app1")
    
    async def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None, use_replica: bool = False) -> Dict:
        """Realiza una petición HTTP con manejo de errores"""
        url = f"{self.replica_url if use_replica else self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=data)
            elif method == "PUT":
                response = await client.put(url, json=data)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            response.raise_for_status()
            return response.json()
    
    async def create_consulta(self, consulta_data: Dict) -> Dict:
        """
        Crea una nueva consulta médica en App1
        Endpoint App1: POST /consultas/
        """
        if not self.circuit_breaker.can_execute():
            logger.warning("Circuit Breaker OPEN para App1 - No se puede crear consulta")
            raise Exception("Servicio App1 no disponible temporalmente")
        
        try:
            endpoint = "/consultas/"
            data = await retry_with_backoff(
                self._make_request,
                endpoint,
                method="POST",
                data=consulta_data
            )
            
            self.circuit_breaker.record_success()
            logger.info(f"Consulta creada exitosamente para paciente {consulta_data.get('patient_id')}")
            return data
        except Exception as e:
            logger.error(f"Error creando consulta en App1: {e}")
            self.circuit_breaker.record_failure()
            raise
    
    async def update_disponibilidad(self, disponibilidad_data: Dict) -> Dict:
        """
        Actualiza la disponibilidad de un médico en App1
        Endpoint App1: POST /medicos/disponibilidad
        """
        if not self.circuit_breaker.can_execute():
            logger.warning("Circuit Breaker OPEN para App1 - No se puede actualizar disponibilidad")
            raise Exception("Servicio App1 no disponible temporalmente")
        
        try:
            endpoint = "/medicos/disponibilidad"
            data = await retry_with_backoff(
                self._make_request,
                endpoint,
                method="POST",
                data=disponibilidad_data
            )
            
            self.circuit_breaker.record_success()
            logger.info(f"Disponibilidad actualizada para médico {disponibilidad_data.get('doctor_id')}")
            return data
        except Exception as e:
            logger.error(f"Error actualizando disponibilidad en App1: {e}")
            self.circuit_breaker.record_failure()
            raise
    
    async def get_historial_paciente(self, patient_id: str) -> Optional[Dict]:
        """
        Obtiene el historial médico de un paciente
        Endpoint App1: GET /consultas/paciente/{id}
        """
        if not self.circuit_breaker.can_execute():
            logger.warning("Circuit Breaker OPEN para App1 - Retornando datos mock")
            return self._mock_historial(patient_id)
        
        try:
            endpoint = f"/consultas/paciente/{patient_id}"
            data = await retry_with_backoff(self._make_request, endpoint)
            
            # Transformar datos de App1 al formato esperado por App3
            result = self._transform_historial(data, patient_id)
            
            self.circuit_breaker.record_success()
            logger.info(f"Historial obtenido exitosamente para paciente {patient_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo historial de App1: {e}")
            self.circuit_breaker.record_failure()
            
            # Intentar con réplica
            try:
                logger.info("Intentando con réplica de App1...")
                endpoint = f"/consultas/paciente/{patient_id}"
                data = await self._make_request(endpoint, use_replica=True)
                result = self._transform_historial(data, patient_id)
                logger.info("Historial obtenido desde réplica")
                return result
            except Exception as e2:
                logger.error(f"Réplica también falló: {e2}")
                # Fallback a datos mock
                return self._mock_historial(patient_id)
    
    async def get_medicos_disponibles(self, specialty: Optional[str] = None) -> List[Dict]:
        """
        Obtiene la lista de médicos disponibles
        Endpoint App1: GET /medicos/
        """
        if not self.circuit_breaker.can_execute():
            logger.warning("Circuit Breaker OPEN para App1 - Retornando datos mock")
            return self._mock_medicos(specialty)
        
        try:
            endpoint = "/medicos/"
            data = await retry_with_backoff(self._make_request, endpoint)
            
            # Transformar datos
            result = self._transform_medicos(data, specialty)
            
            self.circuit_breaker.record_success()
            logger.info("Lista de médicos obtenida exitosamente")
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo médicos de App1: {e}")
            self.circuit_breaker.record_failure()
            
            # Intentar con réplica
            try:
                logger.info("Intentando con réplica de App1...")
                data = await self._make_request(endpoint, use_replica=True)
                result = self._transform_medicos(data, specialty)
                logger.info("Médicos obtenidos desde réplica")
                return result
            except Exception as e2:
                logger.error(f"Réplica también falló: {e2}")
                return self._mock_medicos(specialty)
    
    def _transform_historial(self, data: Dict, patient_id: str) -> Dict:
        """Transforma datos de App1 al formato esperado por App3"""
        consultations = []
        
        # Asumiendo que App1 retorna una lista de consultas
        if isinstance(data, list):
            for consulta in data:
                consultations.append({
                    'id': consulta.get('id'),
                    'date': consulta.get('fecha_consulta', ''),
                    'doctor': consulta.get('nombre_medico', 'Dr. Desconocido'),
                    'specialty': consulta.get('especialidad', 'General'),
                    'diagnosis': consulta.get('diagnostico', ''),
                    'treatment': consulta.get('tratamiento', '')
                })
        elif isinstance(data, dict) and 'consultas' in data:
            for consulta in data['consultas']:
                consultations.append({
                    'id': consulta.get('id'),
                    'date': consulta.get('fecha_consulta', ''),
                    'doctor': consulta.get('nombre_medico', 'Dr. Desconocido'),
                    'specialty': consulta.get('especialidad', 'General'),
                    'diagnosis': consulta.get('diagnostico', ''),
                    'treatment': consulta.get('tratamiento', '')
                })
        
        return {
            'patient_rut': patient_id,
            'consultations': consultations
        }
    
    def _transform_medicos(self, data: Dict, specialty: Optional[str]) -> List[Dict]:
        """Transforma datos de médicos al formato esperado por App3"""
        medicos = []
        
        # Asumiendo que App1 retorna una lista de médicos
        if isinstance(data, list):
            source = data
        elif isinstance(data, dict) and 'medicos' in data:
            source = data['medicos']
        else:
            source = []
        
        for medico in source:
            # Filtrar por especialidad si se especificó
            if specialty and medico.get('especialidad', '').lower() != specialty.lower():
                continue
            
            medicos.append({
                'id': medico.get('id'),
                'name': medico.get('nombre', 'Dr. Desconocido'),
                'specialty': medico.get('especialidad', 'General'),
                'available_slots': medico.get('horarios_disponibles', [])
            })
        
        return medicos
    
    def _mock_historial(self, patient_id: str) -> Dict:
        """Datos mock cuando App1 no está disponible"""
        return {
            'patient_rut': patient_id,
            'consultations': [
                {
                    'id': 999,
                    'date': '2024-11-15',
                    'doctor': 'Dr. Mock (Servicio no disponible)',
                    'specialty': 'Medicina General',
                    'diagnosis': 'Servicio temporalmente no disponible',
                    'treatment': 'Por favor intente más tarde'
                }
            ]
        }
    
    def _mock_medicos(self, specialty: Optional[str]) -> List[Dict]:
        """Datos mock de médicos cuando App1 no está disponible"""
        return [
            {
                'id': 999,
                'name': 'Dr. Mock (Servicio no disponible)',
                'specialty': specialty or 'General',
                'available_slots': []
            }
        ]
