import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("Attempting to connect to the PostgreSQL database...")

db_url = os.getenv('DATABASE_URL')

if not db_url:
    print("\n❌ ERROR: The DATABASE_URL was not found in your .env file.")
    print("Please make sure your backend/.env file contains the correct database connection URL.")
else:
    print(f"Connecting using the provided DATABASE_URL...")
    try:
        # psycopg2 can connect directly using the URL
        conn = psycopg2.connect(db_url)
        print("\n✅ DATABASE CONNECTION SUCCESSFUL! ✅\n")
        
        # Simple query test
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            print(f"PostgreSQL version: {db_version[0]}")

        conn.close()
        print("\nConnection closed successfully.")

    except psycopg2.OperationalError as e:
        print(f"\n❌ CONNECTION FAILED: {e}")
        print("\nPossible causes:")
        print("1. The DATABASE_URL in your .env file is incorrect.")
        print("2. Your local machine's IP is not whitelisted in your cloud provider's network settings (e.g., Render's 'Access' tab).")
        print("3. The database service is not running or is still starting up.")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")