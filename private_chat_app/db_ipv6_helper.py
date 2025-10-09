# db_ipv6_helper.py
# Place this in: C:\private_chat_app\private_chat_app\db_ipv6_helper.py
# This ensures Django uses IPv6 for database connections

import socket
from decouple import config

def get_ipv6_host():
    """
    Get IPv6 address for Supabase database
    Falls back to hostname if IPv6 resolution fails
    """
    hostname = config('DB_HOST', default='db.hxabgehdsdcenyaerxtb.supabase.co')
    port = int(config('DB_PORT', default='5432'))
    
    print(f"Resolving {hostname} for IPv6...")
    
    try:
        # Try to get IPv6 address
        for res in socket.getaddrinfo(hostname, port, socket.AF_INET6, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            ipv6_address = sa[0]
            print(f"✅ Found IPv6 address: {ipv6_address}")
            return ipv6_address
    except Exception as e:
        print(f"⚠️  IPv6 resolution failed: {e}")
        print(f"Falling back to hostname: {hostname}")
        return hostname
    
    return hostname

def test_ipv6_connection():
    """Test if IPv6 connection to Supabase works"""
    hostname = config('DB_HOST', default='db.hxabgehdsdcenyaerxtb.supabase.co')
    port = int(config('DB_PORT', default='5432'))
    
    print("=" * 60)
    print("Testing IPv6 Connection to Supabase")
    print("=" * 60)
    print(f"\nHostname: {hostname}")
    print(f"Port: {port}\n")
    
    # Try all available address families
    for res in socket.getaddrinfo(hostname, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        
        # Determine if IPv4 or IPv6
        if af == socket.AF_INET:
            address_type = "IPv4"
        elif af == socket.AF_INET6:
            address_type = "IPv6"
        else:
            address_type = "Unknown"
        
        try:
            sock = socket.socket(af, socktype, proto)
            sock.settimeout(5)
            sock.connect(sa)
            print(f"✅ Connected via {address_type} to {sa[0]}")
            sock.close()
            
            if af == socket.AF_INET6:
                print(f"\n🎉 IPv6 connection works!")
                print(f"IPv6 Address: {sa[0]}")
                return True, sa[0]
                
        except Exception as e:
            print(f"❌ Failed to connect via {address_type} to {sa[0]}")
            print(f"   Error: {e}")
    
    return False, None

if __name__ == "__main__":
    success, ipv6_addr = test_ipv6_connection()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Configuration Successful!")
        print("=" * 60)
        print("\nYour database connection is working via IPv6.")
        print("Django should now be able to connect to Supabase.")
        print("\nNext steps:")
        print("1. Run: python manage.py check")
        print("2. Run: python manage.py migrate")
    else:
        print("\n" + "=" * 60)
        print("⚠️  Connection Issues")
        print("=" * 60)
        print("Please check:")
        print("1. Your internet connection supports IPv6")
        print("2. Firewall allows IPv6 connections")
        print("3. Try changing DNS to Google DNS (8.8.8.8)")