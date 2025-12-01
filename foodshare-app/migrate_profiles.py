#!/usr/bin/env python3
"""
Migration script to update User model with new fields and guest mode support
"""
import sqlite3
import os
from datetime import datetime

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'foodshare.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔄 Starting profile migration...")
    
    try:
        # Add new columns to user table
        print("📝 Adding role column...")
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN role TEXT DEFAULT 'Garden Volunteer'")
            print("✅ Added role column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️  role column already exists")
            else:
                raise
        
        print("📝 Adding is_guest column...")
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN is_guest INTEGER DEFAULT 0")
            print("✅ Added is_guest column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️  is_guest column already exists")
            else:
                raise
        
        print("📝 Adding created_at column...")
        try:
            cursor.execute(f"ALTER TABLE user ADD COLUMN created_at TEXT DEFAULT '{datetime.utcnow().isoformat()}'")
            print("✅ Added created_at column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️  created_at column already exists")
            else:
                raise
        
        print("📝 Adding last_active column...")
        try:
            cursor.execute(f"ALTER TABLE user ADD COLUMN last_active TEXT DEFAULT '{datetime.utcnow().isoformat()}'")
            print("✅ Added last_active column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️  last_active column already exists")
            else:
                raise
        
        # Create a guest user if it doesn't exist
        print("📝 Creating guest user for kiosk mode...")
        cursor.execute("SELECT id FROM user WHERE username = 'guest'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO user (username, email, bio, location, role, is_guest, created_at)
                VALUES ('guest', 'guest@foodshare.local', 'Browse as a guest - kiosk mode', 'Community Garden', 'Guest', 1, ?)
            """, (datetime.utcnow().isoformat(),))
            print("✅ Created guest user")
        else:
            print("ℹ️  Guest user already exists")
        
        conn.commit()
        print("\n✅ Profile migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
