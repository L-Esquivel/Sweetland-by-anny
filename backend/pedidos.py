from flask import Blueprint, jsonify, request
from flask_login import login_required
from extensions import mysql
import logging
from werkzeug.security import generate_password_hash
import secrets
import string

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")

@pedidos_bp.route("/", methods=["GET"])
@login_required
def get_pedidos():
    try:
        logger.debug("Ejecutando consulta de pedidos")
        cursor = mysql.connection.cursor()
        
        # Primero verificar si existe el campo 'estado'
        cursor.execute("SHOW COLUMNS FROM pedidos LIKE 'estado'")
        tiene_estado = cursor.fetchone()
        
        if tiene_estado:
            # Consulta CON campo estado
            cursor.execute("""
                SELECT 
                    p.id_pedido, 
                    u.nombre AS cliente_nombre,
                    u.telefono AS cliente_telefono,
                    p.fecha_pedido, 
                    p.estado,
                    p.total,
                    p.direccion,
                    COUNT(dp.id_detalle) as total_productos
                FROM pedidos p
                LEFT JOIN usuarios u ON p.usuario_id = u.id_usuario
                LEFT JOIN detalle_pedidos dp ON p.id_pedido = dp.pedido_id
                GROUP BY p.id_pedido, u.nombre, u.telefono
                ORDER BY p.fecha_pedido DESC
            """)
        else:
            # Consulta SIN campo estado
            cursor.execute("""
                SELECT 
                    p.id_pedido, 
                    u.nombre AS cliente_nombre,
                    u.telefono AS cliente_telefono,
                    p.fecha_pedido, 
                    p.total,
                    p.direccion,
                    p.telefono,
                    COUNT(dp.id_detalle) as total_productos
                FROM pedidos p
                LEFT JOIN usuarios u ON p.usuario_id = u.id_usuario
                LEFT JOIN detalle_pedidos dp ON p.id_pedido = dp.pedido_id
                GROUP BY p.id_pedido, u.nombre, u.telefono
                ORDER BY p.fecha_pedido DESC
            """)
        
        filas = cursor.fetchall()
        logger.debug(f"Pedidos encontrados: {len(filas)}")
        
        cursor.close()

        pedidos = []
        for f in filas:
            if tiene_estado:
                pedido = {
                    "id": f[0],
                    "cliente_nombre": f[1] or "Cliente no registrado",
                    "cliente_telefono": f[2] or "Sin teléfono",
                    "fecha_pedido": f[3].strftime('%Y-%m-%d %H:%M:%S') if f[3] else None,
                    "estado": f[4] or "pendiente",
                    "total": float(f[5]) if f[5] else 0,
                    "direccion": f[6] or "Sin dirección",
                    "total_productos": f[7]
                }
            else:
                pedido = {
                    "id": f[0],
                    "cliente_nombre": f[1] or "Cliente no registrado",
                    "cliente_telefono": f[2] or "Sin teléfono",
                    "fecha_pedido": f[3].strftime('%Y-%m-%d %H:%M:%S') if f[3] else None,
                    "estado": "pendiente",  # Valor por defecto
                    "total": float(f[4]) if f[4] else 0,
                    "direccion": f[5] or "Sin dirección",
                    "total_productos": f[7]
                }
            pedidos.append(pedido)
            logger.debug(f"Pedido procesado: {pedido}")

        return jsonify(pedidos)
        
    except Exception as e:
        logger.error(f"Error en get_pedidos: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

@pedidos_bp.route("/<int:id>/detalles", methods=["GET"])
@login_required
def get_detalles_pedido(id):
    try:
        logger.debug(f"Solicitando detalles del pedido {id}")
        cursor = mysql.connection.cursor()
        
        # Verificar que el pedido existe
        cursor.execute("SELECT id_pedido FROM pedidos WHERE id_pedido = %s", (id,))
        pedido_existe = cursor.fetchone()
        
        if not pedido_existe:
            cursor.close()
            return jsonify({"error": f"Pedido {id} no encontrado"}), 404
        
        # Verificar si existe precio_unitario en detalle_pedidos
        cursor.execute("SHOW COLUMNS FROM detalle_pedidos LIKE 'precio_unitario'")
        tiene_precio_unitario = cursor.fetchone()
        
        if tiene_precio_unitario:
            # Consulta CON precio_unitario
            cursor.execute("""
                SELECT 
                    dp.id_detalle,
                    dp.producto_id,
                    p.nombre AS producto_nombre,
                    p.categoria,
                    dp.cantidad,
                    dp.precio_unitario,
                    dp.subtotal
                FROM detalle_pedidos dp
                INNER JOIN productos p ON dp.producto_id = p.id_producto
                WHERE dp.pedido_id = %s
            """, (id,))
        else:
            # Consulta SIN precio_unitario - calcularlo
            cursor.execute("""
                SELECT 
                    dp.id_detalle,
                    dp.producto_id,
                    p.nombre AS producto_nombre,
                    p.categoria,
                    dp.cantidad,
                    dp.subtotal,
                    p.precio as precio_referencia
                FROM detalle_pedidos dp
                INNER JOIN productos p ON dp.producto_id = p.id_producto
                WHERE dp.pedido_id = %s
            """, (id,))
        
        detalles = cursor.fetchall()
        cursor.close()
        
        logger.debug(f"Detalles encontrados para pedido {id}: {len(detalles)}")
        
        detalles_formateados = []
        for detalle in detalles:
            if tiene_precio_unitario:
                detalle_info = {
                    "id": detalle[0],
                    "producto_id": detalle[1],
                    "producto_nombre": detalle[2],
                    "categoria": detalle[3],
                    "cantidad": detalle[4],
                    "precio_unitario": float(detalle[5]) if detalle[5] else 0,
                    "subtotal": float(detalle[6]) if detalle[6] else 0
                }
            else:
                # Calcular precio unitario basado en subtotal / cantidad
                cantidad = detalle[4] or 1
                subtotal = float(detalle[5]) if detalle[5] else 0
                precio_unitario = subtotal / cantidad if cantidad > 0 else 0
                
                detalle_info = {
                    "id": detalle[0],
                    "producto_id": detalle[1],
                    "producto_nombre": detalle[2],
                    "categoria": detalle[3],
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "subtotal": subtotal
                }
            detalles_formateados.append(detalle_info)
            logger.debug(f"Detalle: {detalle_info}")

        return jsonify(detalles_formateados)
        
    except Exception as e:
        logger.error(f"Error en get_detalles_pedido: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

@pedidos_bp.route("/<int:id>", methods=["GET"])
@login_required
def get_pedido(id):
    try:
        cursor = mysql.connection.cursor()
        
        # Verificar si existe el campo 'estado'
        cursor.execute("SHOW COLUMNS FROM pedidos LIKE 'estado'")
        tiene_estado = cursor.fetchone()
        
        if tiene_estado:
            cursor.execute("""
                SELECT p.id_pedido, u.nombre, u.telefono, p.fecha_pedido, 
                       p.estado, p.total, p.direccion
                FROM pedidos p
                LEFT JOIN usuarios u ON p.usuario_id = u.id_usuario
                WHERE p.id_pedido = %s
            """, (id,))
        else:
            cursor.execute("""
                SELECT p.id_pedido, u.nombre, u.telefono, p.fecha_pedido, 
                       p.total, p.direccion
                FROM pedidos p
                LEFT JOIN usuarios u ON p.usuario_id = u.id_usuario
                WHERE p.id_pedido = %s
            """, (id,))
            
        f = cursor.fetchone()
        cursor.close()
        
        if not f:
            return jsonify({"error": "Pedido no encontrado"}), 404

        if tiene_estado:
            pedido = {
                "id_pedido": f[0],
                "cliente_nombre": f[1] or "Cliente no registrado",
                "cliente_telefono": f[2] or "Sin teléfono",
                "fecha_pedido": f[3].strftime('%Y-%m-%d %H:%M:%S') if f[3] else None,
                "estado": f[4] or "pendiente",
                "total": float(f[5]) if f[5] else 0,
                "direccion": f[6] or "Sin dirección"
            }
        else:
            pedido = {
                "id_pedido": f[0],
                "cliente_nombre": f[1] or "Cliente no registrado",
                "cliente_telefono": f[2] or "Sin teléfono",
                "fecha_pedido": f[3].strftime('%Y-%m-%d %H:%M:%S') if f[3] else None,
                "estado": "pendiente",
                "total": float(f[4]) if f[4] else 0,
                "direccion": f[5] or "Sin dirección"
            }
        return jsonify(pedido)
        
    except Exception as e:
        logger.error(f"Error en get_pedido: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

@pedidos_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_pedido(id):
    try:
        data = request.get_json()
        total = data.get("total")
        direccion = data.get("direccion")
        telefono = data.get("telefono")
        estado = data.get("estado")

        cursor = mysql.connection.cursor()
        
        # Verificar si existe el campo 'estado'
        cursor.execute("SHOW COLUMNS FROM pedidos LIKE 'estado'")
        tiene_estado = cursor.fetchone()
        
        if tiene_estado and estado:
            cursor.execute("""
                UPDATE pedidos 
                SET total=%s, direccion=%s, telefono=%s, estado=%s 
                WHERE id_pedido=%s
            """, (total, direccion, telefono, estado, id))
        else:
            cursor.execute("""
                UPDATE pedidos 
                SET total=%s, direccion=%s, telefono=%s
                WHERE id_pedido=%s
            """, (total, direccion, telefono, id))
            
        mysql.connection.commit()
        cursor.close()
        return jsonify({"mensaje": "Pedido actualizado correctamente"})
        
    except Exception as e:
        logger.error(f"Error en update_pedido: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

@pedidos_bp.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_pedido(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM detalle_pedidos WHERE pedido_id = %s", (id,))
        cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"mensaje": "Pedido eliminado correctamente"})
        
    except Exception as e:
        logger.error(f"Error en delete_pedido: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

@pedidos_bp.route("/", methods=["POST"])
@login_required
def create_pedido():
    try:
        data = request.get_json()
        
        usuario_id = data.get("usuario_id")
        cliente_telefono = data.get("telefono")
        direccion = data.get("direccion")
        total = data.get("total", 0)
        
        cursor = mysql.connection.cursor()
        
        # Verificar si existe el campo 'estado'
        cursor.execute("SHOW COLUMNS FROM pedidos LIKE 'estado'")
        tiene_estado = cursor.fetchone()

        if tiene_estado:
            cursor.execute("""
                INSERT INTO pedidos (usuario_id, telefono, direccion, total, estado, fecha_pedido)
                VALUES (%s, %s, %s, %s, 'pendiente', NOW())
            """, (usuario_id, cliente_telefono, direccion, total))
        else:
            cursor.execute("""
                INSERT INTO pedidos (usuario_id, telefono, direccion, total, fecha_pedido)
                VALUES (%s, %s, %s, %s, NOW())
            """, (usuario_id, cliente_telefono, direccion, total))
        
        pedido_id = cursor.lastrowid
        mysql.connection.commit()
        cursor.close()
        
        # ✅ DEBUG: Verificar qué ID se está devolviendo
        print(f"🎯 [BACKEND] Pedido creado con ID: {pedido_id}")
        
        return jsonify({
            "mensaje": "Pedido creado correctamente",
            "id_pedido": pedido_id  # ← Asegúrate de que esto sea correcto
        }), 201
        
    except Exception as e:
        logger.error(f"Error en create_pedido: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

@pedidos_bp.route("/<int:id>/estado", methods=["PUT"])
@login_required
def update_estado_pedido(id):
    try:
        data = request.get_json()
        nuevo_estado = data.get("estado")
        
        # Validar estados permitidos
        estados_permitidos = ['pendiente', 'confirmado', 'en_preparacion', 'completado', 'cancelado']
        if nuevo_estado not in estados_permitidos:
            return jsonify({"error": "Estado no válido"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE pedidos 
            SET estado = %s 
            WHERE id_pedido = %s
        """, (nuevo_estado, id))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            "mensaje": f"Estado del pedido actualizado a '{nuevo_estado}'",
            "estado": nuevo_estado
        })
        
    except Exception as e:
        logger.error(f"Error en update_estado_pedido: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

@pedidos_bp.route("/usuarios", methods=["GET"])
@login_required
def get_usuarios():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT id_usuario, nombre, telefono, email, direccion 
            FROM usuarios 
            WHERE rol = 'cliente'
            ORDER BY nombre
        """)
        filas = cursor.fetchall()
        cursor.close()

        usuarios = []
        for f in filas:
            usuarios.append({
                "id_usuario": f[0],
                "nombre": f[1],
                "telefono": f[2] or "",
                "email": f[3] or "",
                "direccion": f[4] or ""
            })
        
        return jsonify(usuarios)
        
    except Exception as e:
        logger.error(f"Error en get_usuarios: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

@pedidos_bp.route("/usuarios", methods=["POST"])
@login_required
def create_usuario():
    try:
        data = request.get_json()
        
        nombre = data.get("nombre")
        email = data.get("email")
        telefono = data.get("telefono", "")
        direccion = data.get("direccion", "")
        
        # Validar campos obligatorios
        if not nombre or not email:
            return jsonify({"error": "Nombre y email son requeridos"}), 400
        
        # Generar un password temporal
        password_temp = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        password_hash = generate_password_hash(password_temp)
        
        cursor = mysql.connection.cursor()
        
        # Verificar si el email ya existe
        cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            return jsonify({"error": "El email ya está registrado"}), 400
        
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, telefono, direccion, rol, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, 'cliente', NOW())
        """, (nombre, email, password_hash, telefono, direccion))
        
        usuario_id = cursor.lastrowid
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            "mensaje": "Usuario creado correctamente",
            "id_usuario": usuario_id,
            "nombre": nombre,
            "email": email,
            "telefono": telefono,
            "direccion": direccion,
            "password_temporal": password_temp
        }), 201
        
    except Exception as e:
        logger.error(f"Error en create_usuario: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500
    
@pedidos_bp.route("/<int:pedido_id>/agregar_detalle", methods=["POST"])
@login_required
def agregar_detalle_pedido(pedido_id):
    try:
        data = request.get_json()
        
        producto_id = data.get("producto_id")
        cantidad = data.get("cantidad")
        subtotal = data.get("subtotal")
        
        # Validar campos requeridos - SIN precio_unitario
        if not all([producto_id, cantidad, subtotal]):
            return jsonify({"error": "Todos los campos son requeridos"}), 400
        
        cursor = mysql.connection.cursor()
        
        # Verificar que el pedido existe
        cursor.execute("SELECT id_pedido FROM pedidos WHERE id_pedido = %s", (pedido_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": "Pedido no encontrado"}), 404
        
        # CONSULTA CORREGIDA - sin precio_unitario
        cursor.execute("""
            INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, subtotal)
            VALUES (%s, %s, %s, %s)
        """, (pedido_id, producto_id, cantidad, subtotal))
        
        detalle_id = cursor.lastrowid
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            "mensaje": "Detalle de pedido creado correctamente",
            "id_detalle": detalle_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error en agregar_detalle_pedido: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500
# ==================== ENDPOINTS PÚBLICOS (Landing Page) ====================

@pedidos_bp.route("/public", methods=["OPTIONS"])
@pedidos_bp.route("/public/mis-pedidos", methods=["OPTIONS"])
@pedidos_bp.route("/public/login", methods=["OPTIONS"])
@pedidos_bp.route("/public/registro", methods=["OPTIONS"])
@pedidos_bp.route("/public/logout", methods=["OPTIONS"])
def handle_public_options():
    return jsonify({"status": "ok"}), 200


@pedidos_bp.route("/public", methods=["POST"])
def create_pedido_public():
    """
    Guarda un pedido desde la landing page.
    Acepta usuario anónimo (usuario_id = None) o autenticado por token de sesión.
    Body: { usuario_id, telefono, direccion, total, items: [{id_producto, nombre, cantidad, precio, subtotal}] }
    """
    try:
        data = request.get_json()
        usuario_id = data.get("usuario_id")   # None si es anónimo
        telefono   = data.get("telefono", "")
        direccion  = data.get("direccion", "")
        total      = data.get("total", 0)
        items      = data.get("items", [])

        if not items:
            return jsonify({"error": "El carrito está vacío"}), 400

        cursor = mysql.connection.cursor()

        # Insertar pedido
        cursor.execute("""
            INSERT INTO pedidos (usuario_id, telefono, direccion, total, estado, fecha_pedido)
            VALUES (%s, %s, %s, %s, 'pendiente', NOW())
        """, (usuario_id, telefono, direccion, total))

        pedido_id = cursor.lastrowid

        # Insertar detalle por cada item del carrito
        for item in items:
            producto_id = item.get("id_producto")
            cantidad    = item.get("cantidad", 1)
            precio      = item.get("precio", 0)
            subtotal    = item.get("subtotal", precio * cantidad)

            if not producto_id:
                continue

            cursor.execute("""
                INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (pedido_id, producto_id, cantidad, precio, subtotal))

        mysql.connection.commit()
        cursor.close()

        logger.info(f"Pedido público creado: ID {pedido_id}")
        return jsonify({
            "mensaje": "Pedido registrado correctamente",
            "id_pedido": pedido_id
        }), 201

    except Exception as e:
        logger.error(f"Error en create_pedido_public: {str(e)}")
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500


@pedidos_bp.route("/public/login", methods=["POST"])
def login_cliente():
    """Login de clientes desde la landing page."""
    from models import User
    from flask_login import login_user
    data = request.get_json()
    email    = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    user = User.get_by_email(email)
    if user and user.check_password(password):
        if user.rol != 'cliente':
            return jsonify({"error": "Acceso no permitido"}), 403
        login_user(user)
        return jsonify({
            "mensaje": "Login exitoso",
            "usuario": {
                "id": user.id,
                "nombre": user.nombre,
                "email": user.email,
                "telefono": user.telefono,
                "direccion": user.direccion
            }
        })
    return jsonify({"error": "Credenciales inválidas"}), 401


@pedidos_bp.route("/public/registro", methods=["POST"])
def registro_cliente():
    """Registro de nuevos clientes desde la landing page."""
    from werkzeug.security import generate_password_hash
    data = request.get_json()

    nombre    = data.get("nombre")
    email     = data.get("email")
    password  = data.get("password")
    telefono  = data.get("telefono", "")
    direccion = data.get("direccion", "")

    if not nombre or not email or not password:
        return jsonify({"error": "Nombre, email y contraseña son requeridos"}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        return jsonify({"error": "El email ya está registrado"}), 400

    hashed = generate_password_hash(password)
    cursor.execute("""
        INSERT INTO usuarios (nombre, email, password, telefono, direccion, rol, fecha_registro)
        VALUES (%s, %s, %s, %s, %s, 'cliente', NOW())
    """, (nombre, email, hashed, telefono, direccion))

    mysql.connection.commit()
    cursor.close()

    return jsonify({"mensaje": "Registro exitoso. Ya puedes iniciar sesión."}), 201


@pedidos_bp.route("/public/logout", methods=["POST"])
def logout_cliente():
    from flask_login import logout_user
    logout_user()
    return jsonify({"mensaje": "Sesión cerrada"})


@pedidos_bp.route("/public/mis-pedidos", methods=["GET"])
def mis_pedidos():
    """Devuelve el historial de pedidos del cliente logueado."""
    from flask_login import current_user
    if not current_user.is_authenticated:
        return jsonify({"error": "No autenticado"}), 401

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT p.id_pedido, p.fecha_pedido, p.total, p.estado,
                   COUNT(dp.id_detalle) as total_productos
            FROM pedidos p
            LEFT JOIN detalle_pedidos dp ON p.id_pedido = dp.pedido_id
            WHERE p.usuario_id = %s
            GROUP BY p.id_pedido
            ORDER BY p.fecha_pedido DESC
        """, (current_user.id,))
        filas = cursor.fetchall()

        pedidos = []
        for f in filas:
            # Obtener detalle de cada pedido
            cursor.execute("""
                SELECT dp.cantidad, dp.precio_unitario, dp.subtotal,
                       pr.nombre, pr.imagen
                FROM detalle_pedidos dp
                LEFT JOIN productos pr ON dp.producto_id = pr.id_producto
                WHERE dp.pedido_id = %s
            """, (f[0],))
            detalles_raw = cursor.fetchall()
            detalles = [{
                "cantidad": d[0],
                "precio_unitario": float(d[1]) if d[1] else 0,
                "subtotal": float(d[2]) if d[2] else 0,
                "nombre": d[3],
                "imagen": d[4]
            } for d in detalles_raw]

            pedidos.append({
                "id_pedido": f[0],
                "fecha_pedido": f[1].strftime('%Y-%m-%d %H:%M') if f[1] else None,
                "total": float(f[2]) if f[2] else 0,
                "estado": f[3] or "pendiente",
                "total_productos": f[4],
                "detalles": detalles
            })

        cursor.close()
        return jsonify({"pedidos": pedidos})

    except Exception as e:
        logger.error(f"Error en mis_pedidos: {str(e)}")
        return jsonify({"error": str(e)}), 500