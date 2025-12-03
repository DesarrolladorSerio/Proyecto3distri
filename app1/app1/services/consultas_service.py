from db import get_connection

def listar_consultas_service():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM consultas")
    rows = cur.fetchall()
    conn.close()
    return {"consultas": rows}, 200

def registrar_consulta_service(data):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO consultas (id_paciente, id_medico, fecha, motivo, diagnostico, tratamiento)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cur.execute(sql, (
        data["id_paciente"],
        data["id_medico"],
        data["fecha"],
        data.get("motivo"),
        data.get("diagnostico"),
        data.get("tratamiento")
    ))
    conn.commit()

    conn.close()
    return {"msg": "Consulta registrada"}, 201

def historial_paciente_service(identifier):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Query joining with pacientes (to filter by RUT) and medicos (to get details)
    sql = """
        SELECT c.*, m.nombre as nombre_medico, m.especialidad 
        FROM consultas c
        JOIN pacientes p ON c.id_paciente = p.id
        LEFT JOIN medicos m ON c.id_medico = m.id
        WHERE p.rut = %s OR p.id = %s
    """
    # Try to use identifier as both RUT and ID (if it's a number)
    # This covers both cases: passed as RUT string or ID integer
    param = identifier
    
    cur.execute(sql, (param, param))
    rows = cur.fetchall()

    conn.close()
    return {"consultas": rows}, 200
