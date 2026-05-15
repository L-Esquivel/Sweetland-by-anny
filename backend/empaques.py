from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from db import get_db # 🟢 Import the new DB manager
from psycopg2.extras import DictCursor # 🟢 To get results as dictionaries
import logging
from utils import admin_required # 💡 FIX: Import the admin decorator
from recetas import calcular_costo_completo # Import the costing function

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

empaques_bp = Blueprint("empaques", __name__, url_prefix="/empaques")

# ==================== GENERAL PACKAGING CATALOG ====================
# These will appear in the new "Supplies" section

@empaques_bp.route("/", methods=["GET"])
@login_required
def get_empaques():
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # 💡 SAAS-IFICATION: Filter by tenant_id.
            # FIX: Use COALESCE to avoid null prices (NaN on frontend) and convert to dict.
            cursor.execute("""
                SELECT id_empaque, nombre, descripcion, COALESCE(precio, 0) as precio 
                FROM empaques WHERE tenant_id = %s ORDER BY nombre
            """, (tenant_id,))
            empaques_raw = cursor.fetchall()
            empaques = [dict(row) for row in empaques_raw]
            return jsonify(empaques)
    except Exception as e:
        logger.error(f"Error en get_empaques: {str(e)}")
        return jsonify({"error": "Error fetching packaging catalog"}), 500

@empaques_bp.route("/", methods=["POST"])
@admin_required # 💡 FIX: Add decorator so only admins can create packaging.
def add_empaque():
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        nombre = data.get("nombre")
        descripcion = data.get("descripcion", "")
        precio = float(data.get("precio") or 0)

        if not nombre:
            return jsonify({"error": "Name is required"}), 400

        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO empaques (nombre, descripcion, precio, tenant_id) VALUES (%s, %s, %s, %s)",
                (nombre, descripcion, precio, tenant_id)
            )
            conn.commit()
        return jsonify({"message": "Packaging created in catalog"}), 201
    except Exception as e:
        conn.rollback() # 💡 FIX: Use the correct connection for rollback and simplify error handling.
        logger.error(f"Error en add_empaque: {e}", exc_info=True)
        return jsonify({"error": "Internal error creating packaging"}), 500

@empaques_bp.route("/<int:id>", methods=["PUT"])
@admin_required # FIX: Only admins can modify the catalog.
def update_empaque(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        data = request.get_json()
        nombre = data.get("nombre")
        descripcion = data.get("descripcion", "")
        precio = float(data.get("precio") or 0)

        if not nombre:
            return jsonify({"error": "Name is required"}), 400

        with conn.cursor() as cursor:
            # 💡 SAAS-IFICATION: Ensure only packaging from the correct tenant can be updated.
            cursor.execute(
                "UPDATE empaques SET nombre=%s, descripcion=%s, precio=%s WHERE id_empaque=%s AND tenant_id = %s",
                (nombre, descripcion, precio, id, tenant_id)
            )
            conn.commit()
        return jsonify({"message": "Packaging updated successfully"})
    except Exception as e:
        conn.rollback()
        logger.error(f"Error in update_empaque: {e}", exc_info=True)
        return jsonify({"error": "Error updating packaging"}), 500

@empaques_bp.route("/<int:id>", methods=["DELETE"])
@admin_required # FIX: Only admins can delete from the catalog.
def delete_empaque(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # VERIFICATION: Is this packaging in use by any product?
            # 💡 SAAS-IFICATION: The usage check must also be tenant-specific.
            cursor.execute("SELECT COUNT(*) as total FROM recetas_empaques WHERE id_empaque = %s AND tenant_id = %s", (id, tenant_id))
            uso = cursor.fetchone()
            
            if uso and uso['total'] > 0:
                return jsonify({"error": "Cannot delete: packaging is assigned to products in the Recipes section"}), 400
            
            # 💡 SAAS-IFICATION: Ensure only packaging from the correct tenant can be deleted.
            cursor.execute("DELETE FROM empaques WHERE id_empaque=%s AND tenant_id = %s", (id, tenant_id))
            conn.commit()
            return jsonify({"message": "Packaging deleted from catalog"})
    except Exception as e:
        conn.rollback()
        logger.error(f"Error in delete_empaque: {e}", exc_info=True)
        return jsonify({"error": "Error deleting packaging"}), 500

# ==================== PACKAGING ASSIGNED TO PRODUCTS ====================
# These are used specifically within the recipe section of each product

@empaques_bp.route("/producto/<int:producto_id>", methods=["GET"])
@login_required
def get_empaques_producto(producto_id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT re.id, re.id_empaque, re.cantidad, re.subtotal,
                       e.nombre, e.precio
                FROM recetas_empaques re
                LEFT JOIN empaques e ON re.id_empaque = e.id_empaque
                WHERE re.id_producto = %s AND re.tenant_id = %s
            """, (producto_id, tenant_id))
            filas = cursor.fetchall()

            items = []
            costo_total = 0
            for f in filas:
                precio_unitario = float(f["precio"] or 0)
                cantidad = int(f["cantidad"] or 1)
                subtotal = float(f["subtotal"] or (precio_unitario * cantidad))
                
                costo_total += subtotal
                items.append({
                    "id":         f["id"],
                    "id_empaque": f["id_empaque"],
                    "cantidad":   cantidad,
                    "subtotal":   subtotal,
                    "nombre":     f["nombre"],
                    "precio":     precio_unitario
                })

            return jsonify({"empaques": items, "costo_total_empaque": costo_total})
    except Exception as e:
        logger.error(f"Error in get_empaques_producto: {str(e)}")
        return jsonify({"error": "Error fetching product packaging"}), 500

@empaques_bp.route("/producto/<int:producto_id>", methods=["POST"])
@login_required
def add_empaque_producto(producto_id):
    tenant_id = current_user.tenant_id
    data = request.get_json()
    conn = get_db()

    id_empaque = data.get("id_empaque")
    # 💡 FINAL FIX: Diagnostic logs revealed the frontend sends the quantity
    # in the 'cantidad_empaque' field. Added to the logic to capture the value correctly.
    cantidad = data.get("cantidad_empaque") or data.get("cantidad") or data.get("cantidad_necesaria") or 1

    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            if not id_empaque:
                return jsonify({"error": "id_empaque is required"}), 400

            # 💡 SAAS-IFICATION: Get the packaging price from the correct tenant.
            cursor.execute("SELECT precio FROM empaques WHERE id_empaque=%s AND tenant_id = %s", (id_empaque, current_user.tenant_id))
            row = cursor.fetchone()
            
            if not row:
                return jsonify({"error": "Packaging not found"}), 404

            precio_empaque = float(row["precio"] or 0)
            subtotal = precio_empaque * int(cantidad)
            
            # 💡 SAAS-IFICATION: Insert the tenant_id.
            cursor.execute("""
                INSERT INTO recetas_empaques (id_producto, id_empaque, cantidad, subtotal, tenant_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (producto_id, id_empaque, cantidad, subtotal, tenant_id))
            conn.commit()

        # 💡 FIX: Recalculate the product cost to update it in the 'productos' table.
        calcular_costo_completo(producto_id, tenant_id)

        return jsonify({"message": "Packaging assigned to product"}), 201
    except Exception as e:
        conn.rollback()
        logger.error(f"Error in add_empaque_producto: {str(e)}")
        return jsonify({"error": "Error assigning packaging"}), 500

@empaques_bp.route("/producto/item/<int:id>", methods=["DELETE"])
@login_required
def delete_empaque_producto(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    id_producto = None
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # 💡 FIX: Get the id_producto BEFORE deleting to be able to recalculate.
            # 💡 SAAS-IFICATION: Ensure only an item from the correct tenant can be deleted.
            cursor.execute("SELECT id_producto FROM recetas_empaques WHERE id = %s AND tenant_id = %s", (id, tenant_id))
            resultado = cursor.fetchone()
            
            if resultado:
                id_producto = resultado['id_producto']
                cursor.execute("DELETE FROM recetas_empaques WHERE id=%s AND tenant_id = %s", (id, tenant_id))
                conn.commit()
            else:
                return jsonify({"message": "Packaging item not found"}), 404

        # 💡 FIX: If deleted, recalculate the product cost.
        if id_producto:
            calcular_costo_completo(id_producto, tenant_id)

        return jsonify({"message": "Packaging removed from product"})
    except Exception as e:
        conn.rollback()
        logger.error(f"Error in delete_empaque_producto: {str(e)}")
        return jsonify({"error": "Error removing packaging from product"}), 500