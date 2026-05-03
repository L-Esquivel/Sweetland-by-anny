from flask import Blueprint, jsonify, request
from flask_login import login_required
from extensions import mysql

ingredientes_bp = Blueprint("ingredientes", __name__, url_prefix="/ingredientes")

@ingredientes_bp.route("/", methods=["OPTIONS"])
@ingredientes_bp.route("/<int:id>", methods=["OPTIONS"])
def handle_options(id=None):
    return jsonify({"status": "ok"}), 200

@ingredientes_bp.route("/", methods=["GET"])
@login_required
def get_ingredientes():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT id_ingrediente, nombre, unidad, cantidad, costo_unitario
            FROM ingredientes
            ORDER BY nombre
        """)
        filas = cursor.fetchall()
        cursor.close()

        return jsonify([{
            "id_ingrediente": f["id_ingrediente"],
            "nombre":         f["nombre"],
            "unidad":         f["unidad"],
            "cantidad":       float(f["cantidad"]) if f["cantidad"] is not None else 0,
            "costo_unitario": float(f["costo_unitario"]) if f["costo_unitario"] is not None else 0
        } for f in filas])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ingredientes_bp.route("/<int:id>", methods=["GET"])
@login_required
def get_ingrediente(id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id_ingrediente, nombre, unidad, cantidad, costo_unitario
        FROM ingredientes WHERE id_ingrediente = %s
    """, (id,))
    f = cursor.fetchone()
    cursor.close()

    if not f:
        return jsonify({"error": "Ingrediente no encontrado"}), 404

    return jsonify({
        "id_ingrediente": f["id_ingrediente"],
        "nombre":         f["nombre"],
        "unidad":         f["unidad"],
        "cantidad":       float(f["cantidad"]) if f["cantidad"] is not None else 0,
        "costo_unitario": float(f["costo_unitario"]) if f["costo_unitario"] is not None else 0
    })

@ingredientes_bp.route("/", methods=["POST"])
@login_required
def create_ingrediente():
    data          = request.get_json() or {}
    nombre        = data.get("nombre")
    unidad        = data.get("unidad")
    cantidad      = data.get("cantidad")
    costo_unitario = data.get("costo_unitario")

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO ingredientes (nombre, unidad, cantidad, costo_unitario)
        VALUES (%s, %s, %s, %s)
    """, (nombre, unidad, cantidad, costo_unitario))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Ingrediente creado correctamente"}), 201

@ingredientes_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_ingrediente(id):
    data          = request.get_json() or {}
    nombre        = data.get("nombre")
    unidad        = data.get("unidad")
    cantidad      = data.get("cantidad")
    costo_unitario = data.get("costo_unitario")

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE ingredientes
        SET nombre=%s, unidad=%s, cantidad=%s, costo_unitario=%s
        WHERE id_ingrediente=%s
    """, (nombre, unidad, cantidad, costo_unitario, id))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Ingrediente actualizado correctamente"})

@ingredientes_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_ingrediente(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM ingredientes WHERE id_ingrediente = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Ingrediente eliminado correctamente"})