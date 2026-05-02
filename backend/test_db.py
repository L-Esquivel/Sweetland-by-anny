import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Root1234",
        database="sweetland_by_anny"
    )
    print("✅ Conexión exitosa!")
    conn.close()
except Exception as e:
    print("❌ Error:", e)