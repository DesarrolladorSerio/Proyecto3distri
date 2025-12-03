from fastapi import APIRouter, HTTPException
from clients.app2_client import App2Client
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["administrative"])

# Cliente de App2 (singleton)
app2_client = App2Client()

# Modelos de datos para POST
class PatientCreate(BaseModel):
    rut: str
    nombre: str
    email: str
    telefono: str
    direccion: str

class PatientUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class PaymentCreate(BaseModel):
    patient_rut: str
    amount: float
    method: str
    description: str

class VoucherCreate(BaseModel):
    patient_rut: str
    invoice_id: int
    amount: float
    payment_method: str

@router.get("/payments/{patient_rut}")
async def get_payments(patient_rut: str):
    """
    Obtiene información de pagos y facturas del paciente desde App2
    """
    try:
        logger.info(f"Solicitud de información de pagos para paciente: {patient_rut}")
        payment_info = await app2_client.get_payment_info(patient_rut)
        
        if payment_info:
            return payment_info
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró información de pagos para el paciente {patient_rut}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en get_payments: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo información de pagos: {str(e)}"
        )

@router.get("/patient/{patient_rut}")
async def get_patient(patient_rut: str):
    """
    Obtiene datos personales del paciente desde App2
    """
    try:
        logger.info(f"Solicitud de datos del paciente: {patient_rut}")
        patient_data = await app2_client.get_patient_data(patient_rut)
        
        if patient_data:
            return patient_data
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró el paciente {patient_rut}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en get_patient: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo datos del paciente: {str(e)}"
        )

@router.post("/patients")
async def create_patient(patient: PatientCreate):
    """
    Crea un nuevo paciente en App2
    """
    try:
        logger.info(f"Creando paciente: {patient.rut}")
        result = await app2_client.create_patient(patient.dict())
        return result
    except Exception as e:
        logger.error(f"Error en create_patient: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creando paciente: {str(e)}"
        )

@router.put("/patient/{patient_rut}")
async def update_patient(patient_rut: str, patient: PatientUpdate):
    """
    Actualiza datos de un paciente en App2
    """
    try:
        logger.info(f"Actualizando paciente: {patient_rut}")
        result = await app2_client.update_patient(patient_rut, patient.dict(exclude_unset=True))
        return result
    except Exception as e:
        logger.error(f"Error en update_patient: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando paciente: {str(e)}"
        )

@router.post("/payments")
async def create_payment(payment: PaymentCreate):
    """
    Registra un nuevo pago en App2
    """
    try:
        logger.info(f"Registrando pago para paciente: {payment.patient_rut}")
        result = await app2_client.create_payment(payment.dict())
        return result
    except Exception as e:
        logger.error(f"Error en create_payment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error registrando pago: {str(e)}"
        )

@router.post("/vouchers")
async def generate_voucher(voucher: VoucherCreate):
    """
    Genera un comprobante de pago en App2
    """
    try:
        logger.info(f"Generando comprobante para paciente: {voucher.patient_rut}")
        result = await app2_client.generate_voucher(voucher.dict())
        return result
    except Exception as e:
        logger.error(f"Error en generate_voucher: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generando comprobante: {str(e)}"
        )
