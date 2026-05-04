import os
from db import get_db_connection
from werkzeug.security import generate_password_hash

def reset_database():
    # Establecer conexión
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*40)
    print("🧹 INICIANDO LIMPIEZA PROFUNDA DE SWEETLAND")
    print("="*40)
    
    try:
        # 1. Desactivar revisión de llaves foráneas para limpiar sin errores de dependencia
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # 2. Lista de tablas a vaciar
        tablas = [
            "detalle_pedidos", 
            "recetas", 
            "recetas_empaques", 
            "pedidos", 
            "productos", 
            "ingredientes", 
            "empaques", 
            "usuarios"
        ]
        
        for tabla in tablas:
            print(f"🗑️ Limpiando tabla: {tabla}...")
            # TRUNCATE vacía la tabla y reinicia los contadores (IDs vuelven a 1)
            cursor.execute(f"TRUNCATE TABLE {tabla}")
        
        # 3. Reactivar revisión de llaves foráneas
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # 4. MODIFICACIÓN DE ESTRUCTURA (Preparando para el Control de Stock)
        print("\n🛠️ Preparando tabla 'productos' para el control de inventario...")
        try:
            # Agregamos stock (cantidad) y controla_stock (si queremos que descuente o no)
            cursor.execute("ALTER TABLE productos ADD COLUMN stock INT DEFAULT 0")
            cursor.execute("ALTER TABLE productos ADD COLUMN controla_stock BOOLEAN DEFAULT FALSE")
            print("✅ Columnas de inventario añadidas correctamente.")
        except Exception:
            print("ℹ️ Las columnas de stock ya existían, omitiendo paso.")

        # 5. CREAR EL ADMINISTRADOR MAESTRO (Seguridad con Hashing)
        # Puedes cambiar estos datos antes de ejecutar si lo deseas
        admin_email = "admin@sweetland.com"
        admin_pass  = "Sweetland2026*"
        hashed_pw   = generate_password_hash(admin_pass)
        
        print(f"\n🔑 Creando usuario Administrador: {admin_email}...")
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, rol)
            VALUES (%s, %s, %s, %s)
        """, ("Administrador Maestro", admin_email, hashed_pw, "admin"))
        
        # Guardar cambios
        conn.commit()
        
        print("\n" + "="*40)
        print("🎉 ¡BASE DE DATOS LIMPIA Y LISTA PARA PRODUCCIÓN!")
        print(f"👤 Usuario: {admin_email}")
        print(f"🔒 Password: {admin_pass}")
        print("="*40)
        print("⚠️ IMPORTANTE: Por seguridad, elimina este archivo después de usarlo.")

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO DURANTE EL RESET: {str(e)}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Si lo corres manual pide SI
    confirm = input("¿Confirmas borrado total? (SI): ")
    if confirm == "SI":
        reset_database()
else:
    # Si lo llama app.py (import), corre directo
    reset_database()