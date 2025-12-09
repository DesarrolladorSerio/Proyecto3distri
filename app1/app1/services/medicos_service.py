from db import get_connection

def listar_medicos_service():
    conn = get_connection()
    if conn is None:
        return {"error": "No se pudo conectar a la base de datos"}, 503
    
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM medicos")
        rows = cur.fetchall()
        return {"medicos": rows}, 200
    except Exception as e:
        return {"error": f"Error al consultar: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()

def actualizar_disponibilidad_service(data):
    conn = get_connection()
    if conn is None:
        return {"error": "No se pudo conectar a la base de datos"}, 503
    
    try:
        cur = conn.cursor()
        sql = "UPDATE medicos SET disponible=%s WHERE id=%s"
        cur.execute(sql, (data["disponible"], data["id_medico"]))
        conn.commit()
        
        if cur.rowcount == 0:
            return {"error": "Médico no encontrado"}, 404
        
        return {"msg": "Disponibilidad actualizada"}, 200
    except Exception as e:
        return {"error": f"Error al actualizar: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()
