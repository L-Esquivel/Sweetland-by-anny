from flask import Blueprint, request, jsonify
from flask_login import login_required
from db import get_db_connection
from utils import admin_required
from recetas import calcular_costo_completo
import os
from werkzeug.utils import secure_filename

productos_bp = Blueprint("productos_bp", __name__, url_prefix="/productos")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_images_dir():
    # Asegura que las imágenes se guarden en la carpeta static del backend
    return os.path.join(os.path.dirname(__file__), 'static', 'images')

@productos_bp.route("/upload-image", methods=["POST"])
@login_required
@admin_required
def upload_image():
    if 'imagen' not in request.files: return jsonify({"error": "No hay archivo"}), 400
    file = request.files['imagen']
    if file.filename == '': return jsonify({"error": "Nombre vacío"}), 400
    if not allowed_file(file.filename): return jsonify({"error": "Formato inválido"}), 400

    filename = secure_filename(file.filename)
    images_dir = get_images_dir()
    os.makedirs(images_dir, exist_ok=True)
    file.save(os.path.join(images_dir, filename))
    return jsonify({"mensaje": "Imagen subida", "filename": filename}), 201

@productos_bp.route("/", methods=["GET"])
@login_required
def get_productos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(list(rows))

@productos_bp.route("/<int:id>", methods=["GET"])
@login_required
def get_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE id_producto=%s", (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row: return jsonify(row)
    return jsonify({"error": "No encontrado"}), 404

@productos_bp.route("/", methods=["POST"])
@login_required
@admin_required
def add_producto():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO productos (nombre, categoria, descripcion, precio, imagen, stock, controla_stock)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (data.get("nombre"), data.get("categoria"), data.get("descripcion"), 
              data.get("precio"), data.get("imagen"), data.get("stock", 0), data.get("controla_stock", False)))
        conn.commit()
        return jsonify({"mensaje": "Producto creado"}), 201
    finally:
        cursor.close()
        conn.close()

@productos_bp.route("/<int:id>", methods=["PUT"])
@login_required
@admin_required
def update_producto(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE productos
            SET nombre=%s, categoria=%s, descripcion=%s, precio=%s, imagen=%s,
                pax=%s, utilidad_porcentaje=%s, stock=%s, controla_stock=%s
            WHERE id_producto=%s
        """, (data.get("nombre"), data.get("categoria"), data.get("descripcion"), 
              data.get("precio"), data.get("imagen"), data.get("pax"), 
              data.get("utilidad_porcentaje"), data.get("stock", 0), data.get("controla_stock", False), id))
        conn.commit()
        calcular_costo_completo(id)
        return jsonify({"mensaje": "Producto actualizado"})
    finally:
        cursor.close()
        conn.close()

@productos_bp.route("/<int:id>", methods=["DELETE"])
@login_required
@admin_required
def delete_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id_producto=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensaje": "Eliminado"})

@productos_bp.route("/public", methods=["GET"])
def get_productos_public():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_producto, nombre, categoria, descripcion, precio, imagen FROM productos ORDER BY nombre")
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "productos": list(productos)})