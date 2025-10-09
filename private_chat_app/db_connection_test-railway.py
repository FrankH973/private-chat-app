# test_db_connection.py
# Place this file in your project root: C:\private_chat_app\private_chat_app\test_db_connection.py
# Run with: python test_db_connection.py

import psycopg2
from decouple import config

def test_database_connection():
    """Test connection to your PostgreSQL database"""
    
    print("=" * 50)
    print("Testing Railway Database Connection...")
    print("=" * 50)
    
    # Get credentials from .env file
    db_config = {
        'dbname': config('DB_NAME'),
        'user': config('DB_USER'),
        'password': config('DB_PASSWORD'),
        'host': config('DB_HOST'),
        'port': config('DB_PORT', default='5432'),
    }
    
    print(f"\nConnection Details:")
    print(f"  Host: {db_config['host']}")
    print(f"  Port: {db_config['port']}")
    print(f"  Database: {db_config['dbname']}")
    print(f"  User: {db_config['user']}")
    print(f"  Password: {'*' * len(db_config['password'])}")
    
    try:
        # Railway usually doesn't require SSL, but let's try both
        print("\n[Attempt 1] Connecting to Railway...")
        conn = psycopg2.connect(**db_config)
        
        # Create a cursor to execute queries
        cursor = conn.cursor()
        
        # Test query
        cursor.execute('SELECT version();')
        db_version = cursor.fetchone()
        
        print("\n✅ SUCCESS! Railway database connection established!")
        print(f"\nPostgreSQL Version:")
        print(f"  {db_version[0]}")
        
        # Close connections
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 50)
        print("✅ Connection test PASSED!")
        print("Ready to run Django migrations!")
        print("=" * 50)
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection failed")
        print(f"Error: {str(e)}")
        print("\n" + "=" * 50)
        print("TROUBLESHOOTING:")
        print("=" * 50)
        print("1. Verify your Railway database is running")
        print("2. Check credentials in Railway dashboard")
        print("3. Make sure .env file is in the correct location")
        return False
            
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    test_database_connection()