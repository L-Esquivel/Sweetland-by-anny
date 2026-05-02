from flask import Blueprint, jsonify, request
from flask_login import login_required
from extensions import mysql
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

recetas_bp = Blueprint("recetas", __name__, url_prefix="/recetas")

# ================================
# Actualizar costo de producto (ingredientes + empaques)
# ================================
def actualizar_costo_producto(id_producto):
    try:
        cursor = mysql.connection.cursor()

        # Costo de ingredientes
        cursor.execute("""
            SELECT COALESCE(SUM(r.cantidad_necesaria * i.costo_unitario), 0)
            FROM recetas r
            LEFT JOIN ingredientes i ON r.id_ingrediente = i.id_ingrediente
            WHERE r.id_producto = %s
        """, (id_producto,))
        costo_ingredientes = float(cursor.fetchone()[0])

        # Costo de empaques
        cursor.execute("""
            SELECT COALESCE(SUM(subtotal), 0)
            FROM recetas_empaques
            WHERE id_producto = %s
        """, (id_producto,))
        costo_empaques = float(cursor.fetchone()[0])

        nuevo_costo = costo_ingredientes + costo_empaques

        cursor.execute("""
            UPDATE productos SET costo_produccion = %s WHERE id_producto = %s
        """, (nuevo_costo, id_producto))

        mysql.connection.commit()
        cursor.close()
        logger.info(f"Costo actualizado para producto {id_producto}: ${nuevo_costo} (ingredientes: ${costo_ingredientes} + empaques: ${costo_empaques})")

    except Exception as e:
        logger.error(f"Error actualizando costo producto {id_producto}: {str(e)}")
        mysql.connection.rollback()

# ================================
# PREFLIGHT
# ================================
@recetas_bp.route("/", methods=["OPTIONS"])
@recetas_bp.route("/<int:id>", methods=["OPTIONS"])
@recetas_bp.route("/producto/<int:producto_id>", methods=["OPTIONS"])
@recetas_bp.route("/multiple", methods=["OPTIONS"])
@recetas_bp.route("/costo-produccion/<int:producto_id>", methods=["OPTIONS"])
def handle_options(id=None, producto_id=None):
    return jsonify({"status": "ok"}), 200

# ================================
# Obtener todas las recetas
# ================================
@recetas_bp.route("/", methods=["GET"])
@login_required
def get_recetas():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT r.id_receta, r.id_producto, r.id_ingrediente, r.cantidad_necesaria,
               p.nombre AS producto, i.nombre AS ingrediente
        FROM recetas r
        LEFT JOIN productos p ON r.id_producto = p.id_producto
        LEFT JOIN ingredientes i ON r.id_ingrediente = i.id_ingrediente
    """)
    filas = cursor.fetchall()
    cursor.close()

    return jsonify([{
        "id_receta":         f[0],
        "id_producto":       f[1],
        "id_ingrediente":    f[2],
        "cantidad_necesaria": f[3],
        "producto":          f[4],
        "ingrediente":       f[5]
    } for f in filas])

# ================================
# Obtener recetas por producto (ingredientes + empaques + costos)
# ================================
@recetas_bp.route("/producto/<int:producto_id>", methods=["GET"])
@login_required
def get_recetas_por_producto(producto_id):
    cursor = mysql.connection.cursor()

    # Ingredientes
    cursor.execute("""
        SELECT r.id_receta, r.id_ingrediente, r.cantidad_necesaria,
               i.nombre AS ingrediente, i.unidad, i.costo_unitario,
               (r.cantidad_necesaria * i.costo_unitario) as costo_ingrediente
        FROM recetas r
        LEFT JOIN ingredientes i ON r.id_ingrediente = i.id_ingrediente
        WHERE r.id_producto = %s
    """, (producto_id,))
    filas_ing = cursor.fetchall()

    recetas = []
    costo_ingredientes = 0
    for f in filas_ing:
        costo = float(f[6]) if f[6] else 0
        costo_ingredientes += costo
        recetas.append({
            "id_receta":         f[0],
            "id_ingrediente":    f[1],
            "cantidad_necesaria": float(f[2]) if f[2] else 0,
            "ingrediente":       f[3],
            "unidad":            f[4],
            "costo_unitario":    float(f[5]) if f[5] else 0,
            "costo_ingrediente": costo
        })

    # Empaques
    cursor.execute("""
        SELECT re.id, re.id_empaque, re.cantidad, re.subtotal, e.nombre, e.precio
        FROM recetas_empaques re
        LEFT JOIN empaques e ON re.id_empaque = e.id_empaque
        WHERE re.id_producto = %s
    """, (producto_id,))
    filas_emp = cursor.fetchall()

    empaques = []
    costo_empaques = 0
    for f in filas_emp:
        subtotal = float(f[3]) if f[3] else float(f[5] or 0) * int(f[2] or 1)
        costo_empaques += subtotal
        empaques.append({
            "id":         f[0],
            "id_empaque": f[1],
            "cantidad":   f[2],
            "subtotal":   subtotal,
            "nombre":     f[4],
            "precio":     float(f[5]) if f[5] else 0
        })

    cursor.close()

    costo_total = costo_ingredientes + costo_empaques

    return jsonify({
        "recetas":              recetas,
        "empaques":             empaques,
        "costo_ingredientes":   costo_ingredientes,
        "costo_empaques":       costo_empaques,
        "costo_total_produccion": costo_total
    })

# ================================
# Crear receta (un ingrediente)
# ================================
@recetas_bp.route("/", methods=["POST"])
@login_required
def add_receta():
    data = request.get_json()
    id_producto       = data.get("id_producto")
    id_ingrediente    = data.get("id_ingrediente")
    cantidad_necesaria = data.get("cantidad_necesaria")

    if not id_producto or not id_ingrediente or cantidad_necesaria is None:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_producto FROM productos WHERE id_producto=%s", (id_producto,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "El producto no existe"}), 404

    cursor.execute("SELECT id_ingrediente FROM ingredientes WHERE id_ingrediente=%s", (id_ingrediente,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "El ingrediente no existe"}), 404

    cursor.execute("""
        INSERT INTO recetas (id_producto, id_ingrediente, cantidad_necesaria)
        VALUES (%s, %s, %s)
    """, (id_producto, id_ingrediente, cantidad_necesaria))
    mysql.connection.commit()
    cursor.close()

    actualizar_costo_producto(id_producto)
    return jsonify({"mensaje": "Receta agregada correctamente"})

# ================================
# Crear múltiples recetas
# ================================
@recetas_bp.route("/multiple", methods=["POST"])
@login_required
def add_recetas_multiple():
    data = request.get_json()
    id_producto  = data.get("id_producto")
    ingredientes = data.get("ingredientes", [])

    if not id_producto or not ingredientes:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id_producto FROM productos WHERE id_producto=%s", (id_producto,))
        if not cursor.fetchone():
            return jsonify({"error": "El producto no existe"}), 404

        for ing in ingredientes:
            cursor.execute("""
                INSERT INTO recetas (id_producto, id_ingrediente, cantidad_necesaria)
                VALUES (%s, %s, %s)
            """, (id_producto, ing.get("id_ingrediente"), ing.get("cantidad_necesaria")))

        mysql.connection.commit()
        cursor.close()
        actualizar_costo_producto(id_producto)
        return jsonify({"mensaje": f"{len(ingredientes)} ingredientes agregados"})

    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500

# ================================
# Actualizar receta
# ================================
@recetas_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_receta(id):
    data = request.get_json()
    id_producto        = data.get("id_producto")
    id_ingrediente     = data.get("id_ingrediente")
    cantidad_necesaria = data.get("cantidad_necesaria")

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE recetas
        SET id_producto=%s, id_ingrediente=%s, cantidad_necesaria=%s
        WHERE id_receta=%s
    """, (id_producto, id_ingrediente, cantidad_necesaria, id))
    mysql.connection.commit()
    cursor.close()

    actualizar_costo_producto(id_producto)
    return jsonify({"mensaje": "Receta actualizada correctamente"})

# ================================
# Eliminar receta
# ================================
@recetas_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_receta(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_producto FROM recetas WHERE id_receta=%s", (id,))
    resultado = cursor.fetchone()
    id_producto = resultado[0] if resultado else None

    cursor.execute("DELETE FROM recetas WHERE id_receta=%s", (id,))
    mysql.connection.commit()
    cursor.close()

    if id_producto:
        actualizar_costo_producto(id_producto)
    return jsonify({"mensaje": "Receta eliminada correctamente"})

# ================================
# Eliminar todas las recetas de un producto
# ================================
@recetas_bp.route("/producto/<int:producto_id>", methods=["DELETE"])
@login_required
def delete_recetas_producto(producto_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM recetas WHERE id_producto=%s", (producto_id,))
    mysql.connection.commit()
    cursor.close()

    actualizar_costo_producto(producto_id)
    return jsonify({"mensaje": "Recetas eliminadas correctamente"})

# ================================
# Costo de producción
# ================================
@recetas_bp.route("/costo-produccion/<int:producto_id>", methods=["GET"])
@login_required
def get_costo_produccion(producto_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT COALESCE(SUM(r.cantidad_necesaria * i.costo_unitario), 0)
        FROM recetas r
        LEFT JOIN ingredientes i ON r.id_ingrediente = i.id_ingrediente
        WHERE r.id_producto = %s
    """, (producto_id,))
    costo_ing = float(cursor.fetchone()[0])

    cursor.execute("""
        SELECT COALESCE(SUM(subtotal), 0) FROM recetas_empaques WHERE id_producto=%s
    """, (producto_id,))
    costo_emp = float(cursor.fetchone()[0])
    cursor.close()

    return jsonify({
        "costo_ingredientes": costo_ing,
        "costo_empaques":     costo_emp,
        "costo_produccion":   costo_ing + costo_emp
    })