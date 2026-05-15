import os
import cloudinary
import cloudinary.uploader
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user # 🟢 Import current_user
from psycopg2.extras import DictCursor # 🟢 To get results as dictionaries

from db import get_db # 🟢 Import the new DB manager
from utils import admin_required, registrar_log # 🛡️ Import the log utility
from recetas import calcular_costo_completo # Ensure this file is also migrated

productos_bp = Blueprint("productos_bp", __name__, url_prefix="/productos")

# CLOUDINARY CONFIGURATION
cloudinary.config( 
  cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.getenv('CLOUDINARY_API_KEY'), 
  api_secret = os.getenv('CLOUDINARY_API_SECRET'),
  secure = True
)

# ==========================================
# IMAGE UPLOAD TO CLOUD
# ==========================================
@productos_bp.route("/upload-image", methods=["POST"])
@admin_required
def upload_image():
    if 'imagen' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['imagen']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # 💡 SAAS-IFICATION: Isolate images by tenant in Cloudinary.
        tenant_id = current_user.tenant_id
        
        upload_result = cloudinary.uploader.upload(
            file,
            folder=f"precivox/tenants/{tenant_id}/productos",
            resource_type="image"
        )
        secure_url = upload_result.get("secure_url")
        
        # 🛡️ AUDIT: File upload log
        registrar_log(f"Uploaded new image to the cloud: {file.filename}")
        
        return jsonify({
            "message": "Image successfully uploaded to the cloud ✅",
            "filename": secure_url
        }), 201

    except Exception as e:
        current_app.logger.error(f"Cloudinary Error: {str(e)}")
        return jsonify({"error": "Failed to upload to cloud"}), 500

# ==========================================
# PRODUCT MANAGEMENT
# ==========================================

@productos_bp.route("/", methods=["GET"])
@login_required
def get_products():
    # 🔵 POSTGRESQL CONNECTION PATTERN
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        # Use a 'with' statement to automatically close the cursor
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # FIX: Convert results to a list of dictionaries to ensure JSON serialization.
            # This solves the issue of the product table appearing empty.
            # Also, COALESCE is used to ensure the price is never null and avoid 'NaN' errors on the frontend.
            cursor.execute("""
                SELECT id_producto, nombre, categoria, descripcion, COALESCE(precio, 0) as precio, imagen, stock, controla_stock, costo_produccion, pax, utilidad_porcentaje 
                FROM productos WHERE tenant_id = %s ORDER BY nombre
            """, (tenant_id,))
            products_raw = cursor.fetchall()
            products = [dict(row) for row in products_raw]
            return jsonify(products)
    except Exception as e:
        current_app.logger.error(f"Error in get_products: {e}")
        return jsonify({"error": "Error fetching products"}), 500

@productos_bp.route("/", methods=["POST"])
@admin_required
def add_product():
    data = request.json
    nombre = data.get("nombre")
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 💡 SAAS-IFICATION: Insert the tenant_id when creating a new product.
            cursor.execute("""
                INSERT INTO productos (nombre, categoria, descripcion, precio, imagen, stock, controla_stock, costo_produccion, tenant_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s) -- Initialize costo_produccion to 0
            """, (nombre, data.get("categoria"), data.get("descripcion"), 
                  data.get("precio"), data.get("imagen"), data.get("stock", 0), data.get("controla_stock", False), tenant_id))
            
            conn.commit() # 🔵 Commit on the connection
            
            # 🛡️ AUDIT: Creation log
            registrar_log(f"Created product: {nombre}")
            
            return jsonify({"message": "Product created"}), 201
    except Exception as e:
        conn.rollback() # 🔵 Rollback on the connection
        current_app.logger.error(f"Error in add_product: {e}")
        return jsonify({"error": "Error creating product"}), 500

@productos_bp.route("/<int:id>", methods=["PUT"])
@admin_required
def update_product(id):
    data = request.json
    nombre = data.get("nombre")
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 💡 SAAS-IFICATION: Ensure only a product from the correct tenant can be updated.
            cursor.execute("""
                UPDATE productos
                SET nombre=%s, categoria=%s, descripcion=%s, precio=%s, imagen=%s,
                    pax=%s, utilidad_porcentaje=%s, stock=%s, controla_stock=%s
                WHERE id_producto=%s AND tenant_id = %s
            """, (nombre, data.get("categoria"), data.get("descripcion"), 
                  data.get("precio"), data.get("imagen"), data.get("pax"),
                  data.get("utilidad_porcentaje"), data.get("stock"), data.get("controla_stock"), id, tenant_id))
            
            conn.commit()
            # calcular_costo_completo(id, tenant_id) # This function must also be migrated
            
            registrar_log(f"Updated product ID {id}: {nombre}")
            return jsonify({"message": "Product updated"})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in update_product: {e}")
        return jsonify({"error": "Error updating product"}), 500

@productos_bp.route("/<int:id>", methods=["DELETE"])
@admin_required
def delete_product(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            # 💡 SAAS-IFICATION: Ensure only a product from the correct tenant can be deleted.
            cursor.execute("DELETE FROM productos WHERE id_producto=%s AND tenant_id = %s", (id, tenant_id))
            conn.commit()
            
            # 🛡️ AUDIT: Deletion log
            registrar_log(f"Deleted product ID {id}")
            
            return jsonify({"message": "Deleted"})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error in delete_product: {e}")
        return jsonify({"error": "Error deleting product"}), 500

@productos_bp.route("/public", methods=["GET"])
def get_public_products():
    # ⚠️ MULTI-TENANT SECURITY WARNING:
    # This endpoint is for the public landing page. In a multi-tenant system,
    # we cannot simply return all products. We need to know which tenant's
    # products to display.
    #
    # TEMPORARY SOLUTION: We assume the public landing page always corresponds to tenant with id=1 (Sweetland).
    # The definitive solution would involve using subdomains (sweetland.precivox.com) or
    # an identifier in the URL to determine the tenant dynamically.
    tenant_id_publico = os.getenv('PUBLIC_TENANT_ID', 1)
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT id_producto, nombre, categoria, descripcion, precio, imagen 
                FROM productos WHERE tenant_id = %s ORDER BY nombre
            """, (tenant_id_publico,))
            products = cursor.fetchall()
            return jsonify({"success": True, "productos": products})
    except Exception as e:
        current_app.logger.error(f"Error in get_public_products: {e}")
        return jsonify({"error": "Error fetching public products"}), 500