from flask import Blueprint, jsonify, request
from flask_login import login_required
from extensions import mysql
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ingredientes_bp = Blueprint("ingredientes", __name__, url_prefix="/ingredientes")

# ==================== PREFLIGHT ====================
@ingredientes_bp.route("/", methods=["OPTIONS"])
@ingredientes_bp.route("/<int:id>", methods=["OPTIONS"])
def handle_options(id=None):
    return jsonify({"status": "ok"}), 200

# ==================== OBTENER TODOS ====================
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

        # Usamos .get() por seguridad con DictCursor
        return jsonify([{
            "id_ingrediente": f.get("id_ingrediente"),
            "nombre":         f.get("nombre"),
            "unidad":         f.get("unidad"),
            "cantidad":       float(f.get("cantidad") or 0),
            "costo_unitario": float(f.get("costo_unitario") or 0)
        } for f in filas])
    except Exception as e:
        logger.error(f"Error en get_ingredientes: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== OBTENER UNO ====================
@ingredientes_bp.route("/<int:id>", methods=["GET"])
@login_required
def get_ingrediente(id):
    try:
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
            "id_ingrediente": f.get("id_ingrediente"),
            "nombre":         f.get("nombre"),
            "unidad":         f.get("unidad"),
            "cantidad":       float(f.get("cantidad") or 0),
            "costo_unitario": float(f.get("costo_unitario") or 0)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== CREAR INGREDIENTE ====================
@ingredientes_bp.route("/", methods=["POST"])
@login_required
def create_ingrediente():
    try:
        data = request.get_json() or {}
        nombre = data.get("nombre")
        unidad = data.get("unidad")
        
        # Validaciones básicas
        if not nombre or not unidad:
            return jsonify({"error": "Nombre y Unidad son obligatorios"}), 400

        # Limpieza de datos numéricos
        try:
            cantidad = float(data.get("cantidad") or 0)
            costo_unitario = float(data.get("costo_unitario") or 0)
        except (ValueError, TypeError):
            return jsonify({"error": "Cantidad y Costo deben ser números válidos"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO ingredientes (nombre, unidad, cantidad, costo_unitario)
            VALUES (%s, %s, %s, %s)
        """, (nombre, unidad, cantidad, costo_unitario))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"mensaje": "Ingrediente creado correctamente"}), 201

    except Exception as e:
        logger.error(f"Error al crear ingrediente: {str(e)}")
        return jsonify({"error": "Error interno al guardar"}), 500

# ==================== ACTUALIZAR INGREDIENTE ====================
@ingredientes_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_ingrediente(id):
    try:
        data = request.get_json() or {}
        nombre = data.get("nombre")
        unidad = data.get("unidad")
        
        if not nombre or not unidad:
            return jsonify({"error": "Nombre y Unidad son obligatorios"}), 400

        try:
            cantidad = float(data.get("cantidad") or 0)
            costo_unitario = float(data.get("costo_unitario") or 0)
        except (ValueError, TypeError):
            return jsonify({"error": "Valores numéricos inválidos"}), 400

        cursor = mysql.connection.cursor()
        
        # 1. Actualizar el ingrediente
        cursor.execute("""
            UPDATE ingredientes
            SET nombre=%s, unidad=%s, cantidad=%s, costo_unitario=%s
            WHERE id_ingrediente=%s
        """, (nombre, unidad, cantidad, costo_unitario, id))
        
        mysql.connection.commit()
        cursor.close()

        # NOTA: En un mundo ideal, aquí llamaríamos a una función 
        # para recalcular todos los productos que usan este ingrediente.
        # Por ahora, el usuario verá el cambio reflejado la próxima vez que abra la receta.

        return jsonify({"mensaje": "Ingrediente actualizado correctamente"})
    except Exception as e:
        logger.error(f"Error al actualizar ingrediente: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== ELIMINAR INGREDIENTE ====================
@ingredientes_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_ingrediente(id):
    try:
        cursor = mysql.connection.cursor()
        # Verificamos si se está usando en alguna receta antes de borrar (opcional pero recomendado)
        cursor.execute("SELECT COUNT(*) as total FROM recetas WHERE id_ingrediente = %s", (id,))
        uso = cursor.fetchone()
        
        if uso and uso.get('total', 0) > 0:
            cursor.close()
            return jsonify({"error": "No se puede eliminar: el ingrediente está siendo usado en una receta"}), 400

        cursor.execute("DELETE FROM ingredientes WHERE id_ingrediente = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"mensaje": "Ingrediente eliminado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500