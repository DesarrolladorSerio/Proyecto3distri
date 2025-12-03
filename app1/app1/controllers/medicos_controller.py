from flask import Blueprint, request
from services.medicos_service import *

medicos_bp = Blueprint("medicos", __name__)

@medicos_bp.get("/")
def listar_medicos():
    return listar_medicos_service()

@medicos_bp.post("/disponibilidad")
def actualizar_disponibilidad():
    data = request.json
    return actualizar_disponibilidad_service(data)
