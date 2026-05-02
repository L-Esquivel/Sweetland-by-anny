from flask import Blueprint, jsonify, request
from flask_login import login_required
from extensions import mysql

ingredientes_bp = Blueprint("ingredientes", __name__, url_prefix="/ingredientes")

# Obtener todos los ingredientes
@ingredientes_bp.route("/", methods=["GET"])
@login_required
def get_ingredientes():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id_ingrediente, nombre, unidad, cantidad, costo_unitario
        FROM ingredientes
    """)
    filas = cursor.fetchall()
    cursor.close()

    ingredientes = []
    for f in filas:
        ingredientes.append({
            "id_ingrediente": f[0],
            "nombre": f[1],
            "unidad": f[2],
            "cantidad": float(f[3]) if f[3] is not None else None,
            "costo_unitario": float(f[4]) if f[4] is not None else None
        })
    return jsonify(ingredientes)


# Obtener ingrediente por ID
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
        "id_ingrediente": f[0],
        "nombre": f[1],
        "unidad": f[2],
        "cantidad": float(f[3]) if f[3] is not None else None,
        "costo_unitario": float(f[4]) if f[4] is not None else None
    })


# Crear ingrediente
@ingredientes_bp.route("/", methods=["POST"])
@login_required
def create_ingrediente():
    data = request.get_json() or {}
    nombre = data.get("nombre")
    unidad = data.get("unidad")
    cantidad = data.get("cantidad")
    costo_unitario = data.get("costo_unitario")

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO ingredientes (nombre, unidad, cantidad, costo_unitario)
        VALUES (%s, %s, %s, %s)
    """, (nombre, unidad, cantidad, costo_unitario))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"mensaje": "Ingrediente creado correctamente"}), 201


# Actualizar ingrediente
@ingredientes_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_ingrediente(id):
    data = request.get_json() or {}
    nombre = data.get("nombre")
    unidad = data.get("unidad")
    cantidad = data.get("cantidad")
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


# Eliminar ingrediente
@ingredientes_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_ingrediente(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM ingredientes WHERE id_ingrediente = %s", (id,))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"mensaje": "Ingrediente eliminado correctamente"})
