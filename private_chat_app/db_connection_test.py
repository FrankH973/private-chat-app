# test_db_connection.py
# Place this file in your project root: C:\Users\frank\private_chat_app\test_db_connection.py
# Run with: python test_db_connection.py

import psycopg2
from decouple import config

def test_database_connection():
    """Test connection to your PostgreSQL database"""
    
    print("=" * 50)
    print("Testing Database Connection...")
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
        # Test without SSL first
        print("\n[Attempt 1] Connecting without SSL...")
        conn = psycopg2.connect(**db_config)
        
        # Create a cursor to execute queries
        cursor = conn.cursor()
        
        # Test query
        cursor.execute('SELECT version();')
        db_version = cursor.fetchone()
        
        print("\n✅ SUCCESS! Database connection established!")
        print(f"\nPostgreSQL Version:")
        print(f"  {db_version[0]}")
        
        # Close connections
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 50)
        print("Connection test PASSED!")
        print("You can now run Django migrations.")
        print("=" * 50)
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection failed (without SSL)")
        print(f"Error: {str(e)}")
        
        # Try with SSL
        try:
            print("\n[Attempt 2] Trying with SSL required...")
            db_config['sslmode'] = 'require'
            conn = psycopg2.connect(**db_config)
            
            cursor = conn.cursor()
            cursor.execute('SELECT version();')
            db_version = cursor.fetchone()
            
            print("\n✅ SUCCESS! Database connection established with SSL!")
            print(f"\nPostgreSQL Version:")
            print(f"  {db_version[0]}")
            
            cursor.close()
            conn.close()
            
            print("\n⚠️  NOTE: Your database requires SSL.")
            print("Update your .env file: DB_REQUIRE_SSL=True")
            print("\n" + "=" * 50)
            print("Connection test PASSED!")
            print("=" * 50)
            return True
            
        except psycopg2.OperationalError as e2:
            print(f"\n❌ Connection also failed with SSL")
            print(f"Error: {str(e2)}")
            print("\n" + "=" * 50)
            print("TROUBLESHOOTING TIPS:")
            print("=" * 50)
            print("1. Check if the hostname is correct: ww.zmaxus.com")
            print("   (Did you mean www.zmaxus.com?)")
            print("2. Verify your database credentials in cPanel/hosting panel")
            print("3. Check if port 5432 is open on your server")
            print("4. Ensure remote database connections are enabled")
            print("5. Check firewall settings on your hosting provider")
            print("6. Verify the database actually exists on the server")
            return False
            
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    test_database_connection()