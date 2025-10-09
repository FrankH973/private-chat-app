# reset_db.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'private_chat_app.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
    """)
    
print("All tables dropped successfully!")