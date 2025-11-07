#!/usr/bin/env python3
"""
Clean up duplicate gardens in the database
Keeps the first instance of each garden and removes duplicates
"""

import sqlite3
import os

db_path = 'database/foodshare.db'

if not os.path.exists(db_path):
    print("Database not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Finding duplicate gardens...")

# Find all gardens with duplicates
cursor.execute("""
    SELECT name, MIN(id) as keep_id, GROUP_CONCAT(id) as all_ids
    FROM garden
    GROUP BY name
    HAVING COUNT(*) > 1
""")

duplicates = cursor.fetchall()

if not duplicates:
    print("No duplicate gardens found!")
    conn.close()
    exit(0)

print(f"\nFound {len(duplicates)} sets of duplicate gardens:")
for name, keep_id, all_ids in duplicates:
    ids = all_ids.split(',')
    delete_ids = [i for i in ids if i != str(keep_id)]
    print(f"  '{name}': Keeping ID {keep_id}, will delete IDs {', '.join(delete_ids)}")

# Delete duplicate gardens
for name, keep_id, all_ids in duplicates:
    ids = all_ids.split(',')
    delete_ids = [i for i in ids if i != str(keep_id)]
    
    for delete_id in delete_ids:
        # Delete associated plots first
        cursor.execute("DELETE FROM garden_plot WHERE garden_id = ?", (delete_id,))
        # Delete the garden
        cursor.execute("DELETE FROM garden WHERE id = ?", (delete_id,))
        print(f"✓ Deleted duplicate garden '{name}' (ID: {delete_id})")

conn.commit()
print(f"\n✅ Cleanup complete! Removed {sum(len(ids.split(','))-1 for _, _, ids in duplicates)} duplicate gardens.")

# Show remaining gardens
cursor.execute("SELECT id, name FROM garden ORDER BY id")
gardens = cursor.fetchall()
print(f"\nRemaining gardens ({len(gardens)}):")
for garden_id, name in gardens:
    print(f"  ID {garden_id}: {name}")

conn.close()