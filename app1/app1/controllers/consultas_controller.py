from flask import Blueprint, request
from services.consultas_service import *

consultas_bp = Blueprint("consultas", __name__)

@consultas_bp.get("/")
def listar_consultas():
    return listar_consultas_service()

@consultas_bp.post("/")
def registrar_consulta():
    data = request.json
    return registrar_consulta_service(data)

@consultas_bp.get("/paciente/<id_paciente>")
def historial_paciente(id_paciente):
    return historial_paciente_service(id_paciente)
