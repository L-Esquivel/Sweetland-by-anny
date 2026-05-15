from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from db import get_db # 🟢 Importamos el nuevo gestor de DB
import logging
from psycopg2.extras import DictCursor # 🟢 Para obtener resultados como diccionarios

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

recetas_bp = Blueprint("recetas", __name__, url_prefix="/recetas")

# ========================================
# LÓGICA EXACTA DE COSTEO (versión final corregida)
# ========================================
def calcular_costo_completo(id_producto, tenant_id, pax=None, utilidad_porcentaje=None):
    """
    Calcula el costeo completo de un producto.
    """
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # 💡 SAAS-IFICATION: Todas las consultas internas ahora usan tenant_id.
            # 1. TOTAL 1 = Costo de ingredientes (ahora desde recetas_ingredientes)
            cursor.execute("""
                SELECT COALESCE(SUM(costo_ingrediente), 0) as total1
                FROM recetas_ingredientes
                WHERE id_producto = %s AND tenant_id = %s
            """, (id_producto, tenant_id))
            resultado = cursor.fetchone()
            total1 = float(resultado.get('total1', 0) if resultado else 0)

            # 2. Gastos Operativos = TOTAL 1 × 35%
            gastos_operativos = total1 * 0.35

            # 3. Depreciación del Mercado = TOTAL 1 × 10%
            dep_mercado = total1 * 0.10

            # 4. TOTAL 2 = TOTAL 1 × 1.45
            total2 = total1 * 1.45

            # 5. Depreciación de Equipos = TOTAL 2 × 5%
            dep_equipos = total2 * 0.05

            # 6. Valor total de empaques
            cursor.execute("""
                SELECT COALESCE(SUM(subtotal), 0) as costo_empaques
                FROM recetas_empaques
                WHERE id_producto = %s AND tenant_id = %s
            """, (id_producto, tenant_id))
            resultado_empaques = cursor.fetchone()
            costo_empaques = float(resultado_empaques.get('costo_empaques', 0) if resultado_empaques else 0)

            # 7. TOTAL 3
            total3 = total2 + dep_equipos + costo_empaques

            # 8. Obtener PAX y % de utilidad
            if pax is None or utilidad_porcentaje is None:
                cursor.execute("""
                    SELECT pax, utilidad_porcentaje
                    FROM productos
                    WHERE id_producto = %s AND tenant_id = %s
                """, (id_producto, tenant_id))
                prod = cursor.fetchone()
                pax_db = int(prod.get('pax', 1)) if prod and prod.get('pax') is not None else 1
                utilidad_db = float(prod.get('utilidad_porcentaje', 40.0)) if prod and prod.get('utilidad_porcentaje') is not None else 40.0

                pax = pax if pax is not None else pax_db
                utilidad_porcentaje = utilidad_porcentaje if utilidad_porcentaje is not None else utilidad_db

            # 9. Utilidad
            utilidad = total3 * (utilidad_porcentaje / 100)

            # 10. TOTAL 4
            total4 = total3 + utilidad

            # 11. I.C. = TOTAL 4 × 8%
            ic = total4 * 0.08

            # 12. Valor Final = TOTAL 4 × 1.08
            valor_final = total4 * 1.08

            # 13. Precio Sugerido Final (por unidad)
            precio_sugerido = valor_final / pax if pax > 0 else 0

            # Actualizar tabla productos con los valores finales
            cursor.execute("""
                UPDATE productos
                SET costo_produccion = %s,
                    pax = %s,
                    utilidad_porcentaje = %s,
                    precio = %s
                WHERE id_producto = %s AND tenant_id = %s
            """, (total3, pax, utilidad_porcentaje, precio_sugerido, id_producto, tenant_id))

        conn.commit()

        return {
            "costo_base": round(total1, 2),
            "gastos_operativos": round(gastos_operativos, 2),
            "dep_mercado": round(dep_mercado, 2),
            "dep_equipos": round(dep_equipos, 2),
            "costo_empaques": round(costo_empaques, 2),
            "total3": round(total3, 2),
            "utilidad": round(utilidad, 2),
            "total4": round(total4, 2),
            "ic": round(ic, 2),
            "valor_final": round(valor_final, 2),
            "precio_sugerido": round(precio_sugerido, 2),
            "pax": pax,
            "utilidad_porcentaje": utilidad_porcentaje
        }

    except Exception as e:
        logger.error(f"Error en calcular_costo_completo: {str(e)}")
        if 'conn' in locals() and conn: conn.rollback()
        raise

# ================================
# RECALCULAR CON PAX Y UTILIDAD
# ================================
@recetas_bp.route("/recalcular", methods=["POST"])
@login_required
def recalcular_costos():
    tenant_id = current_user.tenant_id
    data = request.get_json()
    id_producto = data.get("id_producto")
    pax = data.get("pax")
    utilidad_porcentaje = data.get("utilidad_porcentaje")

    if not id_producto:
        return jsonify({"error": "id_producto es requerido"}), 400

    try:
        costos = calcular_costo_completo(
            id_producto,
            tenant_id,
            pax=int(pax) if pax is not None else None,
            utilidad_porcentaje=float(utilidad_porcentaje) if utilidad_porcentaje is not None else None
        )
        return jsonify({
            "mensaje": "Costos recalculados correctamente",
            "costos": costos
        })
    except Exception as e:
        logger.error(f"Error en recalcular_costos: {str(e)}")
        return jsonify({"error": "Error al recalcular los costos"}), 500

# ================================
# Obtener todas las recetas
# ================================
@recetas_bp.route("/", methods=["GET"])
@login_required
def get_recetas():
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT ri.id, ri.id_producto, ri.id_ingrediente, ri.cantidad_necesaria,
                       p.nombre AS producto, i.nombre AS ingrediente
                FROM recetas_ingredientes ri
                LEFT JOIN productos p ON ri.id_producto = p.id_producto AND p.tenant_id = %s
                LEFT JOIN ingredientes i ON ri.id_ingrediente = i.id_ingrediente AND i.tenant_id = %s
                WHERE ri.tenant_id = %s
            """, (tenant_id, tenant_id, tenant_id))
            filas_raw = cursor.fetchall()
            # FIX: Convertir a dict para asegurar la serialización JSON.
            filas = [dict(row) for row in filas_raw]
            return jsonify(filas)
    except Exception as e:
        logger.error(f"Error en get_recetas: {str(e)}")
        return jsonify({"error": "Error al obtener las recetas"}), 500

# ================================
# Obtener recetas + empaques + costos de un producto
# ================================
@recetas_bp.route("/producto/<int:producto_id>", methods=["GET"])
@login_required
def get_recetas_por_producto(producto_id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # Ingredientes
            cursor.execute("""
                SELECT ri.id, ri.id_ingrediente, ri.cantidad_necesaria,
                       i.nombre AS ingrediente, i.unidad_medida as unidad, i.costo_por_unidad,
                       ri.costo_ingrediente
                FROM recetas_ingredientes ri
                LEFT JOIN ingredientes i ON ri.id_ingrediente = i.id_ingrediente AND i.tenant_id = %s
                WHERE ri.id_producto = %s AND ri.tenant_id = %s
            """, (tenant_id, producto_id, tenant_id))
            recetas_raw = cursor.fetchall()
            # FIX: Convertir a dict para asegurar la serialización JSON.
            recetas = [dict(row) for row in recetas_raw]

            # Empaques
            cursor.execute("""
                SELECT re.id, re.id_empaque, re.cantidad, re.subtotal,
                       e.nombre, e.precio
                FROM recetas_empaques re
                LEFT JOIN empaques e ON re.id_empaque = e.id_empaque AND e.tenant_id = %s
                WHERE re.id_producto = %s AND re.tenant_id = %s
            """, (tenant_id, producto_id, tenant_id))
            empaques_raw = cursor.fetchall()
            # FIX: Convertir a dict para asegurar la serialización JSON.
            empaques = [dict(row) for row in empaques_raw]

            # Costos
            costos = calcular_costo_completo(producto_id, tenant_id)

            return jsonify({
                "recetas": recetas,
                "empaques": empaques,
                "costos": costos
            })
    except Exception as e:
        logger.error(f"Error en get_recetas_por_producto: {str(e)}")
        return jsonify({"error": "Error al obtener los datos de la receta"}), 500

# ================================
# CRUD Recetas
# ================================
@recetas_bp.route("/", methods=["POST"])
@login_required
def add_receta():
    tenant_id = current_user.tenant_id
    data = request.get_json()
    id_producto = data.get("id_producto")
    id_ingrediente = data.get("id_ingrediente")
    cantidad_necesaria = data.get("cantidad_necesaria")

    if not id_producto or not id_ingrediente or cantidad_necesaria is None:
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # Obtener costo del ingrediente
            cursor.execute("SELECT costo_por_unidad FROM ingredientes WHERE id_ingrediente = %s AND tenant_id = %s", (id_ingrediente, tenant_id))
            ingrediente = cursor.fetchone()
            if not ingrediente:
                return jsonify({"error": "Ingrediente no encontrado"}), 404
            
            costo_unitario = float(ingrediente['costo_por_unidad'])
            costo_ingrediente = costo_unitario * float(cantidad_necesaria)

            cursor.execute("""
                INSERT INTO recetas_ingredientes (id_producto, id_ingrediente, cantidad_necesaria, costo_ingrediente, tenant_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_producto, id_ingrediente, cantidad_necesaria, costo_ingrediente, tenant_id))
            conn.commit()
            
            calcular_costo_completo(id_producto, tenant_id)
            return jsonify({"mensaje": "Receta agregada correctamente"}), 201
    except Exception as e:
        if conn: conn.rollback()
        logger.error(f"Error en add_receta: {e}", exc_info=True)
        return jsonify({"error": "Error al agregar el ingrediente a la receta"}), 500

@recetas_bp.route("/multiple", methods=["POST"])
@login_required
def add_recetas_multiple():
    tenant_id = current_user.tenant_id
    data = request.get_json()
    id_producto = data.get("id_producto")
    ingredientes = data.get("ingredientes", [])

    if not id_producto or not ingredientes:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            for ing in ingredientes:
                id_ingrediente = ing.get("id_ingrediente")
                cantidad_necesaria = ing.get("cantidad_necesaria")

                cursor.execute("SELECT costo_por_unidad FROM ingredientes WHERE id_ingrediente = %s AND tenant_id = %s", (id_ingrediente, tenant_id))
                ing_data = cursor.fetchone()
                if not ing_data: continue # Opcional: manejar error si un ingrediente no existe

                costo_unitario = float(ing_data['costo_por_unidad'])
                costo_ingrediente = costo_unitario * float(cantidad_necesaria)

                cursor.execute("""
                    INSERT INTO recetas_ingredientes (id_producto, id_ingrediente, cantidad_necesaria, costo_ingrediente, tenant_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_producto, id_ingrediente, cantidad_necesaria, costo_ingrediente, tenant_id))
            conn.commit()
            calcular_costo_completo(id_producto, tenant_id)
            return jsonify({"mensaje": "Ingredientes agregados correctamente"}), 201
    except Exception as e:
        if conn: conn.rollback()
        logger.error(f"Error en add_recetas_multiple: {e}", exc_info=True)
        return jsonify({"error": "Error al agregar los ingredientes"}), 500

@recetas_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_receta(id):
    tenant_id = current_user.tenant_id
    data = request.get_json()
    id_producto = data.get("id_producto")
    id_ingrediente = data.get("id_ingrediente")
    cantidad_necesaria = data.get("cantidad_necesaria")

    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT costo_por_unidad FROM ingredientes WHERE id_ingrediente = %s AND tenant_id = %s", (id_ingrediente, tenant_id))
            ing_data = cursor.fetchone()
            if not ing_data: return jsonify({"error": "Ingrediente no encontrado"}), 404

            costo_unitario = float(ing_data['costo_por_unidad'])
            costo_ingrediente = costo_unitario * float(cantidad_necesaria)

            cursor.execute("""
                UPDATE recetas_ingredientes
                SET id_producto = %s, id_ingrediente = %s, cantidad_necesaria = %s, costo_ingrediente = %s
                WHERE id = %s AND tenant_id = %s
            """, (id_producto, id_ingrediente, cantidad_necesaria, costo_ingrediente, id, tenant_id))
            conn.commit()
            if id_producto:
                calcular_costo_completo(id_producto, tenant_id)
            return jsonify({"mensaje": "Receta actualizada correctamente"})
    except Exception as e:
        if conn: conn.rollback()
        logger.error(f"Error en update_receta: {e}", exc_info=True)
        return jsonify({"error": "Error al actualizar la receta"}), 500

@recetas_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_receta(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT id_producto FROM recetas_ingredientes WHERE id = %s AND tenant_id = %s", (id, tenant_id))
            resultado = cursor.fetchone()
            id_producto = resultado.get('id_producto') if resultado else None

            cursor.execute("DELETE FROM recetas_ingredientes WHERE id = %s AND tenant_id = %s", (id, tenant_id))
            conn.commit()

            if id_producto:
                calcular_costo_completo(id_producto, tenant_id)

            return jsonify({"mensaje": "Receta eliminada correctamente"})
    except Exception as e:
        if conn: conn.rollback()
        logger.error(f"Error en delete_receta: {e}", exc_info=True)
        return jsonify({"error": "Error al eliminar la receta"}), 500

@recetas_bp.route("/producto/<int:producto_id>", methods=["DELETE"])
@login_required
def delete_recetas_producto(producto_id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM recetas_ingredientes WHERE id_producto = %s AND tenant_id = %s", (producto_id, tenant_id))
            conn.commit()
            calcular_costo_completo(producto_id, tenant_id)
            return jsonify({"mensaje": "Todas las recetas del producto fueron eliminadas"})
    except Exception as e:
        if conn: conn.rollback()
        logger.error(f"Error en delete_recetas_producto: {e}", exc_info=True)
        return jsonify({"error": "Error al eliminar las recetas del producto"}), 500