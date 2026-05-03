from flask import Blueprint, request, jsonify
from flask_login import login_required
from db import get_db_connection
import os
from werkzeug.utils import secure_filename

# Importamos la función de cálculo desde recetas
from recetas import calcular_costo_completo

productos_bp = Blueprint("productos_bp", __name__, url_prefix="/productos")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_images_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shared-assets', 'images')

# ==================== PREFLIGHT CORS ====================
@productos_bp.route("/", methods=["OPTIONS"])
@productos_bp.route("/<int:id>", methods=["OPTIONS"])
@productos_bp.route("/public", methods=["OPTIONS"])
@productos_bp.route("/upload-image", methods=["OPTIONS"])
def handle_options(id=None):
    return jsonify({"status": "ok"}), 200

# ==================== SUBIDA DE IMAGEN ====================
@productos_bp.route("/upload-image", methods=["POST"])
@login_required
def upload_image():
    if 'imagen' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400

    file = request.files['imagen']

    if file.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Formato no permitido. Usa PNG, JPG, JPEG, GIF o WEBP"}), 400

    filename = secure_filename(file.filename)
    images_dir = get_images_dir()
    os.makedirs(images_dir, exist_ok=True)
    file.save(os.path.join(images_dir, filename))

    return jsonify({
        "mensaje": "Imagen subida correctamente",
        "filename": filename
    }), 201

# ==================== RUTAS PRIVADAS (Panel Admin) ====================

@productos_bp.route("/", methods=["GET"])
@login_required
def get_productos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_producto, nombre, categoria, descripcion, precio, imagen, pax, utilidad_porcentaje, costo_produccion, precio_sugerido FROM productos")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@productos_bp.route("/<int:id>", methods=["GET"])
@login_required
def get_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_producto, nombre, categoria, descripcion, precio, imagen, pax, utilidad_porcentaje, costo_produccion, precio_sugerido FROM productos WHERE id_producto=%s", (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return jsonify(row)
    return jsonify({"error": "Producto no encontrado"}), 404

@productos_bp.route("/", methods=["POST"])
@login_required
def add_producto():
    data = request.json
    nombre = data.get("nombre")
    categoria = data.get("categoria")
    descripcion = data.get("descripcion")
    precio = data.get("precio")
    imagen = data.get("imagen")

    if not nombre or not categoria or not precio:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO productos (nombre, categoria, descripcion, precio, imagen)
        VALUES (%s, %s, %s, %s, %s)
    """, (nombre, categoria, descripcion, precio, imagen))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensaje": "Producto agregado"}), 201

@productos_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_producto(id):
    data = request.json
    nombre = data.get("nombre")
    categoria = data.get("categoria")
    descripcion = data.get("descripcion")
    precio = data.get("precio")
    imagen = data.get("imagen")
    pax = data.get("pax")
    utilidad_porcentaje = data.get("utilidad_porcentaje")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE productos
        SET nombre=%s, categoria=%s, descripcion=%s, precio=%s, imagen=%s,
            pax=%s, utilidad_porcentaje=%s
        WHERE id_producto=%s
    """, (nombre, categoria, descripcion, precio, imagen, pax, utilidad_porcentaje, id))
    conn.commit()
    cursor.close()
    conn.close()

    # ←←← ESTO ES LO QUE FALTABA: recalcular después de cambiar PAX o Utilidad
    calcular_costo_completo(id)

    return jsonify({"mensaje": "Producto actualizado"})

@productos_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id_producto=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensaje": "Producto eliminado"})

# ==================== ENDPOINTS PÚBLICOS (Landing Page) ====================

@productos_bp.route("/public", methods=["GET"])
def get_productos_public():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_producto, nombre, categoria, descripcion, precio, imagen
            FROM productos
            ORDER BY categoria, nombre
        """)
        productos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "productos": productos})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500