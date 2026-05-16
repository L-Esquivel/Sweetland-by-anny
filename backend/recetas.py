from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from db import get_db # 🟢 Import the new DB manager
import logging
from psycopg2.extras import DictCursor # 🟢 To get results as dictionaries

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

recetas_bp = Blueprint("recipes", __name__, url_prefix="/recipes")

# ========================================
# EXACT COSTING LOGIC (final corrected version)
# ========================================
def calculate_full_cost(product_id, tenant_id, pax=None, profit_percentage=None):
    """
    Calculates the full cost of a product.
    This is the core costing engine of the application.
    """
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # 💡 SAAS-IFICATION: All internal queries now use tenant_id.
            # 1. TOTAL 1 = Cost of ingredients (from recetas_ingredientes)
            cursor.execute("""
                SELECT COALESCE(SUM(costo_ingrediente), 0) as base_cost
                FROM recetas_ingredientes
                WHERE id_producto = %s AND tenant_id = %s
            """, (product_id, tenant_id))
            result = cursor.fetchone()
            base_cost = float(result.get('base_cost', 0) if result else 0)

            # 2. Operational Expenses = TOTAL 1 * 35%
            operational_expenses = base_cost * 0.35

            # 3. Market Depreciation = TOTAL 1 * 10%
            market_depreciation = base_cost * 0.10

            # 4. TOTAL 2 = TOTAL 1 * 1.45
            total_2 = base_cost * 1.45

            # 5. Equipment Depreciation = TOTAL 2 * 5%
            equipment_depreciation = total_2 * 0.05

            # 6. Total packaging cost
            cursor.execute("""
                SELECT COALESCE(SUM(subtotal), 0) as packaging_cost
                FROM recetas_empaques
                WHERE id_producto = %s AND tenant_id = %s
            """, (product_id, tenant_id))
            packaging_result = cursor.fetchone()
            packaging_cost = float(packaging_result.get('packaging_cost', 0) if packaging_result else 0)

            # 7. TOTAL 3 (Production Cost)
            production_cost = total_2 + equipment_depreciation + packaging_cost

            # 8. Get PAX and profit percentage from DB if not provided
            if pax is None or profit_percentage is None:
                cursor.execute("""
                    SELECT pax, utilidad_porcentaje
                    FROM productos
                    WHERE id_producto = %s AND tenant_id = %s
                """, (product_id, tenant_id))
                prod = cursor.fetchone()
                pax_db = int(prod.get('pax', 1)) if prod and prod.get('pax') is not None else 1
                profit_db = float(prod.get('utilidad_porcentaje', 40.0)) if prod and prod.get('utilidad_porcentaje') is not None else 40.0

                pax = pax if pax is not None else pax_db
                profit_percentage = profit_percentage if profit_percentage is not None else profit_db

            # 9. Profit
            profit = production_cost * (profit_percentage / 100)

            # 10. TOTAL 4
            total_4 = production_cost + profit

            # 11. I.C. (Consumption Tax) = TOTAL 4 * 8%
            consumption_tax = total_4 * 0.08

            # 12. Final Value = TOTAL 4 * 1.08
            final_value = total_4 * 1.08

            # 13. Final Suggested Price (per unit)
            suggested_price = final_value / pax if pax > 0 else 0

            # Update the 'productos' table with the final values
            cursor.execute("""
                UPDATE productos
                SET costo_produccion = %s,
                    pax = %s,
                    utilidad_porcentaje = %s,
                    precio = %s
                WHERE id_producto = %s AND tenant_id = %s
            """, (production_cost, pax, profit_percentage, suggested_price, product_id, tenant_id))

        conn.commit()

        return {
            "base_cost": round(base_cost, 2),
            "operational_expenses": round(operational_expenses, 2),
            "market_depreciation": round(market_depreciation, 2),
            "equipment_depreciation": round(equipment_depreciation, 2),
            "packaging_cost": round(packaging_cost, 2),
            "production_cost": round(production_cost, 2),
            "profit": round(profit, 2),
            "pre_tax_total": round(total_4, 2),
            "consumption_tax": round(consumption_tax, 2),
            "final_value": round(final_value, 2),
            "suggested_price": round(suggested_price, 2),
            "pax": pax,
            "profit_percentage": profit_percentage
        }

    except Exception as e:
        logger.error(f"Error in calculate_full_cost: {str(e)}")
        if 'conn' in locals() and conn: conn.rollback()
        raise

# ================================
# RECALCULATE WITH PAX AND PROFIT
# ================================
@recetas_bp.route("/recalcular", methods=["POST"])
@login_required
def recalculate_costs():
    tenant_id = current_user.tenant_id
    data = request.get_json()
    product_id = data.get("id_producto")
    pax = data.get("pax")
    profit_percentage = data.get("utilidad_porcentaje")

    if not product_id:
        return jsonify({"error": "product_id is required"}), 400

    try:
        costs = calculate_full_cost(
            product_id,
            tenant_id,
            pax=int(pax) if pax is not None else None,
            profit_percentage=float(profit_percentage) if profit_percentage is not None else None
        )
        return jsonify({
            "message": "Costs recalculated successfully",
            "costs": costs
        })
    except Exception as e:
        logger.error(f"Error in recalculate_costs: {str(e)}")
        return jsonify({"error": "Error recalculating costs"}), 500

# ================================
# Obtener todas las recetas
# ================================
@recetas_bp.route("/", methods=["GET"])
@login_required
def get_recipes():
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
            rows_raw = cursor.fetchall()
            # FIX: Convert to dict to ensure JSON serialization.
            rows = [dict(row) for row in rows_raw]
            return jsonify(rows)
    except Exception as e:
        logger.error(f"Error in get_recipes: {str(e)}")
        return jsonify({"error": "Error fetching recipes"}), 500

# ================================
# Obtener recetas + empaques + costos de un producto
# ================================
@recetas_bp.route("/producto/<int:product_id>", methods=["GET"])
@login_required
def get_product_recipe_details(product_id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # Ingredientes
            cursor.execute("""
                SELECT ri.id, ri.id_ingrediente, ri.cantidad_necesaria,
                       i.nombre AS ingrediente, i.unidad_medida, i.costo_por_unidad,
                       ri.costo_ingrediente
                FROM recetas_ingredientes ri
                LEFT JOIN ingredientes i ON ri.id_ingrediente = i.id_ingrediente AND i.tenant_id = %s
                WHERE ri.id_producto = %s AND ri.tenant_id = %s
            """, (tenant_id, product_id, tenant_id))
            recipes_raw = cursor.fetchall()
            # FIX: Convert to dict to ensure JSON serialization.
            recipes = [dict(row) for row in recipes_raw]

            # Empaques
            cursor.execute("""
                SELECT re.id, re.id_empaque, re.cantidad, re.subtotal,
                       e.nombre, e.precio
                FROM recetas_empaques re
                LEFT JOIN empaques e ON re.id_empaque = e.id_empaque AND e.tenant_id = %s
                WHERE re.id_producto = %s AND re.tenant_id = %s
            """, (tenant_id, product_id, tenant_id))
            packaging_raw = cursor.fetchall()
            # FIX: Convert to dict to ensure JSON serialization.
            packaging = [dict(row) for row in packaging_raw]

            # Costos
            costs = calculate_full_cost(product_id, tenant_id)

            return jsonify({
                "recipes": recipes,
                "packaging": packaging,
                "costs": costs
            })
    except Exception as e:
        logger.error(f"Error in get_product_recipe_details: {str(e)}")
        return jsonify({"error": "Error fetching recipe data"}), 500

# ================================
# CRUD Recetas
# ================================
@recetas_bp.route("/", methods=["POST"])
@login_required
def add_recipe_ingredient():
    tenant_id = current_user.tenant_id
    data = request.get_json()
    product_id = data.get("id_producto")
    ingredient_id = data.get("id_ingrediente")
    quantity_needed = data.get("cantidad_necesaria")

    if not product_id or not ingredient_id or quantity_needed is None:
        return jsonify({"error": "Required fields are missing"}), 400
    
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # Obtener costo del ingrediente
            cursor.execute("SELECT costo_por_unidad FROM ingredientes WHERE id_ingrediente = %s AND tenant_id = %s", (ingredient_id, tenant_id))
            ingrediente = cursor.fetchone()
            if not ingrediente:
                return jsonify({"error": "Ingrediente no encontrado"}), 404
            
            costo_unitario = float(ingrediente['costo_por_unidad'])
            costo_ingrediente = costo_unitario * float(cantidad_necesaria)

            cursor.execute("""
                INSERT INTO recetas_ingredientes (id_producto, id_ingrediente, cantidad_necesaria, costo_ingrediente, tenant_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (product_id, ingredient_id, quantity_needed, costo_ingrediente, tenant_id))
            conn.commit()
            
            calculate_full_cost(product_id, tenant_id)
            return jsonify({"message": "Ingredient added to recipe successfully"}), 201
    except Exception as e:
        if conn: conn.rollback()
        logger.error(f"Error in add_recipe_ingredient: {e}", exc_info=True)
        return jsonify({"error": "Error adding ingredient to recipe"}), 500

@recetas_bp.route("/multiple", methods=["POST"])
@login_required
def add_multiple_recipe_ingredients():
    tenant_id = current_user.tenant_id
    data = request.get_json()
    product_id = data.get("id_producto")
    ingredientes = data.get("ingredientes", [])

    if not product_id or not ingredientes:
        return jsonify({"error": "Required data is missing"}), 400

    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            for ing in ingredientes:
                ingredient_id = ing.get("id_ingrediente")
                quantity_needed = ing.get("cantidad_necesaria")

                cursor.execute("SELECT costo_por_unidad FROM ingredientes WHERE id_ingrediente = %s AND tenant_id = %s", (ingredient_id, tenant_id))
                ing_data = cursor.fetchone()
                if not ing_data: continue # Opcional: manejar error si un ingrediente no existe

                costo_unitario = float(ing_data['costo_por_unidad'])
                costo_ingrediente = costo_unitario * float(quantity_needed)

                cursor.execute("""
                    INSERT INTO recetas_ingredientes (id_producto, id_ingrediente, cantidad_necesaria, costo_ingrediente, tenant_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (product_id, ingredient_id, quantity_needed, costo_ingrediente, tenant_id))
            conn.commit()
            calculate_full_cost(product_id, tenant_id)
            return jsonify({"message": "Ingredients added successfully"}), 201
    except Exception as e:
        if conn: conn.rollback()
        logger.error(f"Error in add_multiple_recipe_ingredients: {e}", exc_info=True)
        return jsonify({"error": "Error adding ingredients"}), 500

@recetas_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_recipe_ingredient(id):
    tenant_id = current_user.tenant_id
    data = request.get_json()
    product_id = data.get("id_producto")
    ingredient_id = data.get("id_ingrediente")
    quantity_needed = data.get("cantidad_necesaria")

    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT costo_por_unidad FROM ingredientes WHERE id_ingrediente = %s AND tenant_id = %s", (ingredient_id, tenant_id))
            ing_data = cursor.fetchone()
            if not ing_data: return jsonify({"error": "Ingrediente no encontrado"}), 404

            costo_unitario = float(ing_data['costo_por_unidad'])
            costo_ingrediente = costo_unitario * float(quantity_needed)

            cursor.execute("""
                UPDATE recetas_ingredientes
                SET id_producto = %s, id_ingrediente = %s, cantidad_necesaria = %s, costo_ingrediente = %s
                WHERE id = %s AND tenant_id = %s
            """, (product_id, ingredient_id, quantity_needed, costo_ingrediente, id, tenant_id))
            conn.commit()
            if product_id:
                calculate_full_cost(product_id, tenant_id)
            return jsonify({"message": "Recipe ingredient updated successfully"})
    except Exception as e:
        if conn: conn.rollback()
        logger.error(f"Error in update_recipe_ingredient: {e}", exc_info=True)
        return jsonify({"error": "Error updating recipe ingredient"}), 500

@recetas_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_recipe_ingredient(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT id_producto FROM recetas_ingredientes WHERE id = %s AND tenant_id = %s", (id, tenant_id))
            resultado = cursor.fetchone()
            product_id = resultado.get('id_producto') if resultado else None

            cursor.execute("DELETE FROM recetas_ingredientes WHERE id = %s AND tenant_id = %s", (id, tenant_id))
            conn.commit()

            if product_id:
                calculate_full_cost(product_id, tenant_id)

            return jsonify({"message": "Recipe ingredient deleted successfully"})
    except Exception as e:
        if conn: conn.rollback()
        logger.error(f"Error in delete_recipe_ingredient: {e}", exc_info=True)
        return jsonify({"error": "Error deleting recipe ingredient"}), 500

@recetas_bp.route("/producto/<int:product_id>", methods=["DELETE"])
@login_required
def delete_all_product_recipes(product_id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM recetas_ingredientes WHERE id_producto = %s AND tenant_id = %s", (product_id, tenant_id))
            conn.commit()
            calculate_full_cost(product_id, tenant_id)
            return jsonify({"message": "All recipes for the product were deleted"})
    except Exception as e:
        if conn: conn.rollback()
        logger.error(f"Error in delete_all_product_recipes: {e}", exc_info=True)
        return jsonify({"error": "Error deleting product recipes"}), 500