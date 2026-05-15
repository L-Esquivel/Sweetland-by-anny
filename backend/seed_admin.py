import os
import psycopg2
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import getpass # To hide password input

# --- Configuration ---
# Load environment variables from .env file in the current directory
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

def create_admin_user():
    """
    Connects to the database and inserts a new tenant and a new admin user.
    """
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL environment variable not found.")
        print("Please ensure you have a .env file with the correct database URL.")
        return

    conn = None
    try:
        # --- Get User Info ---
        print("--- Creating a new Admin User ---")
        admin_name = input("Enter admin's full name: ")
        admin_email = input("Enter admin's email address: ")
        # Use getpass to securely ask for the password without showing it on screen
        admin_password = getpass.getpass("Enter admin's password: ")
        
        role_input = ""
        while role_input not in ['admin', 'superadmin']:
            role_input = input("Enter role ('admin' or 'superadmin'): ").lower()
            if role_input not in ['admin', 'superadmin']:
                print("❌ Invalid role. Please enter 'admin' or 'superadmin'.")
        
        admin_role = role_input

        if not all([admin_name, admin_email, admin_password]):
            print("\n❌ Error: Name, email, and password cannot be empty.")
            return

        # Hash the password
        hashed_password = generate_password_hash(admin_password)

        # --- Database Operations ---
        print("\nConnecting to the database...")
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Connection successful.")

        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # 1. Create a new Tenant first
            # 💡 MEJORA: Lógica diferenciada para superadmin y admin normal.
            if admin_role == 'superadmin':
                tenant_name = "Precivox Platform" # Nombre fijo para el tenant de la plataforma.
            else: # Es un 'admin'
                tenant_name = input("Enter the organization's name (e.g., Sweetland): ")
                if not tenant_name:
                    print("\n❌ Error: Organization name cannot be empty for an 'admin' role.")
                    return
            
            # Buscamos si el tenant ya existe para reutilizarlo, si no, lo creamos.
            cursor.execute("SELECT id_tenant FROM tenants WHERE nombre = %s", (tenant_name,))
            tenant_row = cursor.fetchone()

            if tenant_row:
                tenant_id = tenant_row[0]
                print(f"✅ Using existing tenant '{tenant_name}' with ID: {tenant_id}")
            else:
                print(f"Creating new tenant: '{tenant_name}'...")
                cursor.execute("INSERT INTO tenants (nombre) VALUES (%s) RETURNING id_tenant", (tenant_name,))
                tenant_id = cursor.fetchone()[0]
                print(f"✅ Tenant created with ID: {tenant_id}")

            # 2. Create the Admin User associated with the new tenant
            print(f"Creating user '{admin_email}' with role '{admin_role}' for tenant ID {tenant_id}...")
            cursor.execute(
                """
                INSERT INTO usuarios (nombre, email, password, rol, tenant_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (admin_name, admin_email, hashed_password, admin_role, tenant_id)
            )

            # 3. Populate default module settings for the new tenant
            cursor.execute("SELECT module_key, label FROM modules")
            all_modules = cursor.fetchall()
            if all_modules:
                settings_to_insert = [(tenant_id, m['module_key'], m['label']) for m in all_modules]
                args_str = ','.join(cursor.mogrify("(%s,%s,%s)", s).decode('utf-8') for s in settings_to_insert)
                cursor.execute("INSERT INTO tenant_module_settings (tenant_id, module_key, custom_label) VALUES " + args_str)
                print(f"✅ Default module settings created for tenant ID: {tenant_id}")

            conn.commit()
            print("\n🎉 Success! User and tenant have been created in the database.")
            print("You can now log in to the admin panel with these credentials.")

    except psycopg2.errors.UniqueViolation:
        print(f"\n❌ Error: The email '{admin_email}' already exists in the database.")
        if conn: conn.rollback()
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        if conn: conn.rollback()
    finally:
        if conn:
            conn.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    create_admin_user()