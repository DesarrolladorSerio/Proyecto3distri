from db import get_connection

def listar_consultas_service():
    conn = get_connection()
    if conn is None:
        return {"error": "No se pudo conectar a la base de datos"}, 503
    
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM consultas")
        rows = cur.fetchall()
        return {"consultas": rows}, 200
    except Exception as e:
        return {"error": f"Error al consultar: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()

def registrar_consulta_service(data):
    conn = get_connection()
    if conn is None:
        return {"error": "No se pudo conectar a la base de datos"}, 503
    
    try:
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
        return {"msg": "Consulta registrada"}, 201
    except Exception as e:
        return {"error": f"Error al registrar: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()

def historial_paciente_service(identifier):
    conn = get_connection()
    if conn is None:
        return {"error": "No se pudo conectar a la base de datos"}, 503
    
    try:
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
        return {"consultas": rows}, 200
    except Exception as e:
        return {"error": f"Error al obtener historial: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()
