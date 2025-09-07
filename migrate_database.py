#!/usr/bin/env python3
"""
Database Migration Script
Adds new columns and tables for enhanced admin dashboard
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migrate database to support new features"""
    print("🔧 Starting Database Migration...")
    
    # Database file paths to check
    db_files = [
        'license_plate.db',
        'instance/license_plate.db',
        'license_plate_django/db.sqlite3',
        'license_plate_system/db.sqlite3'
    ]
    
    for db_path in db_files:
        if os.path.exists(db_path):
            print(f"📁 Found database: {db_path}")
            migrate_single_db(db_path)
        else:
            print(f"❌ Database not found: {db_path}")
    
    print("✅ Migration completed!")

def migrate_single_db(db_path):
    """Migrate a single database file"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"🔨 Migrating {db_path}...")
        
        # 1. Add entry_type column to access_log if not exists
        try:
            cursor.execute("ALTER TABLE access_log ADD COLUMN entry_type VARCHAR(10) DEFAULT 'ENTRY'")
            print("  ✅ Added entry_type column to access_log")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("  ℹ️  entry_type column already exists in access_log")
            else:
                print(f"  ⚠️  Error adding entry_type to access_log: {e}")
        
        # 2. Create vehicle_status table if not exists
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plate_number VARCHAR(20) NOT NULL UNIQUE,
                    status VARCHAR(10) NOT NULL,
                    entry_time DATETIME,
                    exit_time DATETIME,
                    duration INTEGER,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    owner_info TEXT
                )
            """)
            print("  ✅ Created vehicle_status table")
        except sqlite3.Error as e:
            print(f"  ⚠️  Error creating vehicle_status table: {e}")
        
        # 3. Create system_stats table if not exists
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE DEFAULT CURRENT_DATE,
                    total_entries INTEGER DEFAULT 0,
                    total_exits INTEGER DEFAULT 0,
                    authorized_entries INTEGER DEFAULT 0,
                    unauthorized_attempts INTEGER DEFAULT 0,
                    vehicles_inside INTEGER DEFAULT 0,
                    peak_occupancy INTEGER DEFAULT 0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("  ✅ Created system_stats table")
        except sqlite3.Error as e:
            print(f"  ⚠️  Error creating system_stats table: {e}")
        
        # 4. Update existing access_log entries to have entry_type
        try:
            cursor.execute("UPDATE access_log SET entry_type = 'ENTRY' WHERE entry_type IS NULL")
            updated_rows = cursor.rowcount
            if updated_rows > 0:
                print(f"  ✅ Updated {updated_rows} existing access_log entries")
            else:
                print("  ℹ️  No existing access_log entries to update")
        except sqlite3.Error as e:
            print(f"  ⚠️  Error updating access_log entries: {e}")
        
        # 5. Create initial system_stats entry for today if not exists
        try:
            today = datetime.now().date()
            cursor.execute("SELECT COUNT(*) FROM system_stats WHERE date = ?", (today,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO system_stats (date, total_entries, total_exits, authorized_entries, 
                                            unauthorized_attempts, vehicles_inside, peak_occupancy)
                    VALUES (?, 0, 0, 0, 0, 0, 0)
                """, (today,))
                print("  ✅ Created initial system_stats entry for today")
            else:
                print("  ℹ️  System stats entry for today already exists")
        except sqlite3.Error as e:
            print(f"  ⚠️  Error creating initial system_stats: {e}")
        
        # 6. Show table info for verification
        try:
            print("\\n  📊 Database Tables:")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print(f"    • {table_name}: {len(columns)} columns")
        except sqlite3.Error as e:
            print(f"  ⚠️  Error showing table info: {e}")
        
        conn.commit()
        conn.close()
        print(f"  ✅ {db_path} migration completed successfully!")
        
    except Exception as e:
        print(f"  ❌ Error migrating {db_path}: {e}")

def verify_migration():
    """Verify that migration was successful"""
    print("\\n🔍 Verifying Migration...")
    
    db_files = [
        'license_plate.db',
        'instance/license_plate.db'
    ]
    
    for db_path in db_files:
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if new columns exist
                cursor.execute("PRAGMA table_info(access_log)")
                access_log_columns = [col[1] for col in cursor.fetchall()]
                has_entry_type = 'entry_type' in access_log_columns
                
                # Check if new tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [table[0] for table in cursor.fetchall()]
                has_vehicle_status = 'vehicle_status' in tables
                has_system_stats = 'system_stats' in tables
                
                print(f"  📁 {db_path}:")
                print(f"    • access_log.entry_type: {'✅' if has_entry_type else '❌'}")
                print(f"    • vehicle_status table: {'✅' if has_vehicle_status else '❌'}")
                print(f"    • system_stats table: {'✅' if has_system_stats else '❌'}")
                
                conn.close()
                
            except Exception as e:
                print(f"  ❌ Error verifying {db_path}: {e}")

if __name__ == "__main__":
    print("🗄️  Database Migration Tool")
    print("=" * 40)
    
    # Check current directory
    print(f"📂 Current directory: {os.getcwd()}")
    print(f"📝 Files in directory: {os.listdir('.')}")
    
    # Run migration
    migrate_database()
    
    # Verify migration
    verify_migration()
    
    print("\\n🚀 Migration completed! You can now start the Flask app.")
    print("   python3 app.py")