import httpx
from typing import Dict, Optional
from config import settings
from utils.circuit_breaker import get_circuit_breaker
from utils.retry import retry_with_backoff
import logging

logger = logging.getLogger(__name__)

class App2Client:
    """Cliente HTTP para comunicarse con App2 (Gestión Administrativa)"""
    
    def __init__(self):
        self.base_url = settings.APP2_URL
        self.timeout = settings.REQUEST_TIMEOUT
        self.circuit_breaker = get_circuit_breaker("app2")
    
    async def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Realiza una petición HTTP con manejo de errores"""
        url = f"{self.base_url}{endpoint}"
        
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
    
    async def create_patient(self, patient_data: Dict) -> Dict:
        """
        Crea un nuevo paciente en App2
        Endpoint App2: POST /patients
        """
        if not self.circuit_breaker.can_execute():
            logger.warning("Circuit Breaker OPEN para App2 - No se puede crear paciente")
            raise Exception("Servicio App2 no disponible temporalmente")
        
        try:
            endpoint = "/patients"
            data = await retry_with_backoff(
                self._make_request,
                endpoint,
                method="POST",
                data=patient_data
            )
            
            self.circuit_breaker.record_success()
            logger.info(f"Paciente creado exitosamente: {patient_data.get('rut')}")
            return data
        except Exception as e:
            logger.error(f"Error creando paciente en App2: {e}")
            self.circuit_breaker.record_failure()
            raise
    
    async def update_patient(self, patient_rut: str, patient_data: Dict) -> Dict:
        """
        Actualiza datos de un paciente en App2
        Endpoint App2: PUT /patients/{rut}
        """
        if not self.circuit_breaker.can_execute():
            logger.warning("Circuit Breaker OPEN para App2 - No se puede actualizar paciente")
            raise Exception("Servicio App2 no disponible temporalmente")
        
        try:
            endpoint = f"/patients/{patient_rut}"
            data = await retry_with_backoff(
                self._make_request,
                endpoint,
                method="PUT",
                data=patient_data
            )
            
            self.circuit_breaker.record_success()
            logger.info(f"Paciente actualizado exitosamente: {patient_rut}")
            return data
        except Exception as e:
            logger.error(f"Error actualizando paciente en App2: {e}")
            self.circuit_breaker.record_failure()
            raise
    
    async def create_payment(self, payment_data: Dict) -> Dict:
        """
        Registra un nuevo pago en App2
        Endpoint App2: POST /payments
        """
        if not self.circuit_breaker.can_execute():
            logger.warning("Circuit Breaker OPEN para App2 - No se puede registrar pago")
            raise Exception("Servicio App2 no disponible temporalmente")
        
        try:
            endpoint = "/payments"
            data = await retry_with_backoff(
                self._make_request,
                endpoint,
                method="POST",
                data=payment_data
            )
            
            self.circuit_breaker.record_success()
            logger.info(f"Pago registrado exitosamente para paciente: {payment_data.get('patient_rut')}")
            return data
        except Exception as e:
            logger.error(f"Error registrando pago en App2: {e}")
            self.circuit_breaker.record_failure()
            raise
    
    async def generate_voucher(self, voucher_data: Dict) -> Dict:
        """
        Genera un comprobante de pago en App2
        Endpoint App2: POST /vouchers
        """
        if not self.circuit_breaker.can_execute():
            logger.warning("Circuit Breaker OPEN para App2 - No se puede generar comprobante")
            raise Exception("Servicio App2 no disponible temporalmente")
        
        try:
            endpoint = "/vouchers"
            data = await retry_with_backoff(
                self._make_request,
                endpoint,
                method="POST",
                data=voucher_data
            )
            
            self.circuit_breaker.record_success()
            logger.info(f"Comprobante generado exitosamente para paciente: {voucher_data.get('patient_rut')}")
            return data
        except Exception as e:
            logger.error(f"Error generando comprobante en App2: {e}")
            self.circuit_breaker.record_failure()
            raise
    
    async def get_payment_info(self, patient_rut: str) -> Optional[Dict]:
        """
        Obtiene información de pagos y facturas del paciente
        Endpoint App2: GET /payments/{patient_id}
        """
        if not self.circuit_breaker.can_execute():
            logger.warning("Circuit Breaker OPEN para App2 - Retornando datos mock")
            return self._mock_payment_info(patient_rut)
        
        try:
            # Primero obtener el paciente para conseguir su ID
            patient = await self.get_patient_data(patient_rut)
            if not patient:
                logger.warning(f"Paciente no encontrado: {patient_rut}, usando mock")
                return self._mock_payment_info(patient_rut)
            
            patient_id = patient.get('id')
            if not patient_id:
                logger.error(f"ID de paciente no encontrado para {patient_rut}")
                return self._mock_payment_info(patient_rut)
            
            # Intentar obtener pagos
            payments_endpoint = f"/payments/{patient_id}"
            try:
                payments_data = await retry_with_backoff(self._make_request, payments_endpoint)
            except:
                # Si no hay pagos, retornar lista vacía
                payments_data = []
            
            # Intentar obtener facturas (invoices)
            try:
                invoices_endpoint = f"/invoices/{patient_id}"
                invoices_data = await self._make_request(invoices_endpoint)
            except:
                invoices_data = []
            
            # Transformar datos al formato esperado por App3
            result = self._transform_payment_info(payments_data, invoices_data, patient_rut)
            
            self.circuit_breaker.record_success()
            logger.info(f"Información de pagos obtenida para paciente {patient_rut} (ID: {patient_id})")
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo información de App2: {e}")
            self.circuit_breaker.record_failure()
            # Fallback a datos mock
            return self._mock_payment_info(patient_rut)
    
    async def get_patient_data(self, patient_rut: str) -> Optional[Dict]:
        """
        Obtiene datos personales del paciente
        Endpoint App2: GET /patients?rut={rut}
        """
        if not self.circuit_breaker.can_execute():
            logger.warning("Circuit Breaker OPEN para App2")
            return None
        
        try:
            # Usar query parameter para buscar directamente por RUT
            endpoint = f"/patients?rut={patient_rut}"
            data = await retry_with_backoff(self._make_request, endpoint)
            
            self.circuit_breaker.record_success()
            return data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de paciente de App2: {e}")
            self.circuit_breaker.record_failure()
            return None
    
    def _transform_payment_info(self, payments_data: any, invoices_data: any, patient_rut: str) -> Dict:
        """Transforma datos de App2 al formato esperado por App3"""
        payments = []
        pending_invoices = []
        paid_invoices = []
        total_debt = 0.0
        
        # Procesar pagos
        if isinstance(payments_data, list):
            for payment in payments_data:
                amount = payment.get('monto', payment.get('amount', 0))
                payments.append({
                    'id': payment.get('id'),
                    'date': payment.get('fecha', payment.get('created_at', '')),
                    'amount': float(amount) if amount is not None else 0.0,
                    'method': payment.get('metodo_pago', payment.get('method', 'Efectivo')),
                    'description': payment.get('descripcion', payment.get('description', ''))
                })
        
        # Procesar facturas (separar en pagadas y pendientes)
        if isinstance(invoices_data, list):
            for invoice in invoices_data:
                is_paid = invoice.get('pagada', False)
                amount = invoice.get('monto', invoice.get('amount', 0))
                amount_float = float(amount) if amount is not None else 0.0
                
                invoice_data = {
                    'id': invoice.get('id'),
                    'date': invoice.get('fecha_emision', invoice.get('created_at', '')),
                    'amount': amount_float,
                    'description': invoice.get('descripcion', invoice.get('description', ''))
                }
                
                if is_paid:
                    # Factura pagada
                    paid_invoices.append(invoice_data)
                else:
                    # Factura pendiente
                    pending_invoices.append(invoice_data)
                    total_debt += amount_float
        
        return {
            'patient_rut': patient_rut,
            'payments': payments,
            'pending_invoices': pending_invoices,
            'paid_invoices': paid_invoices,  # Nuevo campo
            'total_debt': total_debt
        }
    
    def _mock_payment_info(self, patient_rut: str) -> Dict:
        """Datos mock cuando App2 no está disponible"""
        return {
            'patient_rut': patient_rut,
            'payments': [],
            'pending_invoices': [
                {
                    'id': 999,
                    'date': '2024-12-01',
                    'amount': 0,
                    'description': 'Servicio temporalmente no disponible',
                    'due_date': '2024-12-31'
                }
            ],
            'total_debt': 0
        }
