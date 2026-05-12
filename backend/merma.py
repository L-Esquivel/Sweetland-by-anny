from flask import Blueprint, jsonify, request
from flask_login import login_required
from utils import admin_required, registrar_log
from extensions import mysql
import datetime

merma_bp = Blueprint("merma_bp", __name__, url_prefix="/merma")

@merma_bp.route("/", methods=["GET"])
@login_required
@admin_required
def get_merma_registros():
    cursor = mysql.connection.cursor()
    try:
        mes = request.args.get('mes', type=int)
        ano = request.args.get('ano', type=int)

        query = "SELECT * FROM merma ORDER BY fecha DESC"
        if mes and ano:
            query = "SELECT * FROM merma WHERE MONTH(fecha) = %s AND YEAR(fecha) = %s ORDER BY fecha DESC"
        
        cursor.execute(query, (mes, ano) if mes and ano else ())
        registros = cursor.fetchall()
        for registro in registros:
            if isinstance(registro.get('fecha'), datetime.date):
                registro['fecha'] = registro['fecha'].isoformat()
        return jsonify(registros)
    finally:
        if cursor: cursor.close()

@merma_bp.route("/", methods=["POST"])
@login_required
@admin_required
def add_merma_registro():
    data = request.get_json()
    id_producto = data.get("id_producto")
    id_ingrediente = data.get("id_ingrediente")
    cantidad = data.get("cantidad")
    fecha = data.get("fecha")
    motivo = data.get("motivo")

    if not (id_producto or id_ingrediente) or not cantidad or not fecha:
        return jsonify({"error": "Se requiere un producto/ingrediente, cantidad y fecha."}), 400

    cursor = mysql.connection.cursor()
    try:
        costo_unitario = 0
        descripcion = ""
        if id_producto:
            cursor.execute("SELECT nombre, costo_produccion FROM productos WHERE id_producto = %s", (id_producto,))
            item = cursor.fetchone()
            if not item: return jsonify({"error": "Producto no encontrado"}), 404
            costo_unitario = item.get('costo_produccion', 0)
            descripcion = f"Producto: {item.get('nombre')}"
        elif id_ingrediente:
            cursor.execute("SELECT nombre, costo_unitario FROM ingredientes WHERE id_ingrediente = %s", (id_ingrediente,))
            item = cursor.fetchone()
            if not item: return jsonify({"error": "Ingrediente no encontrado"}), 404
            costo_unitario = item.get('costo_unitario', 0)
            descripcion = f"Ingrediente: {item.get('nombre')}"

        costo_perdida = float(costo_unitario) * float(cantidad)

        cursor.execute("""
            INSERT INTO merma (id_producto, id_ingrediente, descripcion, cantidad, costo_perdida, fecha, motivo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id_producto, id_ingrediente, descripcion, cantidad, costo_perdida, fecha, motivo))
        mysql.connection.commit()
        
        registrar_log(f"Registró merma de '{descripcion}' por un costo de ${costo_perdida}")
        return jsonify({"mensaje": "Registro de merma añadido con éxito"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()

@merma_bp.route("/<int:id>", methods=["DELETE"])
@login_required
@admin_required
def delete_merma_registro(id):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM merma WHERE id_merma=%s", (id,))
        mysql.connection.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Registro de merma no encontrado"}), 404
        registrar_log(f"Eliminó registro de merma ID {id}")
        return jsonify({"mensaje": "Registro de merma eliminado"})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()