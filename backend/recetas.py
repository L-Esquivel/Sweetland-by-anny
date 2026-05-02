from flask import Blueprint, jsonify, request
from flask_login import login_required
from extensions import mysql
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

recetas_bp = Blueprint("recetas", __name__, url_prefix="/recetas")

# ================================
# Actualizar costo de producto automáticamente
# ================================
def actualizar_costo_producto(id_producto):
    """Actualiza el costo_produccion en la tabla productos cuando cambia una receta"""
    try:
        cursor = mysql.connection.cursor()
        
        # Calcular nuevo costo total
        cursor.execute("""
            SELECT SUM(r.cantidad_necesaria * i.costo_unitario) as costo_total
            FROM recetas r
            LEFT JOIN ingredientes i ON r.id_ingrediente = i.id_ingrediente
            WHERE r.id_producto = %s
        """, (id_producto,))
        resultado = cursor.fetchone()
        nuevo_costo = float(resultado[0]) if resultado[0] else 0
        
        # Actualizar el producto
        cursor.execute("""
            UPDATE productos 
            SET costo_produccion = %s 
            WHERE id_producto = %s
        """, (nuevo_costo, id_producto))
        
        mysql.connection.commit()
        cursor.close()
        logger.info(f"Costo actualizado para producto {id_producto}: ${nuevo_costo}")
        
    except Exception as e:
        logger.error(f"Error actualizando costo producto {id_producto}: {str(e)}")
        mysql.connection.rollback()

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

    recetas = []
    for f in filas:
        recetas.append({
            "id_receta": f[0],
            "id_producto": f[1],
            "id_ingrediente": f[2],
            "cantidad_necesaria": f[3],
            "producto": f[4],       # nombre producto
            "ingrediente": f[5]     # nombre ingrediente
        })
    return jsonify(recetas)

# ================================
# Obtener una receta por ID
# ================================
@recetas_bp.route("/<int:id>", methods=["GET"])
@login_required
def get_receta(id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT r.id_receta, r.id_producto, r.id_ingrediente, r.cantidad_necesaria,
               p.nombre AS producto, i.nombre AS ingrediente
        FROM recetas r
        LEFT JOIN productos p ON r.id_producto = p.id_producto
        LEFT JOIN ingredientes i ON r.id_ingrediente = i.id_ingrediente
        WHERE r.id_receta = %s
    """, (id,))
    f = cursor.fetchone()
    cursor.close()

    if not f:
        return jsonify({"error": "Receta no encontrada"}), 404

    receta = {
        "id_receta": f[0],
        "id_producto": f[1],
        "id_ingrediente": f[2],
        "cantidad_necesaria": f[3],
        "producto": f[4],
        "ingrediente": f[5]
    }
    return jsonify(receta)

# ================================
# Obtener recetas por producto
# ================================
@recetas_bp.route("/producto/<int:producto_id>", methods=["GET"])
@login_required
def get_recetas_por_producto(producto_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT r.id_receta, r.id_ingrediente, r.cantidad_necesaria,
               i.nombre AS ingrediente, i.unidad, i.costo_unitario,
               (r.cantidad_necesaria * i.costo_unitario) as costo_ingrediente
        FROM recetas r
        LEFT JOIN ingredientes i ON r.id_ingrediente = i.id_ingrediente
        WHERE r.id_producto = %s
    """, (producto_id,))
    filas = cursor.fetchall()
    cursor.close()

    recetas = []
    costo_total = 0
    for f in filas:
        costo_ingrediente = float(f[6]) if f[6] else 0
        costo_total += costo_ingrediente
        recetas.append({
            "id_receta": f[0],
            "id_ingrediente": f[1],
            "cantidad_necesaria": float(f[2]) if f[2] else 0,
            "ingrediente": f[3],
            "unidad": f[4],
            "costo_unitario": float(f[5]) if f[5] else 0,
            "costo_ingrediente": costo_ingrediente
        })

    return jsonify({
        "recetas": recetas,
        "costo_total_produccion": costo_total
    })

# ================================
# Calcular costo de producción
# ================================
@recetas_bp.route("/costo-produccion/<int:producto_id>", methods=["GET"])
@login_required
def get_costo_produccion(producto_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT SUM(r.cantidad_necesaria * i.costo_unitario) as costo_total
        FROM recetas r
        LEFT JOIN ingredientes i ON r.id_ingrediente = i.id_ingrediente
        WHERE r.id_producto = %s
    """, (producto_id,))
    resultado = cursor.fetchone()
    cursor.close()

    costo_total = float(resultado[0]) if resultado[0] else 0
    return jsonify({"costo_produccion": costo_total})

# ================================
# Crear nueva receta
# ================================
@recetas_bp.route("/", methods=["POST"])
@login_required
def add_receta():
    data = request.get_json()
    id_producto = data.get("id_producto")
    id_ingrediente = data.get("id_ingrediente")
    cantidad_necesaria = data.get("cantidad_necesaria")

    # Validaciones
    if not id_producto or not id_ingrediente or cantidad_necesaria is None:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    cursor = mysql.connection.cursor()
    
    # Verificar que el producto existe
    cursor.execute("SELECT id_producto FROM productos WHERE id_producto = %s", (id_producto,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "El producto no existe"}), 404

    # Verificar que el ingrediente existe
    cursor.execute("SELECT id_ingrediente FROM ingredientes WHERE id_ingrediente = %s", (id_ingrediente,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "El ingrediente no existe"}), 404

    cursor.execute("""
        INSERT INTO recetas (id_producto, id_ingrediente, cantidad_necesaria)
        VALUES (%s, %s, %s)
    """, (id_producto, id_ingrediente, cantidad_necesaria))
    mysql.connection.commit()
    
    # ACTUALIZAR COSTO DEL PRODUCTO AUTOMÁTICAMENTE
    actualizar_costo_producto(id_producto)
    
    cursor.close()
    return jsonify({"mensaje": "Receta agregada correctamente"})

# ================================
# Crear múltiples recetas (para un producto completo)
# ================================
@recetas_bp.route("/multiple", methods=["POST"])
@login_required
def add_recetas_multiple():
    data = request.get_json()
    id_producto = data.get("id_producto")
    ingredientes = data.get("ingredientes", [])  # Array de {id_ingrediente, cantidad_necesaria}

    if not id_producto or not ingredientes:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    cursor = mysql.connection.cursor()
    
    try:
        # Verificar que el producto existe
        cursor.execute("SELECT id_producto FROM productos WHERE id_producto = %s", (id_producto,))
        if not cursor.fetchone():
            return jsonify({"error": "El producto no existe"}), 404

        # Insertar cada ingrediente
        for ingrediente in ingredientes:
            id_ingrediente = ingrediente.get("id_ingrediente")
            cantidad = ingrediente.get("cantidad_necesaria")
            
            # Verificar que el ingrediente existe
            cursor.execute("SELECT id_ingrediente FROM ingredientes WHERE id_ingrediente = %s", (id_ingrediente,))
            if not cursor.fetchone():
                return jsonify({"error": f"Ingrediente {id_ingrediente} no existe"}), 404

            cursor.execute("""
                INSERT INTO recetas (id_producto, id_ingrediente, cantidad_necesaria)
                VALUES (%s, %s, %s)
            """, (id_producto, id_ingrediente, cantidad))

        mysql.connection.commit()
        
        # ACTUALIZAR COSTO DEL PRODUCTO AUTOMÁTICAMENTE
        actualizar_costo_producto(id_producto)
        
        cursor.close()
        return jsonify({"mensaje": f"{len(ingredientes)} ingredientes agregados a la receta"})

    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        return jsonify({"error": f"Error al crear recetas: {str(e)}"}), 500

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
    cursor.execute("""
        UPDATE recetas
        SET id_producto=%s, id_ingrediente=%s, cantidad_necesaria=%s
        WHERE id_receta=%s
    """, (id_producto, id_ingrediente, cantidad_necesaria, id))
    mysql.connection.commit()
    
    # ACTUALIZAR COSTO DEL PRODUCTO AUTOMÁTICAMENTE
    actualizar_costo_producto(id_producto)
    
    cursor.close()
    return jsonify({"mensaje": "Receta actualizada correctamente"})

# ================================
# Eliminar receta
# ================================
@recetas_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_receta(id):
    cursor = mysql.connection.cursor()
    
    # PRIMERO obtener el id_producto antes de eliminar
    cursor.execute("SELECT id_producto FROM recetas WHERE id_receta = %s", (id,))
    resultado = cursor.fetchone()
    id_producto = resultado[0] if resultado else None

    # Luego eliminar
    cursor.execute("DELETE FROM recetas WHERE id_receta=%s", (id,))
    mysql.connection.commit()

    # ACTUALIZAR COSTO DEL PRODUCTO AUTOMÁTICAMENTE
    if id_producto:
        actualizar_costo_producto(id_producto)
    
    cursor.close()
    return jsonify({"mensaje": "Receta eliminada correctamente"})

# ================================
# Eliminar todas las recetas de un producto
# ================================
@recetas_bp.route("/producto/<int:producto_id>", methods=["DELETE"])
@login_required
def delete_recetas_producto(producto_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM recetas WHERE id_producto = %s", (producto_id,))
    mysql.connection.commit()
    
    # ACTUALIZAR COSTO DEL PRODUCTO AUTOMÁTICAMENTE
    actualizar_costo_producto(producto_id)
    
    cursor.close()
    return jsonify({"mensaje": "Recetas del producto eliminadas correctamente"})