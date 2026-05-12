from flask import Blueprint, jsonify, request
from flask_login import login_required
from utils import admin_required, registrar_log
from extensions import mysql
import datetime

gastos_bp = Blueprint("gastos_bp", __name__, url_prefix="/gastos")

@gastos_bp.route("/", methods=["GET"])
@login_required
@admin_required
def get_gastos():
    cursor = mysql.connection.cursor()
    try:
        # Permite filtrar por mes y año, ej: /gastos?mes=10&ano=2023
        mes = request.args.get('mes', type=int)
        ano = request.args.get('ano', type=int)

        query = "SELECT * FROM gastos"
        params = []
        if mes and ano:
            query += " WHERE MONTH(fecha) = %s AND YEAR(fecha) = %s"
            params.extend([mes, ano])
        
        query += " ORDER BY fecha DESC"
        
        cursor.execute(query, tuple(params))
        gastos = cursor.fetchall()
        # Convierte objetos de fecha a string para la serialización JSON
        for gasto in gastos:
            if isinstance(gasto.get('fecha'), datetime.date):
                gasto['fecha'] = gasto['fecha'].isoformat()
        return jsonify(gastos)
    finally:
        if cursor: cursor.close()

@gastos_bp.route("/", methods=["POST"])
@login_required
@admin_required
def add_gasto():
    data = request.get_json()
    descripcion = data.get("descripcion")
    monto = data.get("monto")
    fecha = data.get("fecha")
    categoria = data.get("categoria", "Varios")

    if not descripcion or not monto or not fecha:
        return jsonify({"error": "Descripción, monto y fecha son obligatorios"}), 400

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO gastos (descripcion, monto, categoria, fecha)
            VALUES (%s, %s, %s, %s)
        """, (descripcion, monto, categoria, fecha))
        mysql.connection.commit()
        registrar_log(f"Registró nuevo gasto: {descripcion} por ${monto}")
        return jsonify({"mensaje": "Gasto registrado con éxito"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()

@gastos_bp.route("/<int:id>", methods=["PUT"])
@login_required
@admin_required
def update_gasto(id):
    data = request.get_json()
    # ... (código para actualizar, similar a add_gasto)
    return jsonify({"mensaje": "Gasto actualizado con éxito"})

@gastos_bp.route("/<int:id>", methods=["DELETE"])
@login_required
@admin_required
def delete_gasto(id):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM gastos WHERE id_gasto=%s", (id,))
        mysql.connection.commit()
        registrar_log(f"Eliminó gasto ID {id}")
        return jsonify({"mensaje": "Gasto eliminado con éxito"})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()