from fastapi import APIRouter, HTTPException
from clients.app1_client import App1Client
from typing import Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["medical"])

# Cliente de App1 (singleton)
app1_client = App1Client()

# Modelos de datos para POST
class ConsultaCreate(BaseModel):
    patient_id: str
    doctor_id: int
    specialty: str
    diagnosis: str
    treatment: str
    notes: Optional[str] = None

class DisponibilidadUpdate(BaseModel):
    doctor_id: int
    available_slots: list[str]

@router.get("/medical-history/{patient_rut}")
async def get_medical_history(patient_rut: str):
    """
    Obtiene el historial médico del paciente desde App1
    """
    try:
        logger.info(f"Solicitud de historial médico para paciente: {patient_rut}")
        history = await app1_client.get_historial_paciente(patient_rut)
        
        if history:
            return history
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró historial para el paciente {patient_rut}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en get_medical_history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo historial médico: {str(e)}"
        )

@router.get("/doctors")
async def get_doctors(specialty: Optional[str] = None):
    """
    Obtiene la lista de médicos disponibles desde App1
    Parámetros:
    - specialty: (opcional) Filtrar por especialidad
    """
    try:
        logger.info(f"Solicitud de médicos disponibles (especialidad: {specialty})")
        doctors = await app1_client.get_medicos_disponibles(specialty)
        return doctors
    except Exception as e:
        logger.error(f"Error en get_doctors: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo médicos: {str(e)}"
        )

@router.post("/consultations")
async def create_consultation(consulta: ConsultaCreate):
    """
    Crea una nueva consulta médica en App1
    """
    try:
        logger.info(f"Creando consulta para paciente: {consulta.patient_id}")
        result = await app1_client.create_consulta(consulta.dict())
        return result
    except Exception as e:
        logger.error(f"Error en create_consultation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creando consulta: {str(e)}"
        )

@router.post("/doctors/availability")
async def update_doctor_availability(disponibilidad: DisponibilidadUpdate):
    """
    Actualiza la disponibilidad de un médico en App1
    """
    try:
        logger.info(f"Actualizando disponibilidad del médico: {disponibilidad.doctor_id}")
        result = await app1_client.update_disponibilidad(disponibilidad.dict())
        return result
    except Exception as e:
        logger.error(f"Error en update_doctor_availability: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando disponibilidad: {str(e)}"
        )
