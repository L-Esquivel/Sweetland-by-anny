from flask import Blueprint, jsonify, request
from flask_login import login_required
from extensions import mysql
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ==================== BLUEPRINT ====================
recetas_bp = Blueprint("recetas", __name__, url_prefix="/recetas")

# ========================================
# Cálculo completo según tu Excel (CORREGIDO)
# ========================================
def calcular_costo_completo(id_producto):
    cursor = mysql.connection.cursor()
    try:
        # Costo ingredientes
        cursor.execute("""
            SELECT COALESCE(SUM(r.cantidad_necesaria * i.costo_unitario), 0)
            FROM recetas r
            LEFT JOIN ingredientes i ON r.id_ingrediente = i.id_ingrediente
            WHERE r.id_producto = %s
        """, (id_producto,))
        costo_ing = float(cursor.fetchone()[0] or 0)

        # Costo empaques
        cursor.execute("""
            SELECT COALESCE(SUM(subtotal), 0)
            FROM recetas_empaques
            WHERE id_producto = %s
        """, (id_producto,))
        costo_emp = float(cursor.fetchone()[0] or 0)

        costo_base = costo_ing + costo_emp

        # Datos del producto
        cursor.execute("""
            SELECT pax, utilidad_porcentaje 
            FROM productos WHERE id_producto = %s
        """, (id_producto,))
        prod = cursor.fetchone()
        pax = int(prod[0]) if prod and prod[0] else 1
        utilidad = float(prod[1]) if prod and prod[1] else 40.0

        # === CÁLCULO COMPLETO SEGÚN TU EXCEL ===
        total2 = costo_base * 1.45                    # + 35% Gastos Operativos
        total3 = total2 * 1.05 + costo_emp            # + 5% Depreciación Equipos
        total4 = total3 * (1 + utilidad / 100)        # + 10% Depreciación Mercado + Utilidad
        precio_final = total4 * 1.08                  # + 8% I.C.
        precio_sugerido = precio_final / pax if pax > 0 else 0

        # Actualizar tabla productos
        cursor.execute("""
            UPDATE productos 
            SET costo_produccion = %s, 
                precio_sugerido = %s
            WHERE id_producto = %s
        """, (costo_base, precio_sugerido, id_producto))
        mysql.connection.commit()

        return {
            "costo_ingredientes": round(costo_ing, 2),
            "costo_empaques": round(costo_emp, 2),
            "costo_base": round(costo_base, 2),
            "total2": round(total2, 2),
            "total3": round(total3, 2),
            "total4": round(total4, 2),
            "precio_final": round(precio_final, 2),
            "precio_sugerido": round(precio_sugerido, 2),
            "pax": pax,
            "utilidad_porcentaje": utilidad
        }
    finally:
        cursor.close()

# ================================
# PREFLIGHT OPTIONS
# ================================
@recetas_bp.route("/", methods=["OPTIONS"])
@recetas_bp.route("/producto/<int:producto_id>", methods=["OPTIONS"])
@recetas_bp.route("/<int:id>", methods=["OPTIONS"])
@recetas_bp.route("/multiple", methods=["OPTIONS"])
def handle_options():
    return jsonify({"status": "ok"}), 200

# ================================
# Obtener todas las recetas (para el combo del frontend)
# ================================
@recetas_bp.route("/", methods=["GET"])
def get_recetas():
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            SELECT r.id_receta, r.id_producto, r.id_ingrediente, r.cantidad_necesaria,
                   p.nombre AS producto, i.nombre AS ingrediente
            FROM recetas r
            LEFT JOIN productos p ON r.id_producto = p.id_producto
            LEFT JOIN ingredientes i ON r.id_ingrediente = i.id_ingrediente
        """)
        filas = cursor.fetchall()
        columnas = ["id_receta", "id_producto", "id_ingrediente", "cantidad_necesaria", "producto", "ingrediente"]
        resultado = [dict(zip(columnas, fila)) for fila in filas]
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Error en get_recetas: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# ================================
# Obtener recetas + empaques de un producto
# ================================
@recetas_bp.route("/producto/<int:producto_id>", methods=["GET"])
def get_recetas_por_producto(producto_id):
    cursor = mysql.connection.cursor()
    try:
        # Ingredientes
        cursor.execute("""
            SELECT r.id_receta, r.id_ingrediente, r.cantidad_necesaria,
                   i.nombre AS ingrediente, i.unidad, i.costo_unitario,
                   (r.cantidad_necesaria * i.costo_unitario) as costo_ingrediente
            FROM recetas r
            LEFT JOIN ingredientes i ON r.id_ingrediente = i.id_ingrediente
            WHERE r.id_producto = %s
        """, (producto_id,))
        recetas = cursor.fetchall()

        # Empaques
        cursor.execute("""
            SELECT re.id, re.id_empaque, re.cantidad, re.subtotal,
                   e.nombre, e.precio
            FROM recetas_empaques re
            LEFT JOIN empaques e ON re.id_empaque = e.id_empaque
            WHERE re.id_producto = %s
        """, (producto_id,))
        empaques = cursor.fetchall()

        costos = calcular_costo_completo(producto_id)

        return jsonify({
            "recetas": recetas,
            "empaques": empaques,
            "costos": costos
        })
    except Exception as e:
        logger.error(f"Error en get_recetas_por_producto: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# ================================
# Crear receta (un ingrediente)
# ================================
@recetas_bp.route("/", methods=["POST"])
@login_required
def add_receta():
    data = request.get_json()
    id_producto = data.get("id_producto")
    id_ingrediente = data.get("id_ingrediente")
    cantidad_necesaria = data.get("cantidad_necesaria")

    if not id_producto or not id_ingrediente or cantidad_necesaria is None:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("INSERT INTO recetas (id_producto, id_ingrediente, cantidad_necesaria) VALUES (%s, %s, %s)",
                       (id_producto, id_ingrediente, cantidad_necesaria))
        mysql.connection.commit()
        calcular_costo_completo(id_producto)
        return jsonify({"mensaje": "Receta agregada correctamente"})
    finally:
        cursor.close()

# ================================
# Crear múltiples recetas
# ================================
@recetas_bp.route("/multiple", methods=["POST"])
@login_required
def add_recetas_multiple():
    data = request.get_json()
    id_producto = data.get("id_producto")
    ingredientes = data.get("ingredientes", [])

    if not id_producto or not ingredientes:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    cursor = mysql.connection.cursor()
    try:
        for ing in ingredientes:
            cursor.execute("""
                INSERT INTO recetas (id_producto, id_ingrediente, cantidad_necesaria)
                VALUES (%s, %s, %s)
            """, (id_producto, ing.get("id_ingrediente"), ing.get("cantidad_necesaria")))
        mysql.connection.commit()
        calcular_costo_completo(id_producto)
        return jsonify({"mensaje": f"{len(ingredientes)} ingredientes agregados"})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# ================================
# Actualizar receta
# ================================
@recetas_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_receta(id):
    data = request.get_json()
    id_producto = data.get("id_producto")
    id_ingrediente = data.get("id_ingrediente")
    cantidad_necesaria = data.get("cantidad_necesaria")

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            UPDATE recetas
            SET id_producto=%s, id_ingrediente=%s, cantidad_necesaria=%s
            WHERE id_receta=%s
        """, (id_producto, id_ingrediente, cantidad_necesaria, id))
        mysql.connection.commit()
        calcular_costo_completo(id_producto)
        return jsonify({"mensaje": "Receta actualizada correctamente"})
    finally:
        cursor.close()

# ================================
# Eliminar receta
# ================================
@recetas_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_receta(id):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id_producto FROM recetas WHERE id_receta=%s", (id,))
        resultado = cursor.fetchone()
        id_producto = resultado[0] if resultado else None

        cursor.execute("DELETE FROM recetas WHERE id_receta=%s", (id,))
        mysql.connection.commit()

        if id_producto:
            calcular_costo_completo(id_producto)
        return jsonify({"mensaje": "Receta eliminada correctamente"})
    finally:
        cursor.close()

# ================================
# Eliminar todas las recetas de un producto
# ================================
@recetas_bp.route("/producto/<int:producto_id>", methods=["DELETE"])
@login_required
def delete_recetas_producto(producto_id):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM recetas WHERE id_producto=%s", (producto_id,))
        mysql.connection.commit()
        calcular_costo_completo(producto_id)
        return jsonify({"mensaje": "Recetas eliminadas correctamente"})
    finally:
        cursor.close()