#!/usr/bin/env python3
"""
Database migration script to add new features:
1. Add plot attributes to GardenPlot (water_available, tools_available, soil_type, sunlight_level, notes)
2. Add status field to Post (active/resolved)
3. Add garden_follower table for garden following functionality
"""

import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(__file__), 'database', 'foodshare.db')

def migrate():
    """Add new columns to existing tables and create new tables"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Starting database migration...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(garden_plot)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add new columns to GardenPlot table if they don't exist
        if 'water_available' not in columns:
            print("Adding water_available column to garden_plot...")
            cursor.execute("ALTER TABLE garden_plot ADD COLUMN water_available BOOLEAN DEFAULT 0")
        
        if 'tools_available' not in columns:
            print("Adding tools_available column to garden_plot...")
            cursor.execute("ALTER TABLE garden_plot ADD COLUMN tools_available BOOLEAN DEFAULT 0")
        
        if 'soil_type' not in columns:
            print("Adding soil_type column to garden_plot...")
            cursor.execute("ALTER TABLE garden_plot ADD COLUMN soil_type VARCHAR(50)")
        
        if 'sunlight_level' not in columns:
            print("Adding sunlight_level column to garden_plot...")
            cursor.execute("ALTER TABLE garden_plot ADD COLUMN sunlight_level VARCHAR(20)")
        
        if 'notes' not in columns:
            print("Adding notes column to garden_plot...")
            cursor.execute("ALTER TABLE garden_plot ADD COLUMN notes TEXT")
        
        # Check Post table
        cursor.execute("PRAGMA table_info(post)")
        post_columns = [col[1] for col in cursor.fetchall()]
        
        # Add status column to Post table if it doesn't exist
        if 'status' not in post_columns:
            print("Adding status column to post...")
            cursor.execute("ALTER TABLE post ADD COLUMN status VARCHAR(20) DEFAULT 'active'")
            # Update existing posts to have 'active' status
            cursor.execute("UPDATE post SET status = 'active' WHERE status IS NULL")
        
        # Check if garden_follower table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='garden_follower'")
        if not cursor.fetchone():
            print("Creating garden_follower table...")
            cursor.execute("""
                CREATE TABLE garden_follower (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    garden_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    followed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (garden_id) REFERENCES garden (id),
                    FOREIGN KEY (user_id) REFERENCES user (id),
                    UNIQUE(garden_id, user_id)
                )
            """)
        
        # Drop old join_request table if it exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='join_request'")
        if cursor.fetchone():
            print("Dropping old join_request table...")
            cursor.execute("DROP TABLE join_request")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Verify the changes
        print("\nVerifying changes...")
        cursor.execute("PRAGMA table_info(garden_plot)")
        garden_columns = [col[1] for col in cursor.fetchall()]
        print(f"GardenPlot columns: {', '.join(garden_columns)}")
        
        cursor.execute("PRAGMA table_info(post)")
        post_columns = [col[1] for col in cursor.fetchall()]
        print(f"Post columns: {', '.join(post_columns)}")
        
        cursor.execute("PRAGMA table_info(garden_follower)")
        follower_columns = [col[1] for col in cursor.fetchall()]
        print(f"GardenFollower columns: {', '.join(follower_columns)}")
        
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
