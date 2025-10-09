# test_direct_ipv6.py
# Test connection using direct IPv6 address (no DNS lookup needed)
# Place in: C:\private_chat_app\test_direct_ipv6.py
# Run with: python test_direct_ipv6.py

import socket
import psycopg2
from decouple import config

def test_ipv6_socket():
    """Test raw socket connection to IPv6 address"""
    print("=" * 60)
    print("Testing Direct IPv6 Socket Connection")
    print("=" * 60)
    
    ipv6_address = "2600:1f1c:f9:4d07:becb:d9d2:a2c6:3a46"
    port = 5432
    
    print(f"\nTarget IPv6: [{ipv6_address}]:{port}")
    
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((ipv6_address, port))
        print("✅ Socket connection successful!")
        sock.close()
        return True
    except Exception as e:
        print(f"❌ Socket connection failed: {e}")
        return False

def test_psycopg2_connection():
    """Test PostgreSQL connection using psycopg2"""
    print("\n" + "=" * 60)
    print("Testing PostgreSQL Connection with psycopg2")
    print("=" * 60)
    
    ipv6_address = "2600:1f1c:f9:4d07:becb:d9d2:a2c6:3a46"
    
    db_config = {
        'dbname': 'postgres',
        'user': 'postgres',
        'password': config('DB_PASSWORD'),
        'host': ipv6_address,
        'port': '5432',
        'sslmode': 'require',
        'connect_timeout': 10
    }
    
    print(f"\nConnection details:")
    print(f"  Host: [{ipv6_address}]")
    print(f"  Port: 5432")
    print(f"  Database: postgres")
    print(f"  User: postgres")
    print(f"  SSL: Required")
    
    try:
        print("\n[Connecting...]")
        conn = psycopg2.connect(**db_config)
        
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        
        cursor.execute('SELECT current_database(), current_user;')
        db_name, user = cursor.fetchone()
        
        print("\n✅ PostgreSQL connection SUCCESSFUL!")
        print(f"\nDatabase Info:")
        print(f"  PostgreSQL: {version[:60]}...")
        print(f"  Database: {db_name}")
        print(f"  User: {user}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ PostgreSQL connection FAILED!")
        print(f"Error: {str(e)}")
        return False

def main():
    print("\n" + "=" * 60)
    print("  Direct IPv6 Connection Test (No DNS Required)")
    print("=" * 60)
    print("\nThis test uses the IPv6 address directly,")
    print("bypassing all DNS resolution issues.\n")
    
    # Test 1: Raw socket
    socket_ok = test_ipv6_socket()
    
    # Test 2: PostgreSQL
    if socket_ok:
        psycopg2_ok = test_psycopg2_connection()
    else:
        print("\n⚠️  Skipping PostgreSQL test (socket connection failed)")
        psycopg2_ok = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"IPv6 Socket:      {'✅ PASS' if socket_ok else '❌ FAIL'}")
    print(f"PostgreSQL:       {'✅ PASS' if psycopg2_ok else '❌ FAIL'}")
    
    if psycopg2_ok:
        print("\n" + "🎉" * 30)
        print("\n  SUCCESS! Your database connection works!")
        print("\n" + "🎉" * 30)
        print("\nYour .env is now configured with the direct IPv6 address.")
        print("\nNext steps:")
        print("  1. Run: python manage.py check")
        print("  2. Run: python manage.py migrate")
        print("  3. Run: python manage.py createsuperuser")
        print("  4. Run: python manage.py runserver")
        print("\nNote: Using direct IPv6 address bypasses DNS issues.")
    else:
        print("\n" + "=" * 60)
        print("Connection failed. Possible issues:")
        print("=" * 60)
        print("1. Your network doesn't support IPv6")
        print("2. Windows Firewall is blocking IPv6 connections")
        print("3. Router doesn't allow IPv6")
        print("\nTry:")
        print("- Connect to mobile hotspot and test again")
        print("- Check Windows Firewall IPv6 settings")
        print("- Use a different network")
    
    print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    main()