# test_django_db.py
# Complete test for Django database connection with IPv6
# Place in: C:\private_chat_app\private_chat_app\test_django_db.py
# Run with: python test_django_db.py

import os
import sys
import socket
import django
from pathlib import Path

# Add project to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'private_chat_app.settings')
django.setup()

from django.db import connection
from django.conf import settings

def test_ipv6_connectivity():
    """Test IPv6 socket connection first"""
    print("=" * 70)
    print("STEP 1: Testing IPv6 Socket Connection")
    print("=" * 70)
    
    db_config = settings.DATABASES['default']
    hostname = db_config['HOST']
    port = int(db_config['PORT'])
    
    print(f"\nTarget: {hostname}:{port}")
    print(f"Testing all available protocols...\n")
    
    ipv6_works = False
    ipv6_address = None
    
    try:
        for res in socket.getaddrinfo(hostname, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            
            address_type = "IPv6" if af == socket.AF_INET6 else "IPv4" if af == socket.AF_INET else "Unknown"
            
            try:
                sock = socket.socket(af, socktype, proto)
                sock.settimeout(5)
                sock.connect(sa)
                print(f"✅ {address_type:5s} connection successful to {sa[0]}")
                sock.close()
                
                if af == socket.AF_INET6:
                    ipv6_works = True
                    ipv6_address = sa[0]
                    
            except Exception as e:
                print(f"❌ {address_type:5s} connection failed to {sa[0]}")
                
    except Exception as e:
        print(f"❌ Could not resolve hostname: {e}")
        return False, None
    
    if ipv6_works:
        print(f"\n✅ IPv6 connectivity confirmed!")
        print(f"   Address: {ipv6_address}")
    else:
        print(f"\n⚠️  IPv6 connection not available")
    
    return ipv6_works, ipv6_address

def test_django_connection():
    """Test Django database connection"""
    print("\n" + "=" * 70)
    print("STEP 2: Testing Django Database Connection")
    print("=" * 70)
    
    db_config = settings.DATABASES['default']
    
    print(f"\nDatabase Configuration:")
    print(f"  Engine: {db_config['ENGINE']}")
    print(f"  Name: {db_config['NAME']}")
    print(f"  User: {db_config['USER']}")
    print(f"  Host: {db_config['HOST']}")
    print(f"  Port: {db_config['PORT']}")
    print(f"  SSL: {db_config['OPTIONS'].get('sslmode', 'default')}")
    
    try:
        print("\n[Attempting Django connection...]")
        
        # Force a connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            print("\n✅ Django database connection SUCCESSFUL!")
            print(f"\nPostgreSQL Version:")
            print(f"  {version[:80]}...")
            
            # Test a simple query
            cursor.execute("SELECT current_database(), current_user;")
            db_name, db_user = cursor.fetchone()
            print(f"\nConnected to:")
            print(f"  Database: {db_name}")
            print(f"  User: {db_user}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Django database connection FAILED!")
        print(f"Error: {str(e)}\n")
        
        print("Troubleshooting steps:")
        print("1. Check if your .env file has correct credentials")
        print("2. Ensure your network supports IPv6")
        print("3. Try changing system DNS to Google DNS (8.8.8.8)")
        print("4. Check Windows Firewall settings")
        
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  Django + Supabase IPv6 Connection Test")
    print("=" * 70)
    
    # Test 1: IPv6 connectivity
    ipv6_ok, ipv6_addr = test_ipv6_connectivity()
    
    # Test 2: Django connection
    django_ok = test_django_connection()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"IPv6 Socket Connection:    {'✅ PASS' if ipv6_ok else '❌ FAIL'}")
    print(f"Django Database Connection: {'✅ PASS' if django_ok else '❌ FAIL'}")
    
    if django_ok:
        print("\n" + "🎉" * 35)
        print("\n  SUCCESS! Your database is properly configured!")
        print("\n" + "🎉" * 35)
        print("\nNext steps:")
        print("  1. Run: python manage.py makemigrations")
        print("  2. Run: python manage.py migrate")
        print("  3. Run: python manage.py createsuperuser")
        print("  4. Run: python manage.py runserver")
    else:
        print("\n" + "⚠️" * 35)
        print("\n  Connection failed. Please check the troubleshooting steps above.")
        print("\n" + "⚠️" * 35)
        
        if ipv6_ok and not django_ok:
            print("\n💡 IPv6 works but Django connection fails.")
            print("   Try using the direct IPv6 address in settings.py:")
            print(f"   DB_HOST = '{ipv6_addr}'")
            print("   Or add to .env:")
            print(f"   DB_IPV6_ADDRESS={ipv6_addr}")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    main()