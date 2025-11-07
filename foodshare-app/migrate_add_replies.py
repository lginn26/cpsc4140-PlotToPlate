"""
Database migration script to add Reply table
Run this script to update the database schema with the Reply model
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Reply

def migrate():
    with app.app_context():
        print("Creating Reply table...")
        try:
            # Create the Reply table
            db.create_all()
            print("✅ Reply table created successfully!")
            print("Database migration completed.")
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            return False
    return True

if __name__ == "__main__":
    migrate()
