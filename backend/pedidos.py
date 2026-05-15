from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from utils import admin_required, registrar_log # 🛡️ Importamos la auditoría
from db import get_db # 🟢 Importamos el nuevo gestor de DB
from psycopg2.extras import DictCursor # 🟢 Para obtener resultados como diccionarios
import logging, datetime

logger = logging.getLogger(__name__)

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")

# ==================== LÓGICA DE STOCK ====================

def procesar_descuento_stock(cursor, pedido_id, tenant_id):
    """Resta unidades del inventario basándose en el detalle del pedido."""
    try:
        # Esta función es llamada desde otra que ya maneja el commit/rollback,
        # por lo que no hacemos commit aquí para mantener la atomicidad.
        cursor.execute("SELECT producto_id, cantidad FROM detalle_pedidos WHERE pedido_id = %s AND tenant_id = %s", (pedido_id, tenant_id))
        items = cursor.fetchall()
        for item in items:
            cursor.execute("""
                UPDATE productos SET stock = stock - %s 
                WHERE id_producto = %s AND controla_stock = TRUE AND tenant_id = %s
            """, (item['cantidad'], item['producto_id'], tenant_id))
    except Exception as e:
        logger.error(f"Error descontando stock: {e}")
        # Propagamos la excepción para que la función llamadora haga rollback.
        raise

# ==================== STATS (Dashboard) ====================

@pedidos_bp.route("/stats", methods=["GET"])
@admin_required
def get_stats():
    tenant_id = current_user.tenant_id
    conn = get_db()
    cursor = conn.cursor(cursor_factory=DictCursor)
    try:
        # 1. Obtener y validar rango de fechas (default: últimos 30 días)
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=29)

        fecha_inicio_str = request.args.get('fecha_inicio', start_date.strftime('%Y-%m-%d'))
        fecha_fin_str = request.args.get('fecha_fin', end_date.strftime('%Y-%m-%d'))
        params_with_tenant = (tenant_id, fecha_inicio_str, fecha_fin_str)

        # 2. Resumen financiero para el rango
        # 💡 SAAS-IFICATION: Todas las consultas ahora filtran por tenant_id.
        where_pedidos = " WHERE tenant_id = %s AND estado != 'cancelado' AND DATE(fecha_pedido) BETWEEN %s AND %s "
        cursor.execute(f"""
            SELECT 
                SUM(total) as total_ventas_rango,
                COUNT(id_pedido) as num_pedidos_rango
            FROM pedidos {where_pedidos}
        """, params_with_tenant)
        resumen_rango_raw = cursor.fetchone()
        resumen = {
            'total_ventas_rango': float(resumen_rango_raw.get('total_ventas_rango') or 0),
            'num_pedidos_rango': int(resumen_rango_raw.get('num_pedidos_rango') or 0)
        }
        
        # 3. Sumar gastos en el mismo rango de fechas
        cursor.execute("""
            SELECT SUM(monto) as total_gastos_rango
            FROM gastos WHERE tenant_id = %s AND fecha BETWEEN %s AND %s
        """, params_with_tenant)
        gastos_rango_raw = cursor.fetchone()
        resumen['total_gastos_rango'] = float(gastos_rango_raw.get('total_gastos_rango') or 0)

        # 4. Sumar merma en el mismo rango de fechas
        cursor.execute("""
            SELECT SUM(costo_perdida) as total_merma_rango
            FROM merma WHERE tenant_id = %s AND fecha BETWEEN %s AND %s
        """, params_with_tenant)
        merma_rango_raw = cursor.fetchone()
        resumen['total_merma_rango'] = float(merma_rango_raw.get('total_merma_rango') or 0)

        # 5. Datos para la gráfica para el rango
        cursor.execute(f"""
            SELECT DATE(fecha_pedido) as fecha, SUM(total) as venta 
            FROM pedidos {where_pedidos}
            GROUP BY DATE(fecha_pedido) ORDER BY fecha ASC
        """, params_with_tenant)
        grafica_raw = cursor.fetchall()
        grafica = [{"fecha": str(row['fecha']), "venta": float(row['venta'])} for row in grafica_raw]

        # 6. Pedidos por estado para el rango
        cursor.execute(f"SELECT estado, COUNT(id_pedido) as cantidad FROM pedidos {where_pedidos} GROUP BY estado", params_with_tenant)
        estados_raw = cursor.fetchall()
        pedidos_por_estado = {row['estado']: row['cantidad'] for row in estados_raw}

        # 7. Producto Top para el rango
        where_pedidos_aliased = " WHERE ped.tenant_id = %s AND ped.estado = 'completado' AND DATE(ped.fecha_pedido) BETWEEN %s AND %s "
        cursor.execute(f"""
            SELECT p.nombre, p.precio, SUM(dp.cantidad) as total_vendido
            FROM detalle_pedidos dp
            JOIN productos p ON dp.producto_id = p.id_producto
            JOIN pedidos ped ON dp.pedido_id = ped.id_pedido
            {where_pedidos_aliased}
            GROUP BY p.id_producto
            ORDER BY total_vendido DESC LIMIT 1
        """, params_with_tenant)
        producto_top_raw = cursor.fetchone()
        producto_top = None
        if producto_top_raw:
            producto_top = {
                "nombre": producto_top_raw['nombre'],
                "precio": float(producto_top_raw['precio']),
                "total_vendido": int(producto_top_raw['total_vendido'])
            }

        return jsonify({
            "resumen": resumen, 
            "grafica": grafica, 
            "pedidos_por_estado": pedidos_por_estado, 
            "producto_top": producto_top,
            "filtros_aplicados": {"fecha_inicio": fecha_inicio_str, "fecha_fin": fecha_fin_str}
        })
    except Exception as e:
        current_app.logger.error(f"Error en get_stats: {e}")
        return jsonify({"error": "Error al obtener estadísticas"}), 500

# ==================== GESTIÓN ADMIN ====================

@pedidos_bp.route("/", methods=["GET"])
@login_required
def get_pedidos():
    tenant_id = current_user.tenant_id
    conn = get_db()
    cursor = conn.cursor(cursor_factory=DictCursor)
    try:
        cursor.execute("""
            SELECT p.*, u.nombre as cliente_nombre, u.telefono as cliente_telefono 
            FROM pedidos p LEFT JOIN usuarios u ON p.usuario_id = u.id_usuario 
            WHERE p.tenant_id = %s
            ORDER BY p.fecha_pedido DESC
        """, (tenant_id,))
        pedidos = [dict(row) for row in cursor.fetchall()]
        # Formateo de datos para el frontend
        for p in pedidos:
            p['id_pedido'] = p.get('id_pedido') 
            p['total'] = float(p.get('total') or 0)
            if p.get('fecha_pedido'): 
                p['fecha_pedido'] = p['fecha_pedido'].strftime('%Y-%m-%d %H:%M')
        return jsonify(pedidos)
    except Exception as e:
        current_app.logger.error(f"Error en get_pedidos: {e}")
        return jsonify({"error": "Error al obtener pedidos"}), 500

@pedidos_bp.route("/", methods=["POST"])
@admin_required
def create_pedido_admin():
    """
    Permite a un administrador crear un nuevo pedido manualmente.
    Calcula el total en el backend para seguridad.
    """
    data = request.get_json()
    tenant_id = current_user.tenant_id
    conn = get_db()

    items = data.get("items", [])
    if not items:
        return jsonify({"error": "El pedido debe tener al menos un producto"}), 400

    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # 1. Calcular el total del pedido desde el backend para evitar manipulación de precios.
            total_pedido = 0
            productos_a_insertar = []
            for item in items:
                producto_id = item.get("producto_id")
                cantidad = item.get("cantidad")
                if not producto_id or not cantidad or int(cantidad) <= 0:
                    continue # Ignorar items inválidos

                cursor.execute("SELECT precio FROM productos WHERE id_producto = %s AND tenant_id = %s", (producto_id, tenant_id))
                producto_data = cursor.fetchone()
                if not producto_data:
                    raise ValueError(f"Uno de los productos seleccionados (ID: {producto_id}) no fue encontrado.")
                
                precio_unitario = float(producto_data['precio'] or 0)
                subtotal = precio_unitario * int(cantidad)
                total_pedido += subtotal
                productos_a_insertar.append({
                    "producto_id": producto_id,
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "subtotal": subtotal
                })
            
            if not productos_a_insertar:
                return jsonify({"error": "No se proporcionaron productos válidos en el pedido"}), 400

            # 2. Insertar el pedido principal. Asume que la tabla 'pedidos' tiene una columna 'cliente_nombre'.
            cursor.execute("""
                INSERT INTO pedidos (usuario_id, cliente_nombre, telefono, direccion, total, estado, tenant_id)
                VALUES (%s, %s, %s, %s, %s, 'pendiente', %s)
                RETURNING id_pedido
            """, (
                data.get("usuario_id"), 
                data.get("cliente_nombre"), 
                data.get("telefono"), 
                data.get("direccion"), 
                total_pedido, 
                tenant_id
            ))
            pedido_id = cursor.fetchone()[0]

            # 3. Insertar los detalles del pedido.
            for prod in productos_a_insertar:
                cursor.execute("INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, precio_unitario, subtotal, tenant_id) VALUES (%s, %s, %s, %s, %s, %s)",
                               (pedido_id, prod['producto_id'], prod['cantidad'], prod['precio_unitario'], prod['subtotal'], tenant_id))
            
            conn.commit()
            registrar_log(f"Admin creó nuevo pedido ID {pedido_id}")
            return jsonify({"mensaje": "Pedido creado con éxito", "id_pedido": pedido_id}), 201

    except ValueError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error en create_pedido_admin: {e}", exc_info=True)
        return jsonify({"error": "Error interno al crear el pedido"}), 500

@pedidos_bp.route("/<int:id>/estado", methods=["PUT"])
@admin_required # FIX: Se añade decorador de seguridad. Solo admins pueden cambiar el estado.
def update_estado_pedido(id):
    data = request.get_json()
    nuevo_estado = data.get("estado")
    tenant_id = current_user.tenant_id
    conn = get_db()
    cursor = conn.cursor(cursor_factory=DictCursor)
    try:
        cursor.execute("SELECT estado FROM pedidos WHERE id_pedido = %s AND tenant_id = %s", (id, tenant_id))
        actual = cursor.fetchone()
        if not actual: return jsonify({"error": "No existe"}), 404

        if nuevo_estado == 'completado' and actual.get('estado') != 'completado':
            procesar_descuento_stock(cursor, id, tenant_id)

        cursor.execute("UPDATE pedidos SET estado=%s WHERE id_pedido=%s AND tenant_id = %s", (nuevo_estado, id, tenant_id))
        conn.commit()

        # 🛡️ LOG: Seguimiento de estado de pedido
        registrar_log(f"Actualizó estado pedido #{id} de '{actual.get('estado')}' a '{nuevo_estado}'")

        return jsonify({"mensaje": "Actualizado", "estado": nuevo_estado})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error en update_estado_pedido: {e}", exc_info=True)
        return jsonify({"error": "Error al actualizar el estado del pedido"}), 500

@pedidos_bp.route("/<int:id>", methods=["DELETE"])
@admin_required
def delete_pedido(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM detalle_pedidos WHERE pedido_id = %s AND tenant_id = %s", (id, tenant_id))
        cursor.execute("DELETE FROM pedidos WHERE id_pedido = %s AND tenant_id = %s", (id, tenant_id))
        conn.commit()

        # 🛡️ LOG: Eliminación de pedido
        registrar_log(f"Eliminó permanentemente el pedido ID {id}")

        return jsonify({"mensaje": "Pedido eliminado correctamente"})
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error en delete_pedido: {e}", exc_info=True)
        return jsonify({"error": "Error al eliminar el pedido"}), 500

@pedidos_bp.route("/<int:id>/detalles", methods=["GET"])
@login_required
def get_detalles_admin(id):
    tenant_id = current_user.tenant_id
    conn = get_db()
    cursor = conn.cursor(cursor_factory=DictCursor)
    try:
        # Esta ruta es ahora redundante con /detalle_pedidos/pedido/<id>, pero la mantenemos por retrocompatibilidad
        cursor.execute("""
            SELECT dp.*, p.nombre as producto_nombre 
            FROM detalle_pedidos dp JOIN productos p ON dp.producto_id = p.id_producto
            WHERE dp.pedido_id = %s AND dp.tenant_id = %s
        """, (id, tenant_id))
        detalles = [dict(d) for d in cursor.fetchall()]
        for d in detalles:
            d['subtotal'] = float(d['subtotal'] or 0)
            d['precio_unitario'] = float(d.get('precio_unitario') or 0)
        return jsonify(detalles)
    except Exception as e:
        current_app.logger.error(f"Error en get_detalles_admin: {e}")
        return jsonify({"error": "Error al obtener detalles"}), 500

# ==================== ENDPOINTS PÚBLICOS 🌍 ====================

@pedidos_bp.route("/public", methods=["POST"])
def create_pedido_public():
    data = request.get_json()
    # 💡 SAAS-IFICATION: Los pedidos públicos se asocian al tenant público.
    tenant_id_publico = os.getenv('PUBLIC_TENANT_ID', 1)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO pedidos (usuario_id, telefono, direccion, total, estado, tenant_id)
            VALUES (%s, %s, %s, %s, 'pendiente', %s)
            RETURNING id_pedido
        """, (data.get("usuario_id"), data.get("telefono"), data.get("direccion"), data.get("total", 0), tenant_id_publico))
        pedido_id = cursor.fetchone()[0]

        for item in data.get("items", []):
            cursor.execute("""
                INSERT INTO detalle_pedidos (pedido_id, producto_id, cantidad, precio_unitario, subtotal, tenant_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (pedido_id, item.get("id_producto"), item.get("cantidad"), item.get("precio"), item.get("subtotal"), tenant_id_publico))
        conn.commit()

        # 🛡️ LOG: Nuevo pedido entrante
        registrar_log(f"Recibió nuevo pedido web: ID #{pedido_id}")

        return jsonify({"mensaje": "Pedido recibido", "id_pedido": pedido_id}), 201
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error en create_pedido_public: {e}", exc_info=True)
        return jsonify({"error": "Error al procesar el pedido"}), 500

@pedidos_bp.route("/public/mis-pedidos", methods=["GET"])
@login_required
def mis_pedidos():
    tenant_id = current_user.tenant_id
    conn = get_db()
    cursor = conn.cursor(cursor_factory=DictCursor)
    try:
        # Esta ruta ya fue optimizada para evitar N+1, solo se cambia la conexión
        # 1. Obtener todos los pedidos del usuario (1ª consulta)
        cursor.execute("SELECT * FROM pedidos WHERE usuario_id = %s AND tenant_id = %s ORDER BY fecha_pedido DESC", (current_user.id, tenant_id))
        pedidos = [dict(p) for p in cursor.fetchall()]

        if not pedidos:
            return jsonify({"pedidos": []})

        # 2. Obtener TODOS los detalles para ESOS pedidos en una sola consulta (2ª consulta)
        pedido_ids = [p['id_pedido'] for p in pedidos]
        placeholders = ','.join(['%s'] * len(pedido_ids))
        cursor.execute(f"""
            SELECT dp.pedido_id, dp.cantidad, dp.subtotal, pr.nombre 
            FROM detalle_pedidos dp JOIN productos pr ON dp.producto_id = pr.id_producto
            WHERE dp.pedido_id IN ({placeholders}) AND dp.tenant_id = %s
        """, tuple(pedido_ids) + (tenant_id,))
        detalles_todos = cursor.fetchall()

        # 3. Mapear los detalles a sus pedidos correspondientes en Python (muy rápido)
        detalles_por_pedido = {}
        for detalle in detalles_todos:
            pedido_id = detalle['pedido_id']
            if pedido_id not in detalles_por_pedido:
                detalles_por_pedido[pedido_id] = []
            detalles_por_pedido[pedido_id].append({
                "nombre": detalle['nombre'], "cantidad": detalle['cantidad'], "subtotal": float(detalle['subtotal'])
            })

        # 4. Combinar los datos
        for p in pedidos:
            p['total'] = float(p['total'] or 0)
            p['fecha_pedido'] = p['fecha_pedido'].strftime('%Y-%m-%d %H:%M') if p['fecha_pedido'] else ""
            p['detalles'] = detalles_por_pedido.get(p['id_pedido'], [])
        return jsonify({"pedidos": pedidos})
    except Exception as e:
        current_app.logger.error(f"Error en mis_pedidos: {e}")
        return jsonify({"error": "Error al obtener tus pedidos"}), 500