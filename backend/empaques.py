from flask import Blueprint, jsonify, request
from flask_login import login_required
from extensions import mysql
import logging
import MySQLdb.cursors   # ← Importante para usar diccionarios

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

empaques_bp = Blueprint("empaques", __name__, url_prefix="/empaques")

# ==================== PREFLIGHT ====================

@empaques_bp.route("/", methods=["OPTIONS"])
@empaques_bp.route("/<int:id>", methods=["OPTIONS"])
@empaques_bp.route("/producto/<int:producto_id>", methods=["OPTIONS"])
def handle_options(id=None, producto_id=None):
    return jsonify({"status": "ok"}), 200

# ==================== CATÁLOGO DE EMPAQUES ====================

@empaques_bp.route("/", methods=["GET"])
@login_required
def get_empaques():
    cursor = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id_empaque, nombre, descripcion, precio FROM empaques ORDER BY nombre")
    filas = cursor.fetchall()
    cursor.close()
    
    return jsonify([{
        "id_empaque":   row['id_empaque'],
        "nombre":       row['nombre'],
        "descripcion":  row['descripcion'],
        "precio":       float(row['precio']) if row['precio'] else 0
    } for row in filas])


@empaques_bp.route("/", methods=["POST"])
@login_required
def add_empaque():
    data = request.get_json()
    nombre      = data.get("nombre")
    descripcion = data.get("descripcion", "")
    precio      = data.get("precio", 0)

    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO empaques (nombre, descripcion, precio) VALUES (%s, %s, %s)",
        (nombre, descripcion, precio)
    )
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Empaque creado"}), 201


@empaques_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_empaque(id):
    data = request.get_json()
    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE empaques SET nombre=%s, descripcion=%s, precio=%s WHERE id_empaque=%s",
        (data.get("nombre"), data.get("descripcion"), data.get("precio"), id)
    )
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Empaque actualizado"})


@empaques_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_empaque(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM empaques WHERE id_empaque=%s", (id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Empaque eliminado"})

# ==================== EMPAQUES POR PRODUCTO ====================

@empaques_bp.route("/producto/<int:producto_id>", methods=["GET"])
@login_required
def get_empaques_producto(producto_id):
    cursor = mysql.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT re.id, re.id_empaque, re.cantidad, re.subtotal,
               e.nombre, e.precio
        FROM recetas_empaques re
        LEFT JOIN empaques e ON re.id_empaque = e.id_empaque
        WHERE re.id_producto = %s
    """, (producto_id,))
    filas = cursor.fetchall()
    cursor.close()

    items = []
    costo_total = 0
    for row in filas:
        subtotal = float(row['subtotal']) if row['subtotal'] else float(row['precio'] or 0) * int(row['cantidad'] or 1)
        costo_total += subtotal
        items.append({
            "id":           row['id'],
            "id_empaque":   row['id_empaque'],
            "cantidad":     row['cantidad'],
            "subtotal":     subtotal,
            "nombre":       row['nombre'],
            "precio":       float(row['precio']) if row['precio'] else 0
        })

    return jsonify({"empaques": items, "costo_total_empaque": costo_total})


@empaques_bp.route("/producto/<int:producto_id>", methods=["POST"])
@login_required
def add_empaque_producto(producto_id):
    data        = request.get_json()
    id_empaque  = data.get("id_empaque")
    cantidad    = data.get("cantidad", 1)

    if not id_empaque:
        return jsonify({"error": "id_empaque es obligatorio"}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT precio FROM empaques WHERE id_empaque=%s", (id_empaque,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        return jsonify({"error": "Empaque no encontrado"}), 404

    subtotal = float(row[0]) * int(cantidad)
    cursor.execute("""
        INSERT INTO recetas_empaques (id_producto, id_empaque, cantidad, subtotal)
        VALUES (%s, %s, %s, %s)
    """, (producto_id, id_empaque, cantidad, subtotal))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Empaque asignado al producto"}), 201


@empaques_bp.route("/producto/item/<int:id>", methods=["DELETE"])
@login_required
def delete_empaque_producto(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM recetas_empaques WHERE id=%s", (id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Empaque eliminado del producto"})