from flask import Blueprint, jsonify, request
from flask_login import login_required
from extensions import mysql
from flask_cors import cross_origin

detalle_pedidos_bp = Blueprint("detalle_pedidos", __name__, url_prefix="/detalle_pedidos")

# Obtener todos los detalles de todos los pedidos
@detalle_pedidos_bp.route("/", methods=["GET"])
@login_required
@cross_origin()
def get_detalles():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT 
            dp.id_detalle, 
            dp.pedido_id, 
            p.nombre AS producto, 
            dp.cantidad, 
            dp.precio_unitario,
            dp.subtotal
        FROM detalle_pedidos dp
        LEFT JOIN productos p ON dp.producto_id = p.id_producto
        ORDER BY dp.id_detalle DESC
    """)
    filas = cursor.fetchall()
    cursor.close()

    detalles = []
    for f in filas:
        detalles.append({
            "id_detalle": f[0],
            "pedido_id": f[1],
            "producto": f[2],
            "cantidad": f[3],
            "precio_unitario": float(f[4]) if f[4] else 0,
            "subtotal": float(f[5]) if f[5] else 0
        })
    return jsonify(detalles)

# Obtener detalle por ID
@detalle_pedidos_bp.route("/<int:id>", methods=["GET"])
@login_required
@cross_origin()
def get_detalle(id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT 
            dp.id_detalle, 
            dp.pedido_id, 
            p.nombre AS producto, 
            dp.cantidad, 
            dp.precio_unitario,
            dp.subtotal
        FROM detalle_pedidos dp
        LEFT JOIN productos p ON dp.producto_id = p.id_producto
        WHERE dp.id_detalle = %s
    """, (id,))
    f = cursor.fetchone()
    cursor.close()
    
    if not f:
        return jsonify({"error": "Detalle no encontrado"}), 404

    detalle = {
        "id_detalle": f[0],
        "pedido_id": f[1],
        "producto": f[2],
        "cantidad": f[3],
        "precio_unitario": float(f[4]) if f[4] else 0,
        "subtotal": float(f[5]) if f[5] else 0
    }
    return jsonify(detalle)

# Actualizar un detalle
@detalle_pedidos_bp.route("/<int:id>", methods=["PUT"])
@login_required
@cross_origin()
def update_detalle(id):
    data = request.get_json()
    cantidad = data.get("cantidad")
    precio_unitario = data.get("precio_unitario")
    subtotal = data.get("subtotal")

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE detalle_pedidos 
        SET cantidad=%s, precio_unitario=%s, subtotal=%s 
        WHERE id_detalle=%s
    """, (cantidad, precio_unitario, subtotal, id))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Detalle actualizado correctamente"})

# Crear nuevo detalle de pedido
@detalle_pedidos_bp.route("/", methods=["POST"])
@login_required
@cross_origin()
def create_detalle():
    try:
        data = request.get_json()
        
        pedido_id = data.get("pedido_id")
        producto_id = data.get("producto_id")
        cantidad = data.get("cantidad")
        precio_unitario = data.get("precio_unitario")
        subtotal = data.get("subtotal")
        
        # Validar campos requeridos
        if not all([pedido_id, producto_id, cantidad, precio_unitario, subtotal]):
            return jsonify({"error": "Todos los campos son requeridos"}), 400
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
            VALUES (%s, %s, %s, %s, %s)
        """, (pedido_id, producto_id, cantidad, precio_unitario, subtotal))
        
        detalle_id = cursor.lastrowid
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            "mensaje": "Detalle de pedido creado correctamente",
            "id_detalle": detalle_id
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

# Eliminar detalle de pedido
@detalle_pedidos_bp.route("/<int:id>", methods=["DELETE"])
@login_required
@cross_origin()
def delete_detalle(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM detalle_pedidos WHERE id_detalle = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Detalle eliminado correctamente"})