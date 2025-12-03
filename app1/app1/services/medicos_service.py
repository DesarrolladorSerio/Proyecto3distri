from db import get_connection

def listar_medicos_service():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM medicos")
    rows = cur.fetchall()
    conn.close()
    return {"medicos": rows}, 200

def actualizar_disponibilidad_service(data):
    conn = get_connection()
    cur = conn.cursor()

    sql = "UPDATE medicos SET disponible=%s WHERE id=%s"
    cur.execute(sql, (data["disponible"], data["id_medico"]))
    conn.commit()

    conn.close()

    if cur.rowcount == 0:
        return {"error": "Médico no encontrado"}, 404

    return {"msg": "Disponibilidad actualizada"}, 200
