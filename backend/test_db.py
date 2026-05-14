import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("Attempting to connect to the PostgreSQL database on Render...")

db_url = os.getenv('DATABASE_URL')

if not db_url:
    print("\n❌ ERROR: DATABASE_URL not found in your .env file.")
    print("Please make sure your backend/.env file contains the correct URL from Render.")
else:
    print(f"Connecting using the provided DATABASE_URL...")
    try:
        # psycopg2 can connect directly using the URL
        conn = psycopg2.connect(db_url)
        print("\n✅ DATABASE CONNECTION SUCCESSFUL! ✅")
        
        # Simple query test
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            print("PostgreSQL version:", db_version[0])

        conn.close()
        print("\nConnection closed successfully.")

    except psycopg2.OperationalError as e:
        print(f"\n❌ CONNECTION ERROR: {e}")
        print("\nPossible causes:")
        print("1. The DATABASE_URL in your .env file is incorrect.")
        print("2. Your local machine's IP is not whitelisted in Render's network settings (check 'Access' tab).")
        print("3. The Render database service is not running or is still starting up.")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")